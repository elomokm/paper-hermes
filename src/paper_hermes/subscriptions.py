"""Subscription management — persistent topic subscriptions."""

import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


SUBSCRIPTIONS_FILE = Path(__file__).parent.parent.parent / "subscriptions.json"


@dataclass
class Subscription:
    topic: str  # e.g., "safran-veille", "ml-maths"
    query: str  # arXiv search query
    frequency: str = "daily"  # daily | weekly
    last_run: str = ""  # ISO date of last digest run
    created_at: str = ""


def load_subscriptions() -> list[dict]:
    if not SUBSCRIPTIONS_FILE.exists():
        return []
    return json.loads(SUBSCRIPTIONS_FILE.read_text())


def save_subscriptions(subs: list[dict]) -> None:
    SUBSCRIPTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUBSCRIPTIONS_FILE.write_text(json.dumps(subs, indent=2, ensure_ascii=False))


def add_subscription(topic: str, query: str, frequency: str = "daily") -> dict:
    subs = load_subscriptions()

    # Upsert
    for s in subs:
        if s["topic"] == topic:
            s["query"] = query
            s["frequency"] = frequency
            save_subscriptions(subs)
            return s

    sub = {
        "topic": topic,
        "query": query,
        "frequency": frequency,
        "last_run": "",
        "created_at": datetime.now().isoformat()[:10],
    }
    subs.append(sub)
    save_subscriptions(subs)
    return sub


def remove_subscription(topic: str) -> bool:
    subs = load_subscriptions()
    new_subs = [s for s in subs if s["topic"] != topic]
    if len(new_subs) == len(subs):
        return False
    save_subscriptions(new_subs)
    return True


def update_last_run(topic: str, date: str) -> None:
    subs = load_subscriptions()
    for s in subs:
        if s["topic"] == topic:
            s["last_run"] = date
    save_subscriptions(subs)
