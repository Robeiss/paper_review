from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .data import INITIAL_RULE_CHANGES, INITIAL_RULES, INITIAL_VERSIONS

DB_PATH = Path(__file__).resolve().parents[1] / "paper_review.db"
PASSWORD_SALT = "paper-review-v3"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_password(password: str) -> str:
    return hashlib.sha256(f"{PASSWORD_SALT}:{password}".encode("utf-8")).hexdigest()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def encode(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def decode(value: str) -> Any:
    return json.loads(value)


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              account TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL,
              role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
              password_hash TEXT NOT NULL,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS versions (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              published_at TEXT NOT NULL,
              source TEXT NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('draft', 'published', 'archived')),
              changes_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rules (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              summary TEXT NOT NULL,
              specs_json TEXT NOT NULL,
              notes_json TEXT NOT NULL,
              mistakes_json TEXT NOT NULL,
              severity TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rule_changes (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              version_id TEXT NOT NULL,
              rule_id TEXT NOT NULL,
              title TEXT NOT NULL,
              previous TEXT NOT NULL,
              current TEXT NOT NULL,
              impact TEXT NOT NULL,
              risk TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              actor TEXT NOT NULL,
              action TEXT NOT NULL,
              target TEXT NOT NULL,
              detail TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        seed_users(conn)
        seed_versions(conn)
        seed_rules(conn)
        seed_rule_changes(conn)


def seed_users(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return

    users = [
        ("20260001", "示例学生", "student", "student123"),
        ("admin", "教学秘书", "admin", "admin123"),
    ]
    conn.executemany(
        "INSERT INTO users (account, name, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        [(account, name, role, hash_password(password), now_iso()) for account, name, role, password in users],
    )


def seed_versions(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) FROM versions").fetchone()[0]:
        return

    conn.executemany(
        """
        INSERT INTO versions (id, name, published_at, source, status, changes_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                version["id"],
                version["name"],
                version["publishedAt"],
                version["source"],
                version["status"],
                encode(version["changes"]),
            )
            for version in INITIAL_VERSIONS
        ],
    )


def seed_rules(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]:
        return

    conn.executemany(
        """
        INSERT INTO rules (id, name, summary, specs_json, notes_json, mistakes_json, severity, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                rule["id"],
                rule["name"],
                rule["summary"],
                encode(rule["specs"]),
                encode(rule["notes"]),
                encode(rule["commonMistakes"]),
                rule["severity"],
                rule["updatedAt"],
            )
            for rule in INITIAL_RULES
        ],
    )


def seed_rule_changes(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) FROM rule_changes").fetchone()[0]:
        return

    conn.executemany(
        """
        INSERT INTO rule_changes (version_id, rule_id, title, previous, current, impact, risk)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "2026-undergraduate-v1",
                change["ruleId"],
                change["title"],
                change["previous"],
                change["current"],
                change["impact"],
                change["risk"],
            )
            for change in INITIAL_RULE_CHANGES
        ],
    )


def row_to_rule(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "summary": row["summary"],
        "specs": decode(row["specs_json"]),
        "notes": decode(row["notes_json"]),
        "commonMistakes": decode(row["mistakes_json"]),
        "severity": row["severity"],
        "updatedAt": row["updated_at"],
    }


def row_to_version(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "publishedAt": row["published_at"],
        "source": row["source"],
        "status": row["status"],
        "changes": decode(row["changes_json"]),
    }


def row_to_rule_change(row: sqlite3.Row) -> dict:
    return {
        "ruleId": row["rule_id"],
        "title": row["title"],
        "previous": row["previous"],
        "current": row["current"],
        "impact": row["impact"],
        "risk": row["risk"],
    }


def create_token() -> str:
    return secrets.token_urlsafe(32)
