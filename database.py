"""
SQLite database helper for persisting user profiles and weekly snapshots.
"""

import sqlite3
import json
import datetime
from config import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they do not exist."""
    conn = _connect()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT,
            password    TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            age         INTEGER,
            career_goal TEXT,
            account_id  INTEGER,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS snapshots (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            snapshot_date   TEXT DEFAULT (date('now')),

            -- daily routine
            study_hours         REAL,
            screen_time         REAL,
            sleep_hours         REAL,
            skill_learning_hrs  REAL,
            exercise_hours      REAL,
            distraction_hours   REAL,

            -- weekly productivity
            projects_building   INTEGER,
            courses_learning    INTEGER,
            consistency_level   INTEGER,
            focus_level         INTEGER,

            -- self reflection (stored as JSON)
            reflection_json     TEXT,

            -- computed results (stored as JSON)
            result_json         TEXT,

            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


# ── Auth CRUD ───────────────────────────────────────────────

import hashlib

def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_account(email: str, password: str, username: str = "") -> bool:
    """Register a new account. Returns True on success, False if email taken."""
    conn = _connect()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO accounts (email, password, username) VALUES (?, ?, ?)",
            (email.strip().lower(), _hash_pw(password), username.strip()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate(email: str, password: str):
    """Return account row dict if credentials valid, else None."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM accounts WHERE email = ? AND password = ?",
        (email.strip().lower(), _hash_pw(password)),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ── User CRUD ───────────────────────────────────────────────

def upsert_user(name: str, age: int, career_goal: str) -> int:
    """Insert or update a user and return the user id."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        uid = row["id"]
        cur.execute(
            "UPDATE users SET age = ?, career_goal = ? WHERE id = ?",
            (age, career_goal, uid),
        )
    else:
        cur.execute(
            "INSERT INTO users (name, age, career_goal) VALUES (?, ?, ?)",
            (name, age, career_goal),
        )
        uid = cur.lastrowid
    conn.commit()
    conn.close()
    return uid


def get_user(name: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ── Snapshot CRUD ───────────────────────────────────────────

def save_snapshot(user_id: int, daily: dict, weekly: dict,
                  reflection: dict, result: dict) -> int:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO snapshots
            (user_id, study_hours, screen_time, sleep_hours,
             skill_learning_hrs, exercise_hours, distraction_hours,
             projects_building, courses_learning, consistency_level,
             focus_level, reflection_json, result_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        daily.get("study_hours", 0),
        daily.get("screen_time", 0),
        daily.get("sleep_hours", 0),
        daily.get("skill_learning_hours", 0),
        daily.get("exercise_hours", 0),
        daily.get("distraction_hours", 0),
        weekly.get("projects_building", 0),
        weekly.get("courses_learning", 0),
        weekly.get("consistency_level", 5),
        weekly.get("focus_level", 5),
        json.dumps(reflection),
        json.dumps(result),
    ))
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid


def get_user_snapshots(user_id: int, limit: int = 12) -> list:
    """Return the most recent snapshots for a user."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM snapshots WHERE user_id = ? ORDER BY snapshot_date DESC LIMIT ?",
        (user_id, limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    # parse JSON fields
    for r in rows:
        r["reflection"] = json.loads(r["reflection_json"]) if r["reflection_json"] else {}
        r["result"]     = json.loads(r["result_json"])     if r["result_json"] else {}
    return rows


# ── Initialise on import ────────────────────────────────────
init_db()
