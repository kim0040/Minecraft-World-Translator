//! App commands in the native menu bar, so the standard shortcuts work the way they do elsewhere:
//! Open World (Cmd/Ctrl+O), Settings (Cmd+, on macOS), Find (Cmd/Ctrl+F). A choice is forwarded
//! to the window as `pomi-menu`; the page decides whether it applies to the current screen.
use serde::Deserialize;
use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem, Submenu},
    AppHandle, Emitter, Manager, State, Wry,
};

pub const OPEN_WORLD: &str = "pomi-open-world";
pub const SETTINGS: &str = "pomi-settings";
pub const FIND: &str = "pomi-find";

pub struct AppMenu {
    open_world: MenuItem<Wry>,
    settings: MenuItem<Wry>,
    find: MenuItem<Wry>,
}

fn submenu(menu: &Menu<Wry>, names: &[&str]) -> Option<Submenu<Wry>> {
    menu.items()
        .ok()?
        .into_iter()
        .filter_map(|item| item.as_submenu().cloned())
        .find(|item| item.text().is_ok_and(|text| names.contains(&text.as_str())))
}

pub fn extend(app: &tauri::App, menu: &Menu<Wry>) -> tauri::Result<()> {
    let handle = app.handle();
    let open_world = MenuItem::with_id(handle, OPEN_WORLD, "Open World…", true, Some("CmdOrCtrl+O"))?;
    let settings = MenuItem::with_id(handle, SETTINGS, "Settings…", true, Some("CmdOrCtrl+,"))?;
    let find = MenuItem::with_id(handle, FIND, "Find…", true, Some("CmdOrCtrl+F"))?;

    let file = match submenu(menu, &["File"]) {
        Some(file) => file,
        None => {
            let file = Submenu::new(handle, "File", true)?;
            menu.insert(&file, if cfg!(target_os = "macos") { 1 } else { 0 })?;
            file
        }
    };
    file.insert(&open_world, 0)?;
    file.insert(&PredefinedMenuItem::separator(handle)?, 1)?;

    // macOS keeps Settings in the application menu, right after About.
    #[cfg(target_os = "macos")]
    {
        let first = menu.items()?.into_iter().find_map(|item| item.as_submenu().cloned());
        match first {
            Some(app_menu) => {
                app_menu.insert(&settings, 1)?;
                app_menu.insert(&PredefinedMenuItem::separator(handle)?, 2)?;
            }
            None => file.insert(&settings, 2)?,
        }
    }
    #[cfg(not(target_os = "macos"))]
    file.insert(&settings, 2)?;

    match submenu(menu, &["Edit"]) {
        Some(edit) => {
            edit.append(&PredefinedMenuItem::separator(handle)?)?;
            edit.append(&find)?;
        }
        None => {
            let edit = Submenu::with_items(
                handle,
                "Edit",
                true,
                &[
                    &PredefinedMenuItem::cut(handle, None)?,
                    &PredefinedMenuItem::copy(handle, None)?,
                    &PredefinedMenuItem::paste(handle, None)?,
                    &PredefinedMenuItem::select_all(handle, None)?,
                    &PredefinedMenuItem::separator(handle)?,
                    &find,
                ],
            )?;
            menu.append(&edit)?;
        }
    }

    app.manage(AppMenu { open_world, settings, find });
    Ok(())
}

/// Forward an app command; returns false for ids this module does not own.
pub fn select(app: &AppHandle, id: &str) -> bool {
    let action = match id {
        OPEN_WORLD => "open-world",
        SETTINGS => "settings",
        FIND => "find",
        _ => return false,
    };
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.emit("pomi-menu", action);
    }
    true
}

#[derive(Deserialize)]
pub struct MenuLabels {
    #[serde(rename = "openWorld")]
    open_world: String,
    settings: String,
    find: String,
}

/// The page sends its own wording so the menu speaks the selected interface language.
#[tauri::command]
pub fn set_menu_labels(menu: State<'_, AppMenu>, labels: MenuLabels) -> Result<(), String> {
    let clean = |text: &str| text.chars().filter(|c| !c.is_control()).take(60).collect::<String>();
    for (item, text) in [
        (&menu.open_world, &labels.open_world),
        (&menu.settings, &labels.settings),
        (&menu.find, &labels.find),
    ] {
        let text = clean(text);
        if !text.trim().is_empty() {
            item.set_text(text).map_err(|_| "Menu label could not be updated")?;
        }
    }
    Ok(())
}
