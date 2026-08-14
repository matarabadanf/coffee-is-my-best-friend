# Drop 1 — 🌍 World Update: Travel Tracker

> *"Every cup has a story. Where were you?"*

This is an **ULTRA-EXPLICIT, step-by-step implementation guide** for adding the World Update to the app. 

### Core Concept
The World Update tracks **where the user physically IS** when they drink their coffee/tea. It is a **travel tracker**, NOT a coffee-origin tracker. 
All 3 users (Cris, Bea, Fer) live in Madrid, Spain. Their default country is `"ES"`. When they travel, they change the country selector to reflect their current location.

The feature auto-unlocks on **September 1, 2026 (Madrid time)**.

---

## Step 1: Create `feature_flags.py`

This file is required to gate the Drop 1 (and future drops) features until their release date.

Create a new file at: `\\wsl.localhost\Ubuntu-26.04\home\matis-ubuntu\bin\coffee-is-my-best-friend\feature_flags.py`

```python
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

def is_unlocked(feature_key: str, dev_bypass: bool = False) -> bool:
    if dev_bypass:
        return True
    drop = FEATURE_DROPS.get(feature_key)
    if not drop:
        return False
    now = pd.Timestamp.now(tz="Europe/Madrid")
    unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
    return now >= unlock

def get_next_drop() -> dict | None:
    now = pd.Timestamp.now(tz="Europe/Madrid")
    upcoming = []
    for key, drop in FEATURE_DROPS.items():
        unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
        if now < unlock:
            upcoming.append({**drop, "key": key, "unlock_date": unlock})
    return min(upcoming, key=lambda d: d["unlock_date"]) if upcoming else None

def get_countdown_text(feature_key: str) -> str:
    drop = FEATURE_DROPS[feature_key]
    now = pd.Timestamp.now(tz="Europe/Madrid")
    unlock = pd.Timestamp(drop["date"], tz="Europe/Madrid")
    delta = unlock - now
    if delta.total_seconds() <= 0:
        return "🔓 UNLOCKED!"
    days, hours = delta.days, delta.seconds // 3600
    if days > 0:
        return f"🔒 {days}d {hours}h"
    return f"🔒 {hours}h {(delta.seconds % 3600) // 60}m"

def is_dev_mode() -> bool:
    from utils import is_pin_verified
    return (st.query_params.get("dev") == "1" or
            is_pin_verified(st.session_state.get("user", "")))
```

---

## Step 2: Create `world_data.py`

Create a new file at: `\\wsl.localhost\Ubuntu-26.04\home\matis-ubuntu\bin\coffee-is-my-best-friend\world_data.py`

