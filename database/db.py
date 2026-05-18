from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "spc_quality.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT,
                creado_en TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS muestras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT, tipo_producto TEXT, lote TEXT, analista TEXT,
                fecha TEXT, hora TEXT, observaciones TEXT, payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL, unidad TEXT, lsl REAL, usl REAL
            );
            CREATE TABLE IF NOT EXISTS atributos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL, descripcion TEXT
            );
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analisis_id INTEGER, tipo TEXT, payload TEXT NOT NULL, creado_en TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL, activo INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS analisis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL, metadata TEXT NOT NULL, data_json TEXT NOT NULL,
                creado_en TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS analisis_temporales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_sesion TEXT NOT NULL,
                nombre TEXT NOT NULL,
                payload TEXT NOT NULL,
                creado_en TEXT NOT NULL,
                expira_en TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analisis_temporales_codigo ON analisis_temporales(codigo_sesion, expira_en)")
        cleanup_expired_analyses(conn)


def cleanup_expired_analyses(conn: sqlite3.Connection | None = None) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    if conn is not None:
        conn.execute("DELETE FROM analisis_temporales WHERE expira_en < ?", (now,))
        return
    with get_connection() as local_conn:
        local_conn.execute("DELETE FROM analisis_temporales WHERE expira_en < ?", (now,))


def dataframe_to_json(df: pd.DataFrame) -> str:
    return df.to_json(orient="records", date_format="iso")


def dataframe_from_json(payload: str) -> pd.DataFrame:
    return pd.read_json(StringIO(payload), orient="records")


def save_analysis(name: str, metadata: dict, df: pd.DataFrame, session_code: str = "default") -> int:
    payload = {
        "metadata": metadata,
        "variable_df": dataframe_to_json(df),
        "attribute_df": dataframe_to_json(pd.DataFrame()),
        "pareto_df": dataframe_to_json(pd.DataFrame()),
        "ishikawa_effect": "",
        "ishikawa_causes": {},
    }
    return save_temp_analysis(session_code, name, payload)


def save_temp_analysis(session_code: str, name: str, payload: dict, days: int = 7) -> int:
    session_code = session_code.strip().lower()
    if not session_code:
        raise ValueError("Session code is required")
    now = datetime.now().isoformat(timespec="seconds")
    expires = (datetime.now() + timedelta(days=days)).isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO analisis_temporales(codigo_sesion, nombre, payload, creado_en, expira_en) VALUES (?, ?, ?, ?, ?)",
            (session_code, name, json.dumps(payload, ensure_ascii=False), now, expires),
        )
        return int(cursor.lastrowid)


def list_analyses(session_code: str | None = None) -> pd.DataFrame:
    cleanup_expired_analyses()
    with get_connection() as conn:
        if session_code:
            return pd.read_sql_query(
                "SELECT id, nombre, creado_en, expira_en FROM analisis_temporales WHERE codigo_sesion=? ORDER BY id DESC",
                conn,
                params=(session_code.strip().lower(),),
            )
        return pd.read_sql_query("SELECT id, nombre, creado_en, expira_en, codigo_sesion FROM analisis_temporales ORDER BY id DESC", conn)


def load_analysis(analysis_id: int, session_code: str | None = None) -> dict:
    cleanup_expired_analyses()
    with get_connection() as conn:
        if session_code:
            row = conn.execute(
                "SELECT payload FROM analisis_temporales WHERE id=? AND codigo_sesion=?",
                (analysis_id, session_code.strip().lower()),
            ).fetchone()
        else:
            row = conn.execute("SELECT payload FROM analisis_temporales WHERE id=?", (analysis_id,)).fetchone()
    if not row:
        raise ValueError("Analysis not found")
    return json.loads(row[0])


def delete_analysis(analysis_id: int, session_code: str | None = None) -> None:
    with get_connection() as conn:
        if session_code:
            conn.execute("DELETE FROM analisis_temporales WHERE id=? AND codigo_sesion=?", (analysis_id, session_code.strip().lower()))
        else:
            conn.execute("DELETE FROM analisis_temporales WHERE id=?", (analysis_id,))
