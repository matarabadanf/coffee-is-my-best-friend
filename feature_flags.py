"""Autonomous time-gated feature rollout engine. Madrid timezone."""
import pandas as pd
import streamlit as st

FEATURE_DROPS = {
    "world_update": {
        "date": "2026-09-01",
        "title": "🌍 World Update",
        "tagline": "Every cup has a story. Where were you?",
        "pages": ["4_🌍_World_Explorer"],
    },
    "rpg_quests": {
        "date": "2026-09-27",
        "title": "⚔️ RPG Quest Engine",
        "tagline": "Your caffeine fuels the blade.",
        "pages": ["5_⚔️_Quest_Board", "6_🎒_Hero_Inventory"],
    },
    "gacha_raids": {
        "date": "2026-10-16",
        "title": "🎰 Gacha & Boss Raids",
        "tagline": "The beans of fortune await.",
        "pages": ["7_🎰_Gacha", "8_🐉_Boss_Raids"],
        "requires": ["rpg_quests"],
    },
    "coffee_wrapped": {
        "date": "2026-10-31",
        "title": "🎁 Coffee Wrapped 2026",
        "tagline": "Your year in every sip.",
        "pages": ["10_🎁_Wrapped"],
        "hidden_until_unlock": True,
    },
}

def is_dev_mode(user: str = None) -> bool:
    """Check if current session has dev privileges. Fer is the developer and has automatic bypass."""
    try:
        from utils import is_pin_verified
    except ImportError:
        def is_pin_verified(u):
            return False

    current_user = user or st.session_state.get("user", "") or st.query_params.get("user", "")
    if current_user == "Fer":
        return True

    return (st.query_params.get("dev") == "1" or
            is_pin_verified(current_user))

def is_unlocked(feature_key: str, dev_bypass: bool = False) -> bool:
    """Check if a feature is unlocked based on date and timezone or dev bypass."""
    if dev_bypass:
        return True
    drop = FEATURE_DROPS.get(feature_key)
    if not drop:
        return False
    now = pd.Timestamp.now(tz="Europe/Madrid")
    unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
    return now >= unlock

def get_next_drop() -> dict | None:
    """Get the next upcoming feature drop."""
    now = pd.Timestamp.now(tz="Europe/Madrid")
    upcoming = []
    for key, drop in FEATURE_DROPS.items():
        unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
        if now < unlock:
            upcoming.append({**drop, "key": key, "unlock_date": unlock})
    return min(upcoming, key=lambda d: d["unlock_date"]) if upcoming else None

def get_countdown_text(feature_key: str) -> str:
    """Get formatted countdown text for a locked feature."""
    drop = FEATURE_DROPS.get(feature_key)
    if not drop:
        return "🔒 Locked"
    now = pd.Timestamp.now(tz="Europe/Madrid")
    unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
    delta = unlock - now
    if delta.total_seconds() <= 0:
        return "🔓 UNLOCKED!"
    days, hours = delta.days, delta.seconds // 3600
    if days > 0:
        return f"🔒 {days}d {hours}h"
    return f"🔒 {hours}h {(delta.seconds % 3600) // 60}m"
