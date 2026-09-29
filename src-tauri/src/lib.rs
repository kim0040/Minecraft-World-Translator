use std::{fs, path::PathBuf, sync::Mutex};

use serde_json::Value;
use tauri::{Emitter, Manager, State, WindowEvent};
use tauri_plugin_shell::{process::{CommandChild, CommandEvent}, ShellExt};

struct ActiveProcess {
    child: CommandChild,
    cancel_path: PathBuf,
}

#[derive(Default)]
struct ActiveSidecar(Mutex<Option<ActiveProcess>>);

const ALLOWED_REQUESTS: &[&str] = &[
    "notices.get",
    "settings.get",
    "settings.set",
    "credentials.delete",
    "worlds.list",
    "worlds.remember",
    "worlds.forget",
    "world.inspect",
    "resume.status",
    "models.list",
    "scan.start",
    "candidates.page",
    "translate.start",
    "translate.resume",
    "backups.list",
    "restore.start",
];

const KEYRING_SERVICE: &str = "PomiTranslate";

fn keyring_entry(provider: &str) -> Result<keyring::Entry, String> {
    keyring::Entry::new(KEYRING_SERVICE, provider).map_err(|_| "OS credential store is unavailable".into())
}

fn read_key(provider: &str) -> Result<Option<String>, String> {
    match keyring_entry(provider)?.get_password() {
        Ok(secret) => Ok(Some(secret)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(_) => Err("Could not read the API key from the OS credential store".into()),
    }
}

fn delete_key(provider: &str) -> Result<(), String> {
    match keyring_entry(provider)?.delete_credential() {
        Ok(()) | Err(keyring::Error::NoEntry) => Ok(()),
        Err(_) => Err("Could not delete the API key from the OS credential store".into()),
    }
}

#[tauri::command]
async fn sidecar_request(
    app: tauri::AppHandle,
    state: State<'_, ActiveSidecar>,
    mut request: Value,
) -> Result<Value, String> {
    let kind = request
        .get("type")
        .and_then(Value::as_str)
        .ok_or("Missing request type")?
        .to_string();
    if !ALLOWED_REQUESTS.contains(&kind.as_str()) {
        return Err("Unsupported request type".into());
    }
    let id = request
        .get("id")
        .and_then(Value::as_str)
        .ok_or("Missing request id")?
        .to_string();
    if request.get("v").and_then(Value::as_u64) != Some(1) {
        return Err("Unsupported protocol version".into());
    }

    let provider = request
        .get("payload")
        .and_then(|payload| payload.get("provider"))
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string();
    if kind == "credentials.delete" {
        if provider.is_empty() {
            return Err("Missing credential provider".into());
        }
        delete_key(&provider)?;
        return Ok(serde_json::json!({
            "v": 1,
            "id": id,
            "type": "response.ok",
            "payload": {"provider": provider, "deleted": true, "apiKeyStored": false}
        }));
    }
    if matches!(kind.as_str(), "settings.get" | "settings.set" | "models.list" | "translate.start" | "translate.resume") {
        if let Some(payload) = request.get_mut("payload").and_then(Value::as_object_mut) {
            payload.insert("credentialOwner".into(), Value::String("rust".into()));
        }
    }
    if kind == "settings.set" {
        let supplied_key = request
            .get("payload")
            .and_then(|payload| payload.get("apiKey"))
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string();
        if !supplied_key.is_empty() {
            keyring_entry(&provider)?
                .set_password(&supplied_key)
                .map_err(|_| "Could not save the API key in the OS credential store")?;
        }
        if let Some(payload) = request.get_mut("payload").and_then(Value::as_object_mut) {
            payload.remove("apiKey");
        }
    } else if matches!(kind.as_str(), "models.list" | "translate.start" | "translate.resume") && !provider.is_empty() {
        if let Some(secret) = read_key(&provider)? {
            if let Some(payload) = request.get_mut("payload").and_then(Value::as_object_mut) {
                payload.insert("apiKey".into(), Value::String(secret));
            }
        }
    }

    let report_dir = app
        .path()
        .app_data_dir()
        .map_err(|_| "Application data directory is unavailable")?
        .join("reports");
    fs::create_dir_all(&report_dir).map_err(|_| "Cannot create the report directory")?;
    let cancel_path = report_dir.join("active-operation.cancel");
    let _ = fs::remove_file(&cancel_path);

    let mut receiver = {
        let mut active = state.0.lock().map_err(|_| "Sidecar state is unavailable")?;
        if active.is_some() {
            return Err("Another PomiTranslate operation is still running".into());
        }
        let command = app
            .shell()
            .sidecar("pomi-sidecar")
            .map_err(|_| "Packaged translation core is unavailable")?
            .args([
                "--jsonl".to_string(),
                "--report-dir".to_string(),
                report_dir.to_string_lossy().into_owned(),
                "--cancel-file".to_string(),
                cancel_path.to_string_lossy().into_owned(),
            ]);
        let (receiver, mut child) = command
            .spawn()
            .map_err(|_| "Could not start the translation core")?;
        let mut line = serde_json::to_vec(&request).map_err(|_| "Invalid request")?;
        line.push(b'\n');
        child.write(&line).map_err(|_| "Could not send the request to the translation core")?;
        *active = Some(ActiveProcess {
            child,
            cancel_path: cancel_path.clone(),
        });
        receiver
    };

    let mut saw_hello = false;
    let mut stdout_buffer = Vec::<u8>::new();
    let result: Result<Value, String> = 'events: loop {
        match receiver.recv().await {
            Some(CommandEvent::Stdout(bytes)) => {
                stdout_buffer.extend_from_slice(&bytes);
                if stdout_buffer.len() > 8 * 1024 * 1024 {
                    break Err("Translation core returned an oversized message".into());
                }
                while let Some(newline) = stdout_buffer.iter().position(|byte| *byte == b'\n') {
                    let mut line: Vec<u8> = stdout_buffer.drain(..=newline).collect();
                    while line.last().is_some_and(|byte| byte.is_ascii_whitespace()) {
                        line.pop();
                    }
                    if line.is_empty() {
                        continue;
                    }
                    let Ok(message) = serde_json::from_slice::<Value>(&line) else {
                        break 'events Err("Translation core returned an invalid JSONL message".into());
                    };
                    if message.get("type").and_then(Value::as_str) == Some("system.hello") {
                        let version = message
                            .get("payload")
                            .and_then(|value| value.get("protocolVersion"))
                            .and_then(Value::as_u64);
                        if version != Some(1) {
                            break 'events Err("Translation core protocol version does not match".into());
                        }
                        saw_hello = true;
                        continue;
                    }
                    if !saw_hello {
                        break 'events Err("Translation core did not complete its handshake".into());
                    }
                    if message.get("id").and_then(Value::as_str) == Some(id.as_str())
                        && message.get("type").and_then(Value::as_str).is_some_and(|kind| kind.ends_with(".progress"))
                    {
                        let _ = app.emit("pomi-progress", &message);
                        continue;
                    }
                    if message.get("id").and_then(Value::as_str) == Some(id.as_str()) {
                        break 'events Ok(message);
                    }
                }
            }
            Some(CommandEvent::Stderr(_)) => {
                // The sidecar may include private world paths and provider errors.
            }
            Some(CommandEvent::Error(_)) | Some(CommandEvent::Terminated(_)) | None => {
                break Err("Translation core stopped before it returned a result".into());
            }
            Some(_) => continue,
        }
    };

    if let Ok(mut active) = state.0.lock() {
        if let Some(process) = active.take() {
            let _ = process.child.kill();
            let _ = fs::remove_file(process.cancel_path);
        }
    }
    let mut response = result?;
    if matches!(kind.as_str(), "settings.get" | "settings.set") {
        let response_provider = if provider.is_empty() {
            response
                .get("payload")
                .and_then(|payload| payload.get("settings"))
                .and_then(|settings| settings.get("provider"))
                .and_then(Value::as_str)
                .unwrap_or("")
        } else {
            provider.as_str()
        };
        let stored = !response_provider.is_empty() && read_key(response_provider)?.is_some();
        if let Some(payload) = response.get_mut("payload").and_then(Value::as_object_mut) {
            payload.insert("apiKeyStored".into(), Value::Bool(stored));
        }
    }
    Ok(response)
}

#[tauri::command]
fn cancel_active(state: State<'_, ActiveSidecar>) -> Result<bool, String> {
    let active = state.0.lock().map_err(|_| "Sidecar state is unavailable")?;
    let Some(process) = active.as_ref() else {
        return Ok(false);
    };
    fs::write(&process.cancel_path, b"cancel").map_err(|_| "Could not request cancellation")?;
    Ok(true)
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, _, _| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.set_focus();
            }
        }))
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .manage(ActiveSidecar::default())
        .invoke_handler(tauri::generate_handler![sidecar_request, cancel_active])
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                let active = window.state::<ActiveSidecar>();
                if active.0.lock().map(|child| child.is_some()).unwrap_or(false) {
                    api.prevent_close();
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("failed to run PomiTranslate");
}
