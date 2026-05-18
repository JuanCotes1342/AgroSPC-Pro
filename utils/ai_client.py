from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st


GEMINI_MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MAX_PROMPT_CHARS = 6500
MAX_OUTPUT_TOKENS = 2800
EXPERT_SYSTEM_PROMPT = (
    "Actua siempre como analista estadistico especialista en control estadistico de calidad "
    "para agroindustria, SPC/CEP, frutas, hortalizas y plantas medicinales. "
    "Razona con criterio experto, sin presentarte como persona ni mencionar anos de experiencia. "
    "Escribe con tono humano, profesional y facil de entender para estudiantes y usuarios no expertos. "
    "Explica las conclusiones paso a paso, con lenguaje simple, pero sin perder rigor tecnico. "
    "Distingue claramente subgrupos o puntos del grafico frente a mediciones totales; no los mezcles. "
    "Prioriza precision, decisiones accionables y consumo moderado de tokens. "
    "Usa este formato cuando aplique: diagnostico, evidencia, significado practico, riesgo y recomendacion. "
    "Evita sonar robotico, no uses frases cortadas ni estilo telegrama, y no repitas datos innecesarios. "
    "Cierra siempre las listas y conclusiones; no termines con numerales, frases incompletas ni markdown abierto."
)


def build_prompt(prompt: str) -> str:
    compact = " ".join(prompt.split())
    if len(compact) > MAX_PROMPT_CHARS:
        compact = compact[:MAX_PROMPT_CHARS] + " ...[contexto truncado para ahorrar tokens]"
    return f"{EXPERT_SYSTEM_PROMPT}\n\nCaso a analizar:\n{compact}"


def get_gemini_key() -> str | None:
    session_key = st.session_state.get("gemini_api_key")
    if session_key:
        return session_key
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def get_deepseek_key() -> str | None:
    env_key = os.getenv("DEEPSEEK_API_KEY")
    if env_key:
        return env_key
    try:
        return st.secrets.get("DEEPSEEK_API_KEY")
    except Exception:
        return None


def gemini_available() -> bool:
    return bool(get_gemini_key())


def deepseek_available() -> bool:
    return bool(get_deepseek_key())


def generate_with_deepseek(prompt: str, *, temperature: float = 0.35) -> str:
    api_key = get_deepseek_key()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY no configurada")
    payload: dict[str, Any] = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": EXPERT_SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(prompt)},
        ],
        "temperature": temperature,
        "max_tokens": MAX_OUTPUT_TOKENS,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def generate_with_gemini(prompt: str, *, temperature: float = 0.35) -> str:
    api_key = get_gemini_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY no configurada")
    payload: dict[str, Any] = {
        "contents": [{"parts": [{"text": build_prompt(prompt)}]}],
        "generationConfig": {"temperature": temperature, "topP": 0.85, "maxOutputTokens": MAX_OUTPUT_TOKENS},
    }
    errors = []
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as exc:
            errors.append(f"{model}: {exc}")
    raise RuntimeError("; ".join(errors))


def generate_text(prompt: str, fallback: str, *, temperature: float = 0.35) -> tuple[str, str]:
    try:
        return generate_with_deepseek(prompt, temperature=temperature), "DeepSeek"
    except Exception as deepseek_exc:
        deepseek_error = deepseek_exc
    try:
        return generate_with_gemini(prompt, temperature=temperature), "Gemini"
    except Exception as exc:
        return f"{fallback}\n\nNota tecnica: se uso modo local porque la IA externa no respondio (DeepSeek: {deepseek_error}; Gemini: {exc}).", "Local"
