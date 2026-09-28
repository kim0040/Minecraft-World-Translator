"""API keys go through the keyring module. Settings files, SQLite, and logs stay empty of secrets."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SERVICE_NAME = "PomiTranslate"


def remember_api_key(account: str, secret: str) -> None:
    import keyring

    keyring.set_password(SERVICE_NAME, account, secret)


def load_api_key(account: str) -> str | None:
    import keyring

    return keyring.get_password(SERVICE_NAME, account)


def save_public_settings(database: Path, *, provider: str, model: str) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        connection.execute("CREATE TABLE IF NOT EXISTS settings (provider TEXT NOT NULL, model TEXT NOT NULL)")
        connection.execute("DELETE FROM settings")
        connection.execute("INSERT INTO settings (provider, model) VALUES (?, ?)", (provider, model))
        connection.commit()
    finally:
        connection.close()


def redact_log(message: str, secret: str) -> str:
    if not secret:
        return message
    return message.replace(secret, "[redacted]")
