use serde_json::{Map, Value};

pub fn canonical(provider: &str) -> Option<(&'static str, &'static str)> {
    match provider {
        "openai" => Some(("https://api.openai.com/v1", "openai")),
        "openrouter" => Some(("https://openrouter.ai/api/v1", "openai")),
        "comet" => Some(("https://api.cometapi.com/v1", "openai")),
        "gemini" => Some(("https://generativelanguage.googleapis.com/v1beta", "gemini")),
        "anthropic" => Some(("https://api.anthropic.com/v1", "anthropic")),
        _ => None,
    }
}

/// Called before reading credentials. Never route a public-provider key to a custom origin.
pub fn validate(payload: &mut Map<String, Value>) -> Result<(), String> {
    let provider = payload
        .get("provider")
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string();
    crate::credentials::validate_provider(&provider)?;
    if let Some((url, wire)) = canonical(&provider) {
        let supplied = payload.get("baseUrl").and_then(Value::as_str).unwrap_or("");
        if !supplied.is_empty() && supplied.trim_end_matches('/') != url {
            return Err("Public provider endpoint does not match the selected provider; use Custom for a custom URL".into());
        }
        payload.insert("baseUrl".into(), Value::String(url.into()));
        payload.insert("wireFormat".into(), Value::String(wire.into()));
    } else {
        let base = payload
            .get("baseUrl")
            .and_then(Value::as_str)
            .ok_or("Custom provider requires an explicit endpoint")?;
        let url = tauri::Url::parse(base).map_err(|_| "Custom endpoint is invalid")?;
        if !matches!(url.scheme(), "http" | "https")
            || url.host_str().is_none()
            || !url.username().is_empty()
            || url.password().is_some()
            || url.query().is_some()
            || url.fragment().is_some()
        {
            return Err(
                "Custom endpoint must be an HTTP(S) URL without credentials, query or fragment"
                    .into(),
            );
        }
        let wire = payload
            .get("wireFormat")
            .and_then(Value::as_str)
            .unwrap_or("openai");
        if !matches!(wire, "openai" | "anthropic") {
            return Err("Unsupported Custom wire format".into());
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn public_endpoints_are_pinned_and_mismatches_rejected() {
        for provider in ["openai", "openrouter", "gemini", "anthropic", "comet"] {
            let mut payload = serde_json::json!({"provider":provider})
                .as_object()
                .unwrap()
                .clone();
            validate(&mut payload).unwrap();
            assert_eq!(payload["baseUrl"], canonical(provider).unwrap().0);
            payload.insert(
                "baseUrl".into(),
                Value::String("http://127.0.0.1:52831".into()),
            );
            assert!(validate(&mut payload).is_err());
        }
    }
    #[test]
    fn custom_requires_explicit_valid_endpoint() {
        for url in [
            "",
            "file:///tmp/a",
            "https://user:secret@example.com",
            "https://example.com?token=secret",
        ] {
            let mut payload = serde_json::json!({"provider":"custom","baseUrl":url})
                .as_object()
                .unwrap()
                .clone();
            assert!(validate(&mut payload).is_err());
        }
        let mut payload = serde_json::json!({"provider":"custom","baseUrl":"http://127.0.0.1:8080/v1","wireFormat":"openai"}).as_object().unwrap().clone();
        validate(&mut payload).unwrap();
    }
}