```python
"""Travel country registry and passport computation helpers for the World Update."""

from typing import TypedDict

class CountryInfo(TypedDict):
    name: str
    flag: str
    continent: str

# 40+ popular travel destinations covering all 6 inhabited continents
TRAVEL_COUNTRIES: dict[str, CountryInfo] = {
    # ── Europe ──
    "ES": {"name": "Spain",           "flag": "🇪🇸", "continent": "Europe"},
    "FR": {"name": "France",          "flag": "🇫🇷", "continent": "Europe"},
    "IT": {"name": "Italy",           "flag": "🇮🇹", "continent": "Europe"},
    "PT": {"name": "Portugal",        "flag": "🇵🇹", "continent": "Europe"},
    "GB": {"name": "United Kingdom",  "flag": "🇬🇧", "continent": "Europe"},
    "DE": {"name": "Germany",         "flag": "🇩🇪", "continent": "Europe"},
    "NL": {"name": "Netherlands",     "flag": "🇳🇱", "continent": "Europe"},
    "GR": {"name": "Greece",          "flag": "🇬🇷", "continent": "Europe"},
    "CH": {"name": "Switzerland",     "flag": "🇨🇭", "continent": "Europe"},
    "AT": {"name": "Austria",         "flag": "🇦🇹", "continent": "Europe"},
    "BE": {"name": "Belgium",         "flag": "🇧🇪", "continent": "Europe"},
    "IE": {"name": "Ireland",         "flag": "🇮🇪", "continent": "Europe"},
    "CZ": {"name": "Czech Republic",  "flag": "🇨🇿", "continent": "Europe"},
    "HR": {"name": "Croatia",         "flag": "🇭🇷", "continent": "Europe"},
    "IS": {"name": "Iceland",         "flag": "🇮🇸", "continent": "Europe"},
    "NO": {"name": "Norway",          "flag": "🇳🇴", "continent": "Europe"},
    "SE": {"name": "Sweden",          "flag": "🇸🇪", "continent": "Europe"},
    "FI": {"name": "Finland",         "flag": "🇫🇮", "continent": "Europe"},
    "PL": {"name": "Poland",          "flag": "🇵🇱", "continent": "Europe"},
    # ── North & Central America ──
    "US": {"name": "United States",   "flag": "🇺🇸", "continent": "North America"},
    "CA": {"name": "Canada",          "flag": "🇨🇦", "continent": "North America"},
    "MX": {"name": "Mexico",          "flag": "🇲🇽", "continent": "North America"},
    "CR": {"name": "Costa Rica",      "flag": "🇨🇷", "continent": "North America"},
    "CU": {"name": "Cuba",            "flag": "🇨🇺", "continent": "North America"},
    "DO": {"name": "Dominican Rep.",  "flag": "🇩🇴", "continent": "North America"},
    # ── South America ──
    "BR": {"name": "Brazil",          "flag": "🇧🇷", "continent": "South America"},
    "AR": {"name": "Argentina",       "flag": "🇦🇷", "continent": "South America"},
    "PE": {"name": "Peru",            "flag": "🇵🇪", "continent": "South America"},
    "CO": {"name": "Colombia",        "flag": "🇨🇴", "continent": "South America"},
    "CL": {"name": "Chile",           "flag": "🇨🇱", "continent": "South America"},
    # ── Asia ──
    "JP": {"name": "Japan",           "flag": "🇯🇵", "continent": "Asia"},
    "CN": {"name": "China",           "flag": "🇨🇳", "continent": "Asia"},
    "KR": {"name": "South Korea",     "flag": "🇰🇷", "continent": "Asia"},
    "TH": {"name": "Thailand",        "flag": "🇹🇭", "continent": "Asia"},
    "VN": {"name": "Vietnam",         "flag": "🇻🇳", "continent": "Asia"},
    "ID": {"name": "Indonesia",       "flag": "🇮🇩", "continent": "Asia"},
    "IN": {"name": "India",           "flag": "🇮🇳", "continent": "Asia"},
    "AE": {"name": "UAE",             "flag": "🇦🇪", "continent": "Asia"},
    "TR": {"name": "Turkey",          "flag": "🇹🇷", "continent": "Asia"},
    "PH": {"name": "Philippines",     "flag": "🇵🇭", "continent": "Asia"},
    # ── Africa ──
    "ZA": {"name": "South Africa",    "flag": "🇿🇦", "continent": "Africa"},
    "EG": {"name": "Egypt",           "flag": "🇪🇬", "continent": "Africa"},
    "MA": {"name": "Morocco",         "flag": "🇲🇦", "continent": "Africa"},
    "KE": {"name": "Kenya",           "flag": "🇰🇪", "continent": "Africa"},
    "TZ": {"name": "Tanzania",        "flag": "🇹🇿", "continent": "Africa"},
    # ── Oceania ──
    "AU": {"name": "Australia",       "flag": "🇦🇺", "continent": "Oceania"},
    "NZ": {"name": "New Zealand",     "flag": "🇳🇿", "continent": "Oceania"},
    "FJ": {"name": "Fiji",            "flag": "🇫🇯", "continent": "Oceania"},
}

DEFAULT_COUNTRY = "ES"  # All 3 users live in Madrid

def get_country_options() -> list[str]:
    """Returns formatted list for st.selectbox: ['🇪🇸 Spain', '🇫🇷 France', ...]"""
    return [f"{c['flag']} {c['name']}" for c in TRAVEL_COUNTRIES.values()]

def get_country_code_from_option(option: str) -> str:
    """Reverse-lookup: '🇪🇸 Spain' → 'ES'"""
    for code, info in TRAVEL_COUNTRIES.items():
        if f"{info['flag']} {info['name']}" == option:
            return code
    return DEFAULT_COUNTRY

def get_option_from_code(code: str) -> str:
    """Forward-lookup: 'ES' → '🇪🇸 Spain'"""
    info = TRAVEL_COUNTRIES.get(code, TRAVEL_COUNTRIES[DEFAULT_COUNTRY])
    return f"{info['flag']} {info['name']}"

def compute_passport_stats(transactions: list[dict], user: str, default_country: str) -> dict:
    """Compute travel passport statistics from coin_transactions."""
    countries_visited = set()
    continents_reached = set()
    drinks_abroad = 0
    total_logged_with_country = 0
    country_counts = {}

    for tx in transactions:
        if tx.get("user_name") == user and tx.get("transaction_type") == "drink_log":
            meta = tx.get("metadata", {})
            country_code = meta.get("country")
            if country_code and country_code in TRAVEL_COUNTRIES:
                total_logged_with_country += 1
                countries_visited.add(country_code)
                continents_reached.add(TRAVEL_COUNTRIES[country_code]["continent"])
                
                if country_code != default_country:
                    drinks_abroad += 1
                
                country_counts[country_code] = country_counts.get(country_code, 0) + 1

    most_visited_foreign = None
    if country_counts:
        foreign_counts = {k: v for k, v in country_counts.items() if k != default_country}
        if foreign_counts:
            most_visited_code = max(foreign_counts, key=foreign_counts.get)
            most_visited_foreign = (most_visited_code, foreign_counts[most_visited_code])

    diversity_score = (len(countries_visited) / len(TRAVEL_COUNTRIES)) * 100 if TRAVEL_COUNTRIES else 0

    return {
        "countries_visited": countries_visited,
        "continents_reached": continents_reached,
        "drinks_abroad": drinks_abroad,
        "total_logged_with_country": total_logged_with_country,
        "most_visited_foreign": most_visited_foreign,
        "country_counts": country_counts,
        "diversity_score": diversity_score
    }

def get_travel_leaderboard(transactions: list[dict], users: list[str]) -> list[dict]:
    """Returns sorted list of travel stats for leaderboard."""
    leaderboard = []
    
    # Needs preferences to get default_country for each user
    from data_processing import get_user_preferences
    prefs = get_user_preferences(transactions, users)
    
    for u in users:
        u_def = prefs.get(u, {}).get("default_country", DEFAULT_COUNTRY)
        stats = compute_passport_stats(transactions, u, u_def)
        leaderboard.append({
            "user": u,
            "countries": len(stats["countries_visited"]),
            "continents": len(stats["continents_reached"]),
            "diversity": stats["diversity_score"]
        })
        
    leaderboard.sort(key=lambda x: (x["countries"], x["continents"]), reverse=True)
    return leaderboard
```

