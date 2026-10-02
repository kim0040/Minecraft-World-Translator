//! App commands in the native menu bar, so the standard shortcuts work the way they do elsewhere:
//! Open World (Cmd/Ctrl+O), Settings (Cmd+, on macOS), Find (Cmd/Ctrl+F), and a Help menu with the
//! guide, the getting-started tour, shortcuts, licenses and problem reports. "Check for Updates…"
//! sits in the application menu on macOS and in Help elsewhere. A choice is forwarded to the window
//! as `pomi-menu`; the page decides whether it applies to the current screen.
use serde::Deserialize;
use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem, Submenu},
    AppHandle, Emitter, Manager, State, Wry,
};

pub const OPEN_WORLD: &str = "pomi-open-world";
pub const SETTINGS: &str = "pomi-settings";
pub const FIND: &str = "pomi-find";
pub const HELP: &str = "pomi-help";
pub const TOUR: &str = "pomi-tour";
pub const SHORTCUTS: &str = "pomi-shortcuts";
pub const LICENSES: &str = "pomi-licenses";
pub const REPORT: &str = "pomi-report";
pub const UPDATES: &str = "pomi-updates";

pub struct AppMenu {
    open_world: MenuItem<Wry>,
    settings: MenuItem<Wry>,
    find: MenuItem<Wry>,
    help: MenuItem<Wry>,
    tour: MenuItem<Wry>,
    shortcuts: MenuItem<Wry>,
    licenses: MenuItem<Wry>,
    report: MenuItem<Wry>,
    updates: MenuItem<Wry>,
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
    let help = MenuItem::with_id(handle, HELP, "PomiTranslate Help", true, Some(if cfg!(target_os = "macos") { "CmdOrCtrl+?" } else { "F1" }))?;
    let tour = MenuItem::with_id(handle, TOUR, "Getting Started", true, None::<&str>)?;
    let shortcuts = MenuItem::with_id(handle, SHORTCUTS, "Keyboard Shortcuts", true, None::<&str>)?;
    let licenses = MenuItem::with_id(handle, LICENSES, "Open-Source Licenses", true, None::<&str>)?;
    let report = MenuItem::with_id(handle, REPORT, "Report a Problem…", true, None::<&str>)?;
    let updates = MenuItem::with_id(handle, UPDATES, "Check for Updates…", true, None::<&str>)?;

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
    #[cfg_attr(not(target_os = "macos"), allow(unused_mut))]
    let mut updates_placed = false;
    #[cfg(target_os = "macos")]
    {
        let first = menu.items()?.into_iter().find_map(|item| item.as_submenu().cloned());
        match first {
            Some(app_menu) => {
                app_menu.insert(&updates, 1)?;
                app_menu.insert(&PredefinedMenuItem::separator(handle)?, 2)?;
                app_menu.insert(&settings, 3)?;
                app_menu.insert(&PredefinedMenuItem::separator(handle)?, 4)?;
                updates_placed = true;
            }
            None => file.insert(&settings, 2)?,
        }
    }
    #[cfg(not(target_os = "macos"))]
    file.insert(&settings, 2)?;

    let help_menu = match submenu(menu, &["Help"]) {
        Some(existing) => existing,
        None => {
            let created = Submenu::new(handle, "Help", true)?;
            menu.append(&created)?;
            created
        }
    };
    help_menu.append(&help)?;
    help_menu.append(&tour)?;
    help_menu.append(&shortcuts)?;
    help_menu.append(&PredefinedMenuItem::separator(handle)?)?;
    if !updates_placed {
        help_menu.append(&updates)?;
    }
    help_menu.append(&licenses)?;
    help_menu.append(&report)?;
    #[cfg(target_os = "macos")]
    let _ = help_menu.set_as_help_menu_for_nsapp();

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

    app.manage(AppMenu { open_world, settings, find, help, tour, shortcuts, licenses, report, updates });
    Ok(())
}

/// Forward an app command; returns false for ids this module does not own.
pub fn select(app: &AppHandle, id: &str) -> bool {
    let action = match id {
        OPEN_WORLD => "open-world",
        SETTINGS => "settings",
        FIND => "find",
        HELP => "help",
        TOUR => "tour",
        SHORTCUTS => "shortcuts",
        LICENSES => "licenses",
        REPORT => "report",
        UPDATES => "updates",
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
    #[serde(default)]
    help: String,
    #[serde(default)]
    tour: String,
    #[serde(default)]
    shortcuts: String,
    #[serde(default)]
    licenses: String,
    #[serde(default)]
    report: String,
    #[serde(default)]
    updates: String,
}

/// The page sends its own wording so the menu speaks the selected interface language.
#[tauri::command]
pub fn set_menu_labels(menu: State<'_, AppMenu>, labels: MenuLabels) -> Result<(), String> {
    let clean = |text: &str| text.chars().filter(|c| !c.is_control()).take(60).collect::<String>();
    for (item, text) in [
        (&menu.open_world, &labels.open_world),
        (&menu.settings, &labels.settings),
        (&menu.find, &labels.find),
        (&menu.help, &labels.help),
        (&menu.tour, &labels.tour),
        (&menu.shortcuts, &labels.shortcuts),
        (&menu.licenses, &labels.licenses),
        (&menu.report, &labels.report),
        (&menu.updates, &labels.updates),
    ] {
        let text = clean(text);
        if !text.trim().is_empty() {
            item.set_text(text).map_err(|_| "Menu label could not be updated")?;
        }
    }
    Ok(())
}
