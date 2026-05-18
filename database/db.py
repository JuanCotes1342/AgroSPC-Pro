from __future__ import annotations

import json
import sqlite3
from datetime import datetime
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
            """
        )


def save_analysis(name: str, metadata: dict, df: pd.DataFrame) -> int:
    payload = df.to_json(orient="records", date_format="iso")
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO analisis(nombre, metadata, data_json, creado_en) VALUES (?, ?, ?, ?)",
            (name, json.dumps(metadata, ensure_ascii=False), payload, now),
        )
        return int(cursor.lastrowid)


def list_analyses() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query("SELECT id, nombre, creado_en, metadata FROM analisis ORDER BY id DESC", conn)


def load_analysis(analysis_id: int) -> tuple[dict, pd.DataFrame]:
    with get_connection() as conn:
        row = conn.execute("SELECT metadata, data_json FROM analisis WHERE id=?", (analysis_id,)).fetchone()
    if not row:
        raise ValueError("Analysis not found")
    return json.loads(row[0]), pd.read_json(row[1], orient="records")


def delete_analysis(analysis_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM analisis WHERE id=?", (analysis_id,))
