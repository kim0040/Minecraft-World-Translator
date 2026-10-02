//! In-app updates through the official updater: the release publishes `latest.json` next to signed
//! bundles, and the app verifies each download with the public key in `plugins.updater.pubkey`.
//!
//! Without a public key the app can still tell the person that a newer version exists, but it never
//! installs an unverified download; it offers the release page instead. An update never starts while
//! a scan, translation or restore owns the core, and holds the same gate while it downloads, so a job
//! cannot start halfway through an install.
use serde::Serialize;
use tauri::{AppHandle, Emitter, Manager, Runtime};
use tauri_plugin_updater::UpdaterExt;

pub const RELEASES_URL: &str = "https://github.com/kim0040/PomiTranslate/releases/latest";

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct UpdateInfo {
    /// "available" or "current".
    pub status: &'static str,
    pub current_version: String,
    pub version: Option<String>,
    pub notes: Option<String>,
    pub date: Option<String>,
    /// True only when this build carries a signing key, so the download can be verified.
    pub can_install: bool,
    pub release_url: &'static str,
}

/// A build is able to verify updates only when its configuration carries the public key.
pub fn verification_key<R: Runtime>(app: &AppHandle<R>) -> Option<String> {
    app.config()
        .plugins
        .0
        .get("updater")
        .and_then(|updater| updater.get("pubkey"))
        .and_then(|key| key.as_str())
        .map(str::trim)
        .filter(|key| !key.is_empty())
        .map(str::to_owned)
}

fn message(error: tauri_plugin_updater::Error) -> String {
    // Network and manifest errors read the same to the person: the release could not be reached.
    let text = error.to_string();
    if text.contains("404") || text.contains("release JSON") || text.contains("ReleaseNotFound") {
        "UPDATE_NOT_PUBLISHED".into()
    } else {
        "UPDATE_UNREACHABLE".into()
    }
}

pub async fn check<R: Runtime>(app: &AppHandle<R>) -> Result<UpdateInfo, String> {
    let current = app.package_info().version.to_string();
    let updater = app.updater().map_err(message)?;
    let found = updater.check().await.map_err(message)?;
    let can_install = verification_key(app).is_some();
    Ok(match found {
        Some(update) => UpdateInfo {
            status: "available",
            current_version: current,
            version: Some(update.version.clone()),
            notes: update.body.clone().map(|body| body.chars().take(4000).collect()),
            date: update.date.map(|date| date.to_string()),
            can_install,
            release_url: RELEASES_URL,
        },
        None => UpdateInfo {
            status: "current",
            current_version: current,
            version: None,
            notes: None,
            date: None,
            can_install,
            release_url: RELEASES_URL,
        },
    })
}

#[derive(Clone, Serialize)]
pub struct Progress {
    pub downloaded: u64,
    pub total: Option<u64>,
}

/// Download, verify and install, then restart into the new version.
pub async fn install<R: Runtime>(app: &AppHandle<R>) -> Result<(), String> {
    if verification_key(app).is_none() {
        return Err("UPDATE_UNSIGNED_BUILD".into());
    }
    let updater = app.updater().map_err(message)?;
    let Some(update) = updater.check().await.map_err(message)? else {
        return Err("UPDATE_NONE".into());
    };
    let window = app.get_webview_window("main");
    let mut downloaded = 0u64;
    update
        .download_and_install(
            |chunk, total| {
                downloaded += chunk as u64;
                if let Some(window) = &window {
                    let _ = window.emit("pomi-update-progress", Progress { downloaded, total });
                }
            },
            || {},
        )
        .await
        .map_err(|error| {
            if error.to_string().to_lowercase().contains("signature") {
                "UPDATE_SIGNATURE_INVALID".to_string()
            } else {
                "UPDATE_INSTALL_FAILED".to_string()
            }
        })?;
    app.restart();
}