---

## Step 3: Modify `0_Coffee_is_my_best_friend_：).py` (Landing Page)

**File Path:** `\\wsl.localhost\Ubuntu-26.04\home\matis-ubuntu\bin\coffee-is-my-best-friend\0_Coffee_is_my_best_friend_：).py`

### 3.1 Import world_data
At the top of the file, around line 17, add the import:

**BEFORE:**
```python
from utils import enforce_user_identity
```
**AFTER:**
```python
from utils import enforce_user_identity
from world_data import get_country_options, get_option_from_code, get_country_code_from_option
```

### 3.2 Update `handle_drink_log`
Modify the `handle_drink_log` function to accept the `country` argument.

**BEFORE:**
```python
def handle_drink_log(drink_id, drink_name, temp_name):
    if last_click_time and (now - last_click_time).total_seconds() < 60:
        st.warning(f"Wait {int(60 - (now - last_click_time).total_seconds())}s before logging again!")
        return
    try:
        # 1. Insert Click Record (1: Hot Coffee, 3: Iced Coffee, 2: Hot Tea, 4: Iced Tea)
        insert_click(selected_user, 1, drink_id)
        # 2. Insert Coin Transaction with explicit temperature metadata
        insert_transaction(
            selected_user, 
            10, 
            "drink_log", 
            {"drink": drink_name.lower(), "temperature": temp_name.lower(), "drink_id": drink_id}
        )
```

