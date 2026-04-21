import json
from pathlib import Path
from typing import Any


def load_data(filepath: str) -> Any:
    with Path(filepath).open() as f:
        return json.load(f)


STATUS_COLORS: dict = {
    "On Track": "#16A34A",
    "At Risk": "#D97706",
    "Blocked": "#DC2626",
    "Complete": "#2563EB",
}

SEVERITY_COLORS: dict = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#D97706",
    "Low": "#65A30D",
}

STATUS_EMOJI: dict = {
    "On Track": "🟢",
    "At Risk": "🟡",
    "Blocked": "🔴",
    "Complete": "✅",
}

PRIORITY_EMOJI: dict = {
    "Critical": "🔥",
    "High": "⚡",
    "Medium": "📌",
    "Low": "💤",
}


def readiness_color(score: float) -> str:
    if score >= 80:
        return "#16A34A"
    if score >= 60:
        return "#D97706"
    return "#DC2626"


def readiness_label(score: float) -> str:
    if score >= 80:
        return "GREEN — On Track for Launch"
    if score >= 60:
        return "AMBER — Attention Required"
    return "RED — Launch at Risk"


def readiness_rag(score: float) -> str:
    if score >= 80:
        return "GREEN"
    if score >= 60:
        return "AMBER"
    return "RED"
