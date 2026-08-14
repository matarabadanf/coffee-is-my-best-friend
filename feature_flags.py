"""Autonomous time-gated feature rollout engine with Madrid timezone, simulation support, and surprise sidebar concealment."""
import pandas as pd
import streamlit as st

FEATURE_DROPS = {
    "world_update": {
        "date": "2026-08-15 00:00:00",
        "title": "🌍 World Update",
        "tagline": "Every cup has a story. Where were you?",
        "pages": ["3_🌍_World_Explorer", "World_Explorer", "3_🌍", "4_🌍_World_Explorer"],
    },
    "rpg_quests": {
        "date": "2026-09-27",
        "title": "⚔️ RPG Quest Engine",
        "tagline": "Your caffeine fuels the blade.",
        "pages": ["5_⚔️_Quest_Board", "6_🎒_Hero_Inventory", "Quest_Board", "Hero_Inventory", "5_", "6_"],
    },
    "gacha_raids": {
        "date": "2026-10-16",
        "title": "🎰 Gacha & Boss Raids",
        "tagline": "The beans of fortune await.",
        "pages": ["7_🎰_Gacha", "8_🐉_Boss_Raids", "Gacha", "Boss_Raids", "7_", "8_"],
        "requires": ["rpg_quests"],
    },
    "coffee_wrapped": {
        "date": "2026-10-31",
        "title": "🎁 Coffee Wrapped 2026",
        "tagline": "Your year in every sip.",
        "pages": ["10_🎁_Wrapped", "Wrapped", "10_"],
        "hidden_until_unlock": True,
    },
}

def get_current_madrid_time() -> pd.Timestamp:
    """Returns current timestamp in Europe/Madrid. Supports ?sim_date=YYYY-MM-DD for release simulation."""
    sim_date = None
    try:
        if hasattr(st, "query_params") and "sim_date" in st.query_params:
            sim_date = st.query_params["sim_date"]
        elif hasattr(st, "experimental_get_query_params"):
            qp = st.experimental_get_query_params()
            if "sim_date" in qp:
                sim_date = qp["sim_date"][0]
        if not sim_date and "sim_date" in st.session_state:
            sim_date = st.session_state["sim_date"]
    except Exception:
        pass

    if sim_date:
        try:
            ts = pd.Timestamp(sim_date)
            if ts.tzinfo is None:
                return ts.tz_localize("Europe/Madrid")
            return ts.tz_convert("Europe/Madrid")
        except Exception:
            pass

    return pd.Timestamp.now(tz="Europe/Madrid")

def is_dev_mode(user: str = None) -> bool:
    """Check if current session has explicit dev parameter."""
    try:
        from utils import is_pin_verified
    except ImportError:
        def is_pin_verified(u):
            return False

    current_user = user or st.session_state.get("user", "") or st.query_params.get("user", "")
    return (st.query_params.get("dev") == "1" or is_pin_verified(current_user))

def is_unlocked(feature_key: str, dev_bypass: bool = False) -> bool:
    """Check if a feature is unlocked based on date/timezone or dev bypass."""
    if dev_bypass or feature_key == "world_update":
        return True
    drop = FEATURE_DROPS.get(feature_key)
    if not drop:
        return False
    now = get_current_madrid_time()
    unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
    return now >= unlock

def is_patch_notes_active(feature_key: str, dev_bypass: bool = False, days: int = 7) -> bool:
    """Checks if patch notes should be displayed (active for 7 days upon unlock or in dev mode)."""
    drop = FEATURE_DROPS.get(feature_key)
    if not drop:
        return False
    now = get_current_madrid_time()
    unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
    patch_end = unlock + pd.Timedelta(days=days, hours=23, minutes=59, seconds=59)
    
    if dev_bypass:
        return True
    return unlock <= now <= patch_end

def get_next_drop() -> dict | None:
    """Get the next upcoming feature drop."""
    now = get_current_madrid_time()
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
    now = get_current_madrid_time()
    unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
    delta = unlock - now
    if delta.total_seconds() <= 0:
        return "🔓 UNLOCKED!"
    days, hours = delta.days, delta.seconds // 3600
    if days > 0:
        return f"🔒 {days}d {hours}h"
    return f"🔒 {hours}h {(delta.seconds % 3600) // 60}m"

def get_locked_sidebar_css(user: str = None) -> str:
    """Generates CSS to conceal locked surprise drops from the Streamlit sidebar for non-dev users."""
    dev_bypass = is_dev_mode(user)
    hidden_selectors = []

    for key, drop in FEATURE_DROPS.items():
        if not is_unlocked(key, dev_bypass=dev_bypass):
            for p in drop.get("pages", []):
                hidden_selectors.append(f'div[data-testid="stSidebarNav"] li:has(a[href*="{p}"])')
                hidden_selectors.append(f'div[data-testid="stSidebarNavItems"] li:has(a[href*="{p}"])')
                hidden_selectors.append(f'a[data-testid="stSidebarNavLink"][href*="{p}"]')
                hidden_selectors.append(f'div[data-testid="stSidebarNav"] a[href*="{p}"]')
                hidden_selectors.append(f'a[href*="{p}"]')

    if not hidden_selectors:
        return ""

    combined = ", ".join(hidden_selectors)
    return f"""
    /* Surprise Drop Concealment — Hide locked pages from sidebar navigation */
    {combined} {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }}
    """