**AFTER:**
```python
def handle_drink_log(drink_id, drink_name, temp_name, country_code):
    if last_click_time and (now - last_click_time).total_seconds() < 60:
        st.warning(f"Wait {int(60 - (now - last_click_time).total_seconds())}s before logging again!")
        return
    try:
        # 1. Insert Click Record (1: Hot Coffee, 3: Iced Coffee, 2: Hot Tea, 4: Iced Tea)
        insert_click(selected_user, 1, drink_id)
        # 2. Insert Coin Transaction with explicit temperature metadata
        insert_transaction(
            selected_user, 
            10, 
            "drink_log", 
            {
                "drink": drink_name.lower(), 
                "temperature": temp_name.lower(), 
                "drink_id": drink_id,
                "country": country_code
            }
        )
```

### 3.3 Update the UI for Country Selection
Modify the buttons area. Add the `st.selectbox` before the columns and update the `handle_drink_log` calls.

**BEFORE:**
```python
# --- 2. Hero Quick-Tap Beverage Section (Coffee & Tea - Hot & Iced) ---
st.subheader("⚡ Log Your Beverage")

if "coffee_break" in active_perks.get(selected_user, []):
    st.error("🚫 You are on a mandatory Coffee Break! You cannot log drinks right now.")
else:
    b_col1, b_col2 = st.columns(2)
    
    # ☕ COFFEE ZONE
    with b_col1:
        with st.container(border=True):
            st.markdown("### ☕ Coffee Section")
            st.caption("Rich roast &bull; **95mg** Caffeine &bull; 🪙 `+10 Coins`")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("☕ Hot Coffee", key="btn_hot_coffee", use_container_width=True):
                    handle_drink_log(1, "Coffee", "Hot")
            with c_btn2:
                if st.button("🧊 Iced Coffee", key="btn_iced_coffee", use_container_width=True):
                    handle_drink_log(3, "Coffee", "Iced")
                    
    # 🍵 TEA ZONE
    with b_col2:
        with st.container(border=True):
            st.markdown("### 🍵 Tea Section")
            st.caption("Fresh steep &bull; **35mg** Caffeine &bull; 🪙 `+10 Coins`")
            
            t_btn1, t_btn2 = st.columns(2)
            with t_btn1:
                if st.button("🍵 Hot Tea", key="btn_hot_tea", use_container_width=True):
                    handle_drink_log(2, "Tea", "Hot")
            with t_btn2:
                if st.button("🧊 Iced Tea", key="btn_iced_tea", use_container_width=True):
                    handle_drink_log(4, "Tea", "Iced")
```

**AFTER:**
```python
# --- 2. Hero Quick-Tap Beverage Section (Coffee & Tea - Hot & Iced) ---
st.subheader("⚡ Log Your Beverage")

if "coffee_break" in active_perks.get(selected_user, []):
    st.error("🚫 You are on a mandatory Coffee Break! You cannot log drinks right now.")
else:
    # --- COUNTRY SELECTOR ---
    default_country_code = prefs.get(selected_user, {}).get("default_country", "ES")
    default_option = get_option_from_code(default_country_code)
    all_options = get_country_options()
    
    selected_option = st.selectbox(
        "📍 Drinking in:",
        all_options,
        index=all_options.index(default_option) if default_option in all_options else 0
    )
    selected_country_code = get_country_code_from_option(selected_option)

    b_col1, b_col2 = st.columns(2)
    
    # ☕ COFFEE ZONE
    with b_col1:
        with st.container(border=True):
            st.markdown("### ☕ Coffee Section")
            st.caption("Rich roast &bull; **95mg** Caffeine &bull; 🪙 `+10 Coins`")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("☕ Hot Coffee", key="btn_hot_coffee", use_container_width=True):
                    handle_drink_log(1, "Coffee", "Hot", selected_country_code)
            with c_btn2:
                if st.button("🧊 Iced Coffee", key="btn_iced_coffee", use_container_width=True):
                    handle_drink_log(3, "Coffee", "Iced", selected_country_code)
                    
    # 🍵 TEA ZONE
    with b_col2:
        with st.container(border=True):
            st.markdown("### 🍵 Tea Section")
            st.caption("Fresh steep &bull; **35mg** Caffeine &bull; 🪙 `+10 Coins`")
            
            t_btn1, t_btn2 = st.columns(2)
            with t_btn1:
                if st.button("🍵 Hot Tea", key="btn_hot_tea", use_container_width=True):
                    handle_drink_log(2, "Tea", "Hot", selected_country_code)
            with t_btn2:
                if st.button("🧊 Iced Tea", key="btn_iced_tea", use_container_width=True):
                    handle_drink_log(4, "Tea", "Iced", selected_country_code)
```

