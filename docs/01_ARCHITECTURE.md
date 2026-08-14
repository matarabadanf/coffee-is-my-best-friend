# Cross-Cutting Architecture — Shared Systems Reference

> **Purpose**: This document provides full code for the feature flags engine, the file structure map, and cross-cutting systems like economy and achievements.

---

## 1. Feature Flags Engine (`feature_flags.py`) [NEW FILE]

Create this file in the root directory. This is the **COMPLETE CODE**. Do not write a stub.

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
    """Check if a feature is unlocked based on date and timezone."""
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
    """Check if current user has dev privileges."""
    from utils import is_pin_verified
    return (st.query_params.get("dev") == "1" or
            is_pin_verified(st.session_state.get("user", "")))
```

### Page Guard Pattern

When creating a new page for a specific drop (e.g., `pages/5_⚔️_Quest_Board.py`), use this pattern at the VERY TOP of the file to prevent access before unlock:

```python
import streamlit as st
from feature_flags import is_unlocked, is_dev_mode, get_countdown_text

# Guard pattern
if not is_unlocked("rpg_quests", dev_bypass=is_dev_mode()):
    st.markdown(f"### {get_countdown_text('rpg_quests')}")
    st.info("This feature hasn't been unlocked yet!")
    st.stop()
    
# Rest of the page code...
```

---

## 2. Complete File Structure Map (After All Drops)

```text
coffee-is-my-best-friend/
├── 0_Coffee_is_my_best_friend_：).py    # Landing (MODIFY: country selector, quest widget)
├── database.py                          # Supabase CRUD (MODIFY: new table functions)
├── data_processing.py                   # Metrics (MODIFY: new achievements + feats)
├── utils.py                             # Auth helpers (UNCHANGED)
├── requirements.txt                     # Dependencies (MODIFY: add folium, Pillow, streamlit-folium)
│
├── # ─── NEW: Core Engines ───
├── feature_flags.py                     # [NEW] Autonomous rollout controller
├── world_data.py                        # [NEW] TRAVEL_COUNTRIES, passport helpers
├── rpg_data.py                          # [NEW] HERO_CLASSES, BESTIARY, LOOT_TABLE, XP curve
├── rpg_engine.py                        # [NEW] Quest resolution, caffeine calc, loot rolls
├── gacha_engine.py                      # [NEW] Banner config, pull mechanics, pity system
├── raid_engine.py                       # [NEW] Boss raid logic, damage calc
├── wrapped_engine.py                    # [NEW] Wrapped metrics, personality algorithm
│
├── components/
│   ├── ui.py                            # CSS & components (MODIFY: new widgets)
│   └── charts.py                        # Charts (MODIFY: origin/travel charts)
│
├── pages/
│   ├── 1_📈_Graphs!_Graphs!_Graphs!.py  # (MODIFY: Tab 5 Travel Analytics)
│   ├── 2_🏆_Trophy_Room.py              # (MODIFY: new achievement tracks)
│   ├── 3_🎨_Theme_Shop.py               # (UNCHANGED)
│   ├── 4_🌍_World_Explorer.py           # [NEW] Travel map & passport (Drop 1)
│   ├── 5_⚔️_Quest_Board.py              # [NEW] Quest selection & tracker (Drop 2)
│   ├── 6_🎒_Hero_Inventory.py           # [NEW] Hero stats, gear, skills (Drop 2+3)
│   ├── 7_🎰_Gacha.py                    # [NEW] Gacha banner pulls (Drop 3)
│   ├── 8_🐉_Boss_Raids.py               # [NEW] Cooperative boss raids (Drop 3)
│   ├── 10_🎁_Wrapped.py                 # [NEW] Coffee Wrapped 2026 (Drop 4)
│   └── 99_⚙️_Settings.py               # (MODIFY: default country, class display)
```

---

## 3. Unified Coin Economy Balance Sheet

### Earning
| Source | Coins | Drop |
|---|---|---|
| Drink Log | +10 | Core |
| Easy Quest | +5-12 | Drop 2 |
| Medium Quest | +25-50 | Drop 2 |
| Hard Quest | +80-150 | Drop 2 |
| Legendary Quest | +300-500 | Drop 2 |
| Item Sell | +5-500 (by rarity/level) | Drop 2 |
| Boss Raid Victory | +500-1000 | Drop 3 |

### Spending
| Sink | Cost | Drop |
|---|---|---|
| Theme Shop | 20-1050 | Core |
| Single Gacha Pull | 50 | Drop 3 |
| 10x Multi-Pull | 450 | Drop 3 |

**Balance Check**: ~150-200 coins/day active. 10x gacha = ~3 days of play.

---

## 4. Achievement Totals (All Drops)

### Tracks: 14 total
| # | Track | Tiers |
|---|---|---|
| 1-11 | Original mastery tracks | 4 tiers each |
| 12 | 🌍 World Explorer | 5 tiers |
| 13 | ⚔️ Quest Warrior | 5 tiers |
| 14 | 🎰 Gacha Collector | 5 tiers |

### Secret Feats: 28 total
| # | Feats | Drop |
|---|---|---|
| 1-11 | Original secret feats | Core |
| 12-14 | Continent Hopper, Jet Lagged, Homebody | Drop 1 |
| 15-20 | Cardiac Casualty, Triple Cardiac, Zen Warrior, Chosen One, Speed Demon, Born Again | Drop 2 |
| 21-25 | Pity Party, Beginner's Luck, Party Carry, Fellowship, Monster Hunter | Drop 3 |
| 26-28 | Unwrapped, Show Off, Complete Journey | Drop 4 |

---

## 5. Required New Dependencies

Modify `requirements.txt` to include these exact versions (or higher):

```text
folium>=0.16.0
streamlit-folium>=0.20
Pillow>=10.0.0
```

---

## 6. Key Design Rules (From User Feedback)

> [!IMPORTANT]
> These rules are **non-negotiable** and must be respected across all drops:

| Rule | Details |
|---|---|
| **Travel, not origin** | Drop 1 country = where the USER is, not where the coffee bean comes from |
| **One-time class pick** | Hero class chosen ONCE for free at RPG first-unlock. Reclass only via rare quest drop item |
| **No multi-questing** | ONE active quest at a time per user. No skills or mechanics that bypass this |
| **Leveled items** | Items have Lv.1-5 (Drop 2, quest loot) and Lv.6-10 (Drop 3, gacha/raid exclusive) |
| **Level cap 50 → 100** | Drop 2 caps at 50, Drop 3 raises to 100 |
| **Wrapped = 2026 only** | All Wrapped queries filtered to Jan 1 - Oct 31, 2026 |
