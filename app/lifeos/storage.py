"""Small local-first SQLite storage layer."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from platformdirs import user_data_path


def database_path() -> Path:
    path = Path(user_data_path("LIFE OS", "AKKI-9605"))
    path.mkdir(parents=True, exist_ok=True)
    return path / "lifeos.db"


def connect(path: Path | None = None) -> sqlite3.Connection:
    db = sqlite3.connect(path or database_path())
    db.row_factory = sqlite3.Row
    db.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    return db


def list_notes(db: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(db.execute("SELECT * FROM notes ORDER BY updated_at DESC, id DESC"))


def save_note(db: sqlite3.Connection, title: str, body: str, note_id: int | None = None) -> int:
    clean_title = title.strip() or "Untitled note"
    if note_id is None:
        cursor = db.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (clean_title, body))
        db.commit()
        return int(cursor.lastrowid)
    db.execute(
        "UPDATE notes SET title = ?, body = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (clean_title, body, note_id),
    )
    db.commit()
    return note_id


def delete_note(db: sqlite3.Connection, note_id: int) -> None:
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