---

## Step 4: Modify `pages/99_⚙️_Settings.py` (Settings Page)

**File Path:** `\\wsl.localhost\Ubuntu-26.04\home\matis-ubuntu\bin\coffee-is-my-best-friend\pages\99_⚙️_Settings.py`

### 4.1 Import world_data
At the top of the file, add:
```python
from world_data import get_country_options, get_option_from_code, get_country_code_from_option
```

### 4.2 Add Home Base Country Section
Around line 133, after the Profile & Badges section ends:

**BEFORE:**
```python
    if st.button("Save Profile Settings", use_container_width=True):
        insert_transaction(selected_user, 0, "preference", {"emoji": emoji, "title": selected_title})
        st.success("Profile saved! Refreshing...")
        st.rerun()

st.header("🎒 Active Inventory & Perks")
```

**AFTER:**
```python
    if st.button("Save Profile Settings", use_container_width=True):
        insert_transaction(selected_user, 0, "preference", {"emoji": emoji, "title": selected_title})
        st.success("Profile saved! Refreshing...")
        st.rerun()

st.header("🌍 Location Settings")
with st.container(border=True):
    st.markdown("### 🌍 Home Base Country")
    st.caption("Your default location for drinks.")
    
    default_country_code = prefs.get(selected_user, {}).get("default_country", "ES")
    default_option = get_option_from_code(default_country_code)
    all_options = get_country_options()
    
    selected_option = st.selectbox(
        "Default Country",
        all_options,
        index=all_options.index(default_option) if default_option in all_options else 0
    )
    
    if st.button("💾 Save Location", use_container_width=True):
        new_country_code = get_country_code_from_option(selected_option)
        insert_transaction(selected_user, 0, "preference", {"default_country": new_country_code})
        st.success("Location saved! Refreshing...")
        st.rerun()

st.header("🎒 Active Inventory & Perks")
```

---

## Step 5: Modify `data_processing.py`

**File Path:** `\\wsl.localhost\Ubuntu-26.04\home\matis-ubuntu\bin\coffee-is-my-best-friend\data_processing.py`

### 5.1 Add Import at top of file
Add `from world_data import TRAVEL_COUNTRIES, DEFAULT_COUNTRY, compute_passport_stats` near the imports at the top of the file.

### 5.2 Parse `default_country` preference
Locate the `get_user_preferences` function. Modify the preferences parser.

**BEFORE:**
```python
def get_user_preferences(transactions, users):
    prefs = {u: {"theme": "Latte (Light)", "emoji": "☕", "title": None, "ui_style": "Modern Flat"} for u in users}
    
    if not transactions:
        return prefs
        
    tx_df = pd.DataFrame(transactions)
    if tx_df.empty or "transaction_type" not in tx_df.columns:
        return prefs
        
    pref_txs = tx_df[tx_df["transaction_type"] == "preference"]
    if pref_txs.empty:
        return prefs
        
    for _, row in pref_txs.iterrows():
        u = row.get("user_name")
        meta = row.get("metadata", {})
        if u in prefs and isinstance(meta, dict):
            if "theme" in meta:
                prefs[u]["theme"] = meta["theme"]
            if "emoji" in meta:
                prefs[u]["emoji"] = meta["emoji"]
            if "title" in meta:
                prefs[u]["title"] = meta["title"]
            if "ui_style" in meta:
                prefs[u]["ui_style"] = meta["ui_style"]
                
    return prefs
```

