from __future__ import annotations

import json
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .database import (
    connect,
    create_token,
    encode,
    hash_password,
    init_db,
    now_iso,
    row_to_rule,
    row_to_rule_change,
    row_to_version,
)

app = FastAPI(title="Paper Review API", version="0.3.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict[str, dict[str, str]] = {}


class LoginRequest(BaseModel):
    account: str
    password: str


class RuleInput(BaseModel):
    id: str = Field(min_length=3)
    name: str
    summary: str
    specs: list[dict[str, str]]
    notes: list[str]
    commonMistakes: list[str]
    severity: str
    updatedAt: str


class VersionInput(BaseModel):
    id: str = Field(min_length=3)
    name: str
    publishedAt: str
    source: str
    status: str = "draft"
    changes: list[str]


class RuleChangeInput(BaseModel):
    versionId: str
    ruleId: str
    title: str
    previous: str
    current: str
    impact: str
    risk: str


class StudentProgressInput(BaseModel):
    checkedKeys: list[str]


def audit(actor: str, action: str, target: str, detail: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO audit_logs (actor, action, target, detail, created_at) VALUES (?, ?, ?, ?, ?)",
            (actor, action, target, detail, now_iso()),
        )


def current_user(authorization: str | None = Header(default=None)) -> dict[str, str]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.removeprefix("Bearer ").strip()
    user = sessions.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def admin_user(user: dict[str, str] = Depends(current_user)) -> dict[str, str]:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required")
    return user


def get_rule_pack() -> dict[str, Any]:
    with connect() as conn:
        current = conn.execute(
            "SELECT * FROM versions WHERE status = 'published' ORDER BY published_at DESC LIMIT 1"
        ).fetchone()
        previous = conn.execute(
            "SELECT * FROM versions WHERE id != ? ORDER BY published_at DESC LIMIT 1",
            (current["id"],),
        ).fetchone()
        rules = conn.execute("SELECT * FROM rules ORDER BY id").fetchall()
        changes = conn.execute(
            "SELECT * FROM rule_changes WHERE version_id = ? ORDER BY id",
            (current["id"],),
        ).fetchall()

    return {
        "previousVersion": row_to_version(previous),
        "currentVersion": row_to_version(current),
        "ruleChanges": [row_to_rule_change(row) for row in changes],
        "thesisRules": [row_to_rule(row) for row in rules],
    }


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/auth/login")
def login(payload: LoginRequest) -> dict:
    with connect() as conn:
        user = conn.execute("SELECT * FROM users WHERE account = ?", (payload.account,)).fetchone()

    if not user or user["password_hash"] != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid account or password")

    token = create_token()
    sessions[token] = {"account": user["account"], "name": user["name"], "role": user["role"]}
    audit(user["account"], "login", "session", f"{user['role']} login")
    return {"token": token, "user": sessions[token]}


@app.get("/api/rule-pack")
def read_rule_pack(_: dict[str, str] = Depends(current_user)) -> dict:
    return get_rule_pack()


@app.get("/api/rule-versions/current")
def get_current_rule_version() -> dict:
    return get_rule_pack()


@app.get("/api/admin/rules")
def list_rules(_: dict[str, str] = Depends(admin_user)) -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM rules ORDER BY id").fetchall()
    return [row_to_rule(row) for row in rows]


@app.post("/api/admin/rules")
def create_rule(payload: RuleInput, user: dict[str, str] = Depends(admin_user)) -> dict:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO rules (id, name, summary, specs_json, notes_json, mistakes_json, severity, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.id,
                payload.name,
                payload.summary,
                encode(payload.specs),
                encode(payload.notes),
                encode(payload.commonMistakes),
                payload.severity,
                payload.updatedAt,
            ),
        )
    audit(user["account"], "create_rule", payload.id, payload.name)
    return payload.model_dump()


