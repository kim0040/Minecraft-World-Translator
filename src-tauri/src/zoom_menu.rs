//! Real WebView zoom; percentages work with every supported UI language.
use std::sync::atomic::{AtomicU16, Ordering};
use tauri::{
    menu::{CheckMenuItem, Menu, PredefinedMenuItem, Submenu},
    App, AppHandle, Emitter, Manager, Wry,
};

const LEVELS: [u16; 6] = [75, 100, 125, 150, 175, 200];
struct ZoomMenu {
    items: Vec<(u16, CheckMenuItem<Wry>)>,
    current: AtomicU16,
}

pub fn install(app: &mut App) -> tauri::Result<()> {
    let menu = Menu::default(app.handle())?;
    let view = menu
        .items()?
        .into_iter()
        .filter_map(|item| item.as_submenu().cloned())
        .find(|item| item.text().is_ok_and(|text| text == "View"));
    let view = match view {
        Some(view) => view,
        None => {
            let view = Submenu::new(app, "View", true)?;
            menu.append(&view)?;
            view
        }
    };
    view.append(&PredefinedMenuItem::separator(app)?)?;
    let mut items = Vec::new();
    for level in LEVELS {
        let shortcut = match level {
            100 => Some("CmdOrCtrl+0"),
            200 => Some("CmdOrCtrl+2"),
            _ => None,
        };
        let item = CheckMenuItem::with_id(
            app,
            format!("pomi-zoom-{level}"),
            format!("{level}%"),
            true,
            level == 100,
            shortcut,
        )?;
        view.append(&item)?;
        items.push((level, item));
    }
    app.manage(ZoomMenu {
        items,
        current: AtomicU16::new(100),
    });
    app.set_menu(menu)?;
    Ok(())
}

pub fn select(app: &AppHandle, id: &str) {
    let menu = app.state::<ZoomMenu>();
    let Some((level, _)) = menu.items.iter().find(|(_, item)| item.id().as_ref() == id) else {
        return;
    };
    let Some(window) = app.get_webview_window("main") else {
        return;
    };
    if window.set_zoom(f64::from(*level) / 100.0).is_err() {
        for (value, item) in &menu.items {
            let _ = item.set_checked(*value == menu.current.load(Ordering::Relaxed));
        }
        let _ = window.emit("pomi-zoom-failed", ());
        return;
    }
    menu.current.store(*level, Ordering::Relaxed);
    for (value, item) in &menu.items {
        let _ = item.set_checked(value == level);
    }
}
