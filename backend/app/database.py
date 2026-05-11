import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import get_settings


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS knowledge_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    file_path TEXT NOT NULL,
    sources TEXT,
    trust_score REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    task TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    input TEXT,
    output TEXT,
    score REAL,
    status TEXT NOT NULL,
    error_message TEXT,
    runtime_ms INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS improvement_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    lesson_type TEXT NOT NULL,
    agent_name TEXT,
    task_id TEXT,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    version TEXT NOT NULL,
    prompt TEXT NOT NULL,
    score REAL,
    is_active INTEGER DEFAULT 0,
    risk_level TEXT DEFAULT 'low',
    change_reason TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    suggestion TEXT NOT NULL,
    expected_benefit TEXT,
    risk_level TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_scoreboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL UNIQUE,
    total_runs INTEGER DEFAULT 0,
    success_runs INTEGER DEFAULT 0,
    failed_runs INTEGER DEFAULT 0,
    average_score REAL DEFAULT 0,
    average_runtime_ms INTEGER DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    display_name TEXT,
    email TEXT NULL,
    mode TEXT DEFAULT 'local',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    role TEXT,
    language TEXT DEFAULT 'vi',
    answer_style TEXT,
    technical_level TEXT,
    preferences_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_memories (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    confidence REAL DEFAULT 0.7,
    importance INTEGER DEFAULT 1,
    expires_at TEXT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    archived_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    user_id TEXT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    category TEXT DEFAULT 'custom',
    description TEXT,
    role TEXT NOT NULL,
    goal TEXT,
    system_prompt TEXT,
    default_model TEXT,
    temperature REAL DEFAULT 0.2,
    risk_level TEXT DEFAULT 'low',
    is_system INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    allowed_tools_json TEXT,
    input_schema_json TEXT,
    output_schema_json TEXT,
    evaluation_metrics_json TEXT,
    config_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, slug)
);

CREATE TABLE IF NOT EXISTS tools (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    input_schema_json TEXT,
    output_schema_json TEXT,
    permission_level TEXT NOT NULL,
    timeout_seconds INTEGER DEFAULT 30,
    retry_policy_json TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_tools (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(agent_id, tool_id)
);

CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    user_id TEXT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    description TEXT,
    definition_json TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_runs (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NULL,
    user_id TEXT NULL,
    input_json TEXT,
    output_json TEXT,
    status TEXT NOT NULL,
    runtime_ms INTEGER,
    created_at TEXT NOT NULL,
    completed_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS workflow_steps (
    id TEXT PRIMARY KEY,
    workflow_run_id TEXT NOT NULL,
    agent_id TEXT NULL,
    step_name TEXT NOT NULL,
    input_json TEXT,
    output_json TEXT,
    status TEXT NOT NULL,
    runtime_ms INTEGER,
    order_index INTEGER,
    created_at TEXT NOT NULL,
    completed_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS approval_requests (
    id TEXT PRIMARY KEY,
    user_id TEXT NULL,
    workflow_run_id TEXT NULL,
    agent_run_id TEXT NULL,
    action_type TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    payload_json TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    resolved_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS evaluations (
    id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    dataset_id TEXT NULL,
    score REAL,
    metrics_json TEXT,
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    dataset_type TEXT NOT NULL,
    items_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_feedbacks (
    id TEXT PRIMARY KEY,
    user_id TEXT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    rating INTEGER,
    comment TEXT,
    created_at TEXT NOT NULL
);
"""


AGENT_COLUMN_MIGRATIONS = {
    "category": "TEXT DEFAULT 'custom'",
    "description": "TEXT",
    "allowed_tools_json": "TEXT",
    "input_schema_json": "TEXT",
    "output_schema_json": "TEXT",
    "evaluation_metrics_json": "TEXT",
}


def get_database_path() -> Path:
    return get_settings().database_path


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA_SQL)
        _ensure_columns(connection, "agents", AGENT_COLUMN_MIGRATIONS)


def _ensure_columns(connection: sqlite3.Connection, table_name: str, columns: dict[str, str]) -> None:
    existing = {
        str(row["name"])
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    for column_name, column_definition in columns.items():
        if column_name in existing:
            continue
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