@app.put("/api/admin/rules/{rule_id}")
def update_rule(rule_id: str, payload: RuleInput, user: dict[str, str] = Depends(admin_user)) -> dict:
    with connect() as conn:
        result = conn.execute(
            """
            UPDATE rules
            SET name = ?, summary = ?, specs_json = ?, notes_json = ?, mistakes_json = ?, severity = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                payload.name,
                payload.summary,
                encode(payload.specs),
                encode(payload.notes),
                encode(payload.commonMistakes),
                payload.severity,
                payload.updatedAt,
                rule_id,
            ),
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rule not found")
    audit(user["account"], "update_rule", rule_id, payload.name)
    return {**payload.model_dump(), "id": rule_id}


@app.delete("/api/admin/rules/{rule_id}")
def delete_rule(rule_id: str, user: dict[str, str] = Depends(admin_user)) -> dict:
    with connect() as conn:
        result = conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rule not found")
    audit(user["account"], "delete_rule", rule_id, "deleted")
    return {"ok": True}


@app.get("/api/admin/versions")
def list_versions(_: dict[str, str] = Depends(admin_user)) -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM versions ORDER BY published_at DESC").fetchall()
    return [row_to_version(row) for row in rows]


@app.get("/api/admin/rule-changes")
def list_rule_changes(_: dict[str, str] = Depends(admin_user)) -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM rule_changes ORDER BY id DESC").fetchall()
    return [row_to_rule_change(row) for row in rows]


@app.post("/api/admin/rule-changes")
def create_rule_change(payload: RuleChangeInput, user: dict[str, str] = Depends(admin_user)) -> dict:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO rule_changes (version_id, rule_id, title, previous, current, impact, risk)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.versionId,
                payload.ruleId,
                payload.title,
                payload.previous,
                payload.current,
                payload.impact,
                payload.risk,
            ),
        )
        row = conn.execute("SELECT * FROM rule_changes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    audit(user["account"], "create_rule_change", payload.ruleId, payload.title)
    return row_to_rule_change(row)


@app.put("/api/admin/rule-changes/{change_id}")
def update_rule_change(change_id: int, payload: RuleChangeInput, user: dict[str, str] = Depends(admin_user)) -> dict:
    with connect() as conn:
        result = conn.execute(
            """
            UPDATE rule_changes
            SET version_id = ?, rule_id = ?, title = ?, previous = ?, current = ?, impact = ?, risk = ?
            WHERE id = ?
            """,
            (
                payload.versionId,
                payload.ruleId,
                payload.title,
                payload.previous,
                payload.current,
                payload.impact,
                payload.risk,
                change_id,
            ),
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rule change not found")
        row = conn.execute("SELECT * FROM rule_changes WHERE id = ?", (change_id,)).fetchone()
    audit(user["account"], "update_rule_change", payload.ruleId, payload.title)
    return row_to_rule_change(row)


@app.delete("/api/admin/rule-changes/{change_id}")
def delete_rule_change(change_id: int, user: dict[str, str] = Depends(admin_user)) -> dict:
    with connect() as conn:
        target = conn.execute("SELECT * FROM rule_changes WHERE id = ?", (change_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Rule change not found")
        conn.execute("DELETE FROM rule_changes WHERE id = ?", (change_id,))
    audit(user["account"], "delete_rule_change", str(change_id), target["title"])
    return {"ok": True}


@app.post("/api/admin/versions")
def create_version(payload: VersionInput, user: dict[str, str] = Depends(admin_user)) -> dict:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO versions (id, name, published_at, source, status, changes_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (payload.id, payload.name, payload.publishedAt, payload.source, payload.status, encode(payload.changes)),
        )
    audit(user["account"], "create_version", payload.id, payload.name)
    return payload.model_dump()


@app.post("/api/admin/versions/{version_id}/publish")
def publish_version(version_id: str, user: dict[str, str] = Depends(admin_user)) -> dict:
    with connect() as conn:
        target = conn.execute("SELECT * FROM versions WHERE id = ?", (version_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Version not found")
        conn.execute("UPDATE versions SET status = 'archived' WHERE status = 'published'")
        conn.execute("UPDATE versions SET status = 'published' WHERE id = ?", (version_id,))
    audit(user["account"], "publish_version", version_id, target["name"])
    return {"ok": True}


@app.get("/api/admin/audit-logs")
def list_audit_logs(_: dict[str, str] = Depends(admin_user)) -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50").fetchall()
    return [dict(row) for row in rows]


@app.get("/api/me/progress")
def get_my_progress(user: dict[str, str] = Depends(current_user)) -> dict:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM student_progress WHERE user_account = ?",
            (user["account"],),
        ).fetchall()
    return {
        "items": {
            row["rule_id"]: {
                "checkedKeys": json.loads(row["checked_json"]),
                "updatedAt": row["updated_at"],
            }
            for row in rows
        }
    }


@app.put("/api/me/progress/{rule_id}")
def save_my_progress(rule_id: str, payload: StudentProgressInput, user: dict[str, str] = Depends(current_user)) -> dict:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO student_progress (user_account, rule_id, checked_json, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_account, rule_id)
            DO UPDATE SET checked_json = excluded.checked_json, updated_at = excluded.updated_at
            """,
            (user["account"], rule_id, encode(payload.checkedKeys), now_iso()),
        )
    return {"ok": True}