**AFTER:**
```python
def get_user_preferences(transactions, users):
    prefs = {u: {"theme": "Latte (Light)", "emoji": "☕", "title": None, "ui_style": "Modern Flat", "default_country": "ES"} for u in users}
    
    if not transactions:
        return prefs
        
    tx_df = pd.DataFrame(transactions)
    if tx_df.empty or "transaction_type" not in tx_df.columns:
        return prefs
        
    pref_txs = tx_df[tx_df["transaction_type"] == "preference"]
    if pref_txs.empty:
        return prefs
        
    for _, row in pref_txs.iterrows():
        u = row.get("user_name")
        meta = row.get("metadata", {})
        if u in prefs and isinstance(meta, dict):
            if "theme" in meta:
                prefs[u]["theme"] = meta["theme"]
            if "emoji" in meta:
                prefs[u]["emoji"] = meta["emoji"]
            if "title" in meta:
                prefs[u]["title"] = meta["title"]
            if "ui_style" in meta:
                prefs[u]["ui_style"] = meta["ui_style"]
            if "default_country" in meta:
                prefs[u]["default_country"] = meta["default_country"]
                
    return prefs
```

### 5.3 Add World Explorer Achievement
In the `ACHIEVEMENT_TIERS` dictionary:

**BEFORE:**
```python
    "combustion": {
        "title": "🔥 Combustion Overclock",
        "icon": "🔥",
        "desc": "Days where daily caffeine velocity reached >= 400 mg (On-Fire state).",
        "tiers": [
            {"level": "Bronze", "name": "Ignition Spark", "target": 1},
            {"level": "Silver", "name": "Flamethrower", "target": 5},
            {"level": "Gold", "name": "Inferno Beast", "target": 15},
            {"level": "Diamond", "name": "Combustion Monarch", "target": 35},
        ]
    }
}
```

**AFTER:**
```python
    "combustion": {
        "title": "🔥 Combustion Overclock",
        "icon": "🔥",
        "desc": "Days where daily caffeine velocity reached >= 400 mg (On-Fire state).",
        "tiers": [
            {"level": "Bronze", "name": "Ignition Spark", "target": 1},
            {"level": "Silver", "name": "Flamethrower", "target": 5},
            {"level": "Gold", "name": "Inferno Beast", "target": 15},
            {"level": "Diamond", "name": "Combustion Monarch", "target": 35},
        ]
    },
    "world_explorer": {
        "title": "🌍 World Explorer",
        "icon": "🌍",
        "desc": "Visit different countries and expand your passport.",
        "tiers": [
            {"level": "Bronze",  "name": "🗺️ First Stamp",       "target": 1},
            {"level": "Silver",  "name": "✈️ Frequent Flyer",     "target": 3},
            {"level": "Gold",    "name": "🌎 Globe Trotter",      "target": 8},
            {"level": "Diamond", "name": "🗺️ World Traveler",     "target": 15},
            {"level": "Master",  "name": "👑 Nomad Supreme",      "target": 25},
        ]
    }
}
```

### 5.4 Add Secret Feats
In the `SECRET_FEATS` list:

**BEFORE:**
```python
    {
        "id": "chromatic_sovereign",
        "title": "🌈 The Chromatic Sovereign",
        "desc": "Unlocked all 8 handcrafted aesthetic palettes in the Theme Boutique to attain complete stylistic supremacy.",
        "hint": "Don every cloak, gown, and armor tailored by the masters of bean and leaf..."
    }
]
```

**AFTER:**
```python
    {
        "id": "chromatic_sovereign",
        "title": "🌈 The Chromatic Sovereign",
        "desc": "Unlocked all 8 handcrafted aesthetic palettes in the Theme Boutique to attain complete stylistic supremacy.",
        "hint": "Don every cloak, gown, and armor tailored by the masters of bean and leaf..."
    },
    {
        "id": "continent_hopper",
        "title": "🌏 Continent Hopper",
        "desc": "Log drinks in 3+ different continents.",
        "hint": "One cup per landmass. The equator is just a suggestion."
    },
    {
        "id": "jet_lagged",
        "title": "✈️ Jet Lagged",
        "desc": "Log drinks in 2 different countries within 24 hours.",
        "hint": "Two flags in 24 hours. Where did you wake up?"
    },
    {
        "id": "homebody",
        "title": "🏠 The Homebody",
        "desc": "Log 100 consecutive drinks in your default country.",
        "hint": "100 cups and never left the zip code."
    }
]
```

