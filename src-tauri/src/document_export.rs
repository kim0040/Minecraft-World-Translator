use serde::Deserialize;
use serde_json::Value;
use std::io::Write;
use tauri_plugin_dialog::DialogExt;

#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DocumentKind {
    Settings,
    ScanReport,
    TranslationReport,
}

impl DocumentKind {
    fn filename(&self) -> &'static str {
        match self {
            Self::Settings => "pomi-settings.json",
            Self::ScanReport => "scan-report.json",
            Self::TranslationReport => "translate-report.json",
        }
    }
}

/// The destination comes from a native dialog, never from renderer path input.
#[tauri::command]
pub async fn export_document(
    app: tauri::AppHandle,
    state: tauri::State<'_, super::ActiveSidecar>,
    kind: DocumentKind,
    document: Option<Value>,
) -> Result<bool, String> {
    let _gate = state
        .request_gate
        .try_lock()
        .map_err(|_| "Another operation is running")?;
    let filename = kind.filename();
    let bytes = match kind {
        DocumentKind::Settings => {
            let value = document.ok_or("Missing public settings")?;
            serde_json::to_vec_pretty(&value).map_err(|_| "Invalid public settings")?
        }
        _ => {
            let path = super::credential_root(&app)?.join("reports").join(filename);
            let bytes = std::fs::read(path).map_err(|_| "The latest report is unavailable")?;
            serde_json::from_slice::<Value>(&bytes).map_err(|_| "The report is not valid JSON")?;
            bytes
        }
    };
    tauri::async_runtime::spawn_blocking(move || {
        let Some(destination) = app
            .dialog()
            .file()
            .add_filter("JSON", &["json"])
            .set_file_name(filename)
            .blocking_save_file()
        else {
            return Ok(false);
        };
        let destination = destination
            .into_path()
            .map_err(|_| "Invalid export destination")?;
        if destination.extension().and_then(|ext| ext.to_str()) != Some("json") {
            return Err("Choose a JSON file for the export".into());
        }
        if std::fs::symlink_metadata(&destination).is_ok_and(|meta| meta.file_type().is_symlink()) {
            return Err("Cannot export through a symbolic link".into());
        }
        let parent = destination.parent().ok_or("Invalid export destination")?;
        let mut temporary =
            tempfile::NamedTempFile::new_in(parent).map_err(|_| "Cannot create export file")?;
        temporary
            .write_all(&bytes)
            .map_err(|_| "Cannot write export file")?;
        temporary
            .as_file()
            .sync_all()
            .map_err(|_| "Cannot finish export file")?;
        temporary
            .persist(destination)
            .map_err(|_| "Cannot save export file")?;
        Ok(true)
    })
    .await
    .map_err(|_| "Export could not finish")?
}