### 5.5 Compute New Metrics
In `get_gamification_metrics`, inside the `for user in users:` loop:

**BEFORE:**
```python
        u_streak = trophies["streaks"].get(user, 0)

        user_counts = {
            "total": u_total,
            "coffee": u_coffee,
            "tea": u_tea,
            "iced": u_iced,
            "streak": u_streak,
            "active_days": u_active_days,
            "early": u_early,
            "night": u_night,
            "surge": u_surge,
            "weekend": u_weekend,
            "combustion": u_on_fire_days
        }
```

**AFTER:**
```python
        u_streak = trophies["streaks"].get(user, 0)

        # Drop 1 Travel Stats
        prefs_for_user = get_user_preferences(transactions, [user]).get(user, {})
        u_def_country = prefs_for_user.get("default_country", "ES")
        passport = compute_passport_stats(transactions or [], user, u_def_country)
        u_unique_foreign_countries = len([c for c in passport["countries_visited"] if c != u_def_country])

        user_counts = {
            "total": u_total,
            "coffee": u_coffee,
            "tea": u_tea,
            "iced": u_iced,
            "streak": u_streak,
            "active_days": u_active_days,
            "early": u_early,
            "night": u_night,
            "surge": u_surge,
            "weekend": u_weekend,
            "combustion": u_on_fire_days,
            "world_explorer": u_unique_foreign_countries
        }
```

Further down in `get_gamification_metrics`, add the secret feat checks:

**BEFORE:**
```python
        # 11. The Chromatic Sovereign (Unlocked all 8 themes in Theme Shop)
        unlocked_set = set(get_unlocked_themes(transactions, user)) if transactions else set(BASE_THEMES)
        chromatic_unlocked = bool(len(unlocked_set) >= len(ALL_VALID_THEMES))
```

**AFTER:**
```python
        # 11. The Chromatic Sovereign (Unlocked all 8 themes in Theme Shop)
        unlocked_set = set(get_unlocked_themes(transactions, user)) if transactions else set(BASE_THEMES)
        chromatic_unlocked = bool(len(unlocked_set) >= len(ALL_VALID_THEMES))

        # Drop 1 Secret Feats
        continent_hopper_unlocked = len(passport["continents_reached"]) >= 3
        
        jet_lagged_unlocked = False
        homebody_unlocked = False
        max_consecutive_default_country = 0
        current_consecutive_default = 0
        
        if transactions:
            user_txs = [tx for tx in transactions if tx.get("user_name") == user and tx.get("transaction_type") == "drink_log"]
            user_txs.sort(key=lambda x: pd.to_datetime(x["created_at"]))
            
            for i in range(len(user_txs)):
                tx = user_txs[i]
                c_code = tx.get("metadata", {}).get("country", "ES")
                if c_code == u_def_country:
                    current_consecutive_default += 1
                    max_consecutive_default_country = max(max_consecutive_default_country, current_consecutive_default)
                else:
                    current_consecutive_default = 0
                    
                if i > 0:
                    prev_tx = user_txs[i-1]
                    prev_code = prev_tx.get("metadata", {}).get("country", "ES")
                    if c_code != prev_code:
                        time_diff = pd.to_datetime(tx["created_at"]) - pd.to_datetime(prev_tx["created_at"])
                        if time_diff.total_seconds() <= 86400:
                            jet_lagged_unlocked = True
                            
        homebody_unlocked = max_consecutive_default_country >= 100
```

And save them to the `user_secrets` dict:

**BEFORE:**
```python
        user_secrets["thermal_sandwich"] = sandwich_unlocked
        user_secrets["chromatic_sovereign"] = chromatic_unlocked

        trophies["secret_feats"][user] = user_secrets
```

**AFTER:**
```python
        user_secrets["thermal_sandwich"] = sandwich_unlocked
        user_secrets["chromatic_sovereign"] = chromatic_unlocked
        user_secrets["continent_hopper"] = continent_hopper_unlocked
        user_secrets["jet_lagged"] = jet_lagged_unlocked
        user_secrets["homebody"] = homebody_unlocked

        trophies["secret_feats"][user] = user_secrets
```

---

## Step 6: Create `pages/4_🌍_World_Explorer.py`

Create a new file at: `\\wsl.localhost\Ubuntu-26.04\home\matis-ubuntu\bin\coffee-is-my-best-friend\pages\4_🌍_World_Explorer.py`

```python
import streamlit as st
import pandas as pd
from feature_flags import is_unlocked, is_dev_mode, get_countdown_text
from world_data import compute_passport_stats, get_travel_leaderboard, TRAVEL_COUNTRIES, get_option_from_code
from database import get_transactions
from data_processing import get_user_preferences
from utils import enforce_user_identity
from components.ui import inject_custom_css

st.set_page_config(page_title="World Explorer", page_icon="🌍", layout="wide")

if not is_unlocked("world_update", dev_bypass=is_dev_mode()):
    st.markdown(f"### {get_countdown_text('world_update')}")
    st.info("The World Update hasn't been unlocked yet!")
    st.stop()

users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

transactions = get_transactions()
prefs = get_user_preferences(transactions, users)

user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")
inject_custom_css(user_theme, user_style)

default_country = prefs.get(selected_user, {}).get("default_country", "ES")
passport = compute_passport_stats(transactions, selected_user, default_country)

st.title(f"🌍 World Explorer — {selected_user}'s Passport")

# Interactive map placeholder
st.markdown("### 🗺️ Visited Countries Map")
try:
    import folium
    from streamlit_folium import st_folium
    m = folium.Map(location=[20, 0], zoom_start=2)
    # Highlight visited countries
    for code in passport["countries_visited"]:
        if code in TRAVEL_COUNTRIES:
            c = TRAVEL_COUNTRIES[code]
            folium.Marker(
                location=[0, 0], # Note: Real coordinates per country would be needed for a precise map
                popup=f"{c['flag']} {c['name']}: {passport['country_counts'][code]} drinks",
                icon=folium.Icon(color="red" if code != default_country else "blue")
            ).add_to(m)
    st_folium(m, width=1200, height=400)
except ImportError:
    st.info("Map unavailable. Please install `folium` and `streamlit-folium`.")

st.markdown("### 🛂 Passport Stats")
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.metric("🗺️ Countries Visited", f"{len(passport['countries_visited'])} / {len(TRAVEL_COUNTRIES)}")
with c2:
    with st.container(border=True):
        st.metric("🌎 Continents Reached", f"{len(passport['continents_reached'])} / 6")
with c3:
    with st.container(border=True):
        st.metric("✈️ Drinks Abroad", passport["drinks_abroad"])

c4, c5 = st.columns(2)
with c4:
    with st.container(border=True):
        mvf = passport["most_visited_foreign"]
        if mvf:
            c_name = get_option_from_code(mvf[0])
            st.metric("🏆 Most Visited Foreign Country", f"{c_name}", f"{mvf[1]} drinks")
        else:
            st.metric("🏆 Most Visited Foreign Country", "None Yet", "0 drinks")
with c5:
    with st.container(border=True):
        st.metric("📊 Diversity Score", f"{passport['diversity_score']:.1f}%")

st.markdown("### 🏆 Travel Leaderboard")
leaderboard = get_travel_leaderboard(transactions, users)

lb_df = pd.DataFrame(leaderboard)
lb_df.index = lb_df.index + 1
lb_df = lb_df.rename(columns={
    "user": "User",
    "countries": "🗺️ Countries",
    "continents": "🌎 Continents",
    "diversity": "📊 Diversity Score (%)"
})

st.dataframe(lb_df, use_container_width=True)
```

---

## Step 7: Update `requirements.txt`
Add `folium>=0.16.0` and `streamlit-folium>=0.20` to the project's `requirements.txt` file so the map renders properly. Ensure `feature_flags.py` runs by testing with the `?dev=1` url query parameter.
