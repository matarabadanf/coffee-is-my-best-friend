# Drop 3 — 🎰 Gacha & Boss Raids Implementation Specification

This document provides step-by-step, exact code implementations for Drop 3.

## Step 1: Update `rpg_data.py`
Change the maximum level and add the extended XP curve, and the skill tree data structures.

```python
# In rpg_data.py, replace MAX_LEVEL and xp_for_level:

MAX_LEVEL = 100

def xp_for_level(level: int) -> int:
    """Total cumulative XP required to reach a given level."""
    if level <= 1:
        return 0
    if level <= 50:
        return int(100 * (level - 1) ** 1.5)
    # Steeper curve for 51-100
    xp_at_50 = int(100 * 49 ** 1.5)
    return xp_at_50 + int(200 * (level - 50) ** 2.0)

# Add Skill Trees
SKILL_TREES = {
    "Caffeinated Warrior": {
        "Fury": {
            "berserker_brew": {"name": "Berserker Brew", "desc": "+5% ATK per caffeinated drink today (max +25%)", "cost": 1},
            "caffeine_rage": {"name": "Caffeine Rage", "desc": "+10% ATK when caffeine > 300mg", "cost": 1},
            "espresso_onslaught": {"name": "Espresso Onslaught", "desc": "15% chance to earn double gold from quests", "cost": 1},
        },
        "Iron": {
            "thick_skin": {"name": "Thick Skin", "desc": "+5 flat DEF", "cost": 1},
            "fortified_stomach": {"name": "Fortified Stomach", "desc": "Heart attack threshold raised additional 50mg", "cost": 1},
            "unbreakable": {"name": "Unbreakable", "desc": "Survive one heart attack per day (recovery reduced to 30 min)", "cost": 1},
        },
        "Fortune": {
            "lucky_find": {"name": "Lucky Find", "desc": "+5% loot drop chance", "cost": 1},
            "treasure_hunter": {"name": "Treasure Hunter", "desc": "+10% chance to upgrade loot rarity", "cost": 1},
            "midas_brew": {"name": "Midas Brew", "desc": "+25% gold from quests", "cost": 1},
        }
    },
    "Tea Sage": {
        "Wisdom": {
            "sages_focus": {"name": "Sage's Focus", "desc": "+10% XP", "cost": 1},
            "enlightened_mind": {"name": "Enlightened Mind", "desc": "+15% XP from quests", "cost": 1},
            "transcendence": {"name": "Transcendence", "desc": "Gain 50% XP even from failed quests", "cost": 1},
        },
        "Serenity": {
            "calm_heart": {"name": "Calm Heart", "desc": "Heart attack threshold raised by 100mg", "cost": 1},
            "inner_peace": {"name": "Inner Peace", "desc": "Recovery time halved (1 hr instead of 2)", "cost": 1},
            "zen_master": {"name": "Zen Master", "desc": "Heart attacks impossible below 600mg", "cost": 1},
        },
        "Mystic": {
            "arcane_luck": {"name": "Arcane Luck", "desc": "+8% bonus pity progress per gacha pull", "cost": 1},
            "star_reader": {"name": "Star Reader", "desc": "Gacha guarantees Rare+ every 7 pulls (instead of 10)", "cost": 1},
            "cosmic_alignment": {"name": "Cosmic Alignment", "desc": "One free 10x gacha pull per week", "cost": 1},
        }
    },
    "Iced Assassin": {
        "Shadow": {
            "quick_strike": {"name": "Quick Strike", "desc": "+10% SPD", "cost": 1},
            "ambush": {"name": "Ambush", "desc": "First quest of the day completes 30% faster", "cost": 1},
            "time_warp": {"name": "Time Warp", "desc": "10% chance quest completes instantly", "cost": 1},
        },
        "Precision": {
            "critical_eye": {"name": "Critical Eye", "desc": "15% chance for critical loot (guaranteed rarity upgrade)", "cost": 1},
            "weak_spot": {"name": "Weak Spot", "desc": "+10 ATK vs. Legendary monsters", "cost": 1},
            "executioner": {"name": "Executioner", "desc": "Quests against Easy monsters always drop loot", "cost": 1},
        },
        "Stealth": {
            "evasion": {"name": "Evasion", "desc": "10% chance to avoid heart attack trigger", "cost": 1},
            "ghost_walk": {"name": "Ghost Walk", "desc": "Heart attack recovery time reduced to 30 min", "cost": 1},
            "phantom_blade": {"name": "Phantom Blade", "desc": "Double loot chance from Legendary quests", "cost": 1},
        }
    },
    "Frost Ranger": {
        "Scout": {
            "pathfinder": {"name": "Pathfinder", "desc": "-5% quest duration", "cost": 1},
            "trailblazer": {"name": "Trailblazer", "desc": "-10% quest duration", "cost": 1},
            "cartographer": {"name": "Cartographer", "desc": "Unlock hidden quest variants with +50% gold bonus", "cost": 1},
        },
        "Survival": {
            "thick_hide": {"name": "Thick Hide", "desc": "+20 max HP", "cost": 1},
            "iron_will": {"name": "Iron Will", "desc": "Easy quests can never fail", "cost": 1},
            "last_stand": {"name": "Last Stand", "desc": "When heart attack triggers, 50% chance to just lose quest gold but keep XP", "cost": 1},
        },
        "Harvest": {
            "forager": {"name": "Forager", "desc": "Quests may drop bonus material items", "cost": 1},
            "double_harvest": {"name": "Double Harvest", "desc": "15% chance for double loot", "cost": 1},
            "golden_touch": {"name": "Golden Touch", "desc": "Item sell prices doubled", "cost": 1},
        }
    }
}
```

## Step 2: Create `gacha_engine.py`
Create a new file `gacha_engine.py` with the complete gacha logic.

```python
import random
from datetime import datetime, timezone
import database

GACHA_RATES = {
    "common":    0.55,
    "uncommon":  0.27,
    "rare":      0.12,
    "epic":      0.05,
    "legendary": 0.01,
}

GACHA_COST = {
    "single": 50,
    "multi":  450,
}

PITY_THRESHOLDS = {
    "rare_pity":      10,
    "legendary_pity": 90,
    "hard_pity":      180,
}

GACHA_BANNERS = {
    "forge_of_ancients": {
        "id": "forge_of_ancients",
        "name": "⚒️ Forge of the Ancients",
        "start": "2026-10-16T00:00:00+02:00", 
        "end": "2026-10-30T23:59:59+02:00",
        "rate_up_item": "excalibrew_lv8",
        "rate_up_name": "☕ Excalibrew Lv.8",
        "featured_items": ["enchanted_katana_lv7", "mithril_plate_lv6", "winged_greaves_lv7"],
        "pool_item_levels": [6, 7, 8],
    },
    "celestial_wardrobe": {
        "id": "celestial_wardrobe",
        "name": "✨ Celestial Wardrobe",
        "start": "2026-10-30T00:00:00+02:00", 
        "end": "2026-11-13T23:59:59+01:00",
        "rate_up_item": "brewmasters_robe_lv9",
        "rate_up_name": "☕ Brewmaster's Robe Lv.9",
        "featured_items": ["plate_armor_lv7", "chainmail_lv8", "amulet_vitality_lv7"],
        "pool_item_levels": [6, 7, 8, 9],
    },
    "fates_gambit": {
        "id": "fates_gambit",
        "name": "🎲 Fate's Gambit",
        "start": "2026-11-13T00:00:00+01:00", 
        "end": "2026-11-27T23:59:59+01:00",
        "rate_up_item": "bean_of_destiny_lv10",
        "rate_up_name": "☕ Bean of Destiny Lv.10",
        "featured_items": ["lucky_charm_lv8", "ring_of_health_lv7", "swift_sandals_lv8"],
        "pool_item_levels": [7, 8, 9, 10],
    },
}

def get_active_banner() -> dict | None:
    now = datetime.now(timezone.utc)
    for b_id, banner in GACHA_BANNERS.items():
        start = datetime.fromisoformat(banner["start"]).astimezone(timezone.utc)
        end = datetime.fromisoformat(banner["end"]).astimezone(timezone.utc)
        if start <= now <= end:
            return banner
    return None

def get_pity_counter(user: str, banner_id: str) -> int:
    pulls = database.get_gacha_pulls(user, banner_id)
    count = 0
    for p in reversed(pulls):
        if p.get("rarity") == "legendary":
            break
        count += 1
    return count

def pull_gacha(user: str, banner_id: str, count: int = 1) -> list[dict]:
    banner = GACHA_BANNERS[banner_id]
    current_pity = get_pity_counter(user, banner_id)
    pulls = database.get_gacha_pulls(user, banner_id)
    total_pulls = len(pulls)
    
    results = []
    
    for i in range(count):
        current_pity += 1
        total_pulls += 1
        
        is_pity = False
        rarity = "common"
        item_id = ""
        
        # Determine Rarity
        if total_pulls % PITY_THRESHOLDS["hard_pity"] == 0:
            rarity = "legendary"
            item_id = banner["rate_up_item"]
            is_pity = True
            current_pity = 0
        elif current_pity >= PITY_THRESHOLDS["legendary_pity"]:
            rarity = "legendary"
            is_pity = True
            current_pity = 0
            if random.random() < 0.5:
                item_id = banner["rate_up_item"]
            else:
                item_id = f"random_legendary_{random.choice(banner['pool_item_levels'])}"
        else:
            r = random.random()
            if current_pity % PITY_THRESHOLDS["rare_pity"] == 0:
                if r < 0.05:
                    rarity = "epic"
                elif r < 0.06:
                    rarity = "legendary"
                    current_pity = 0
                else:
                    rarity = "rare"
                    is_pity = True
            else:
                if r < 0.01:
                    rarity = "legendary"
                    current_pity = 0
                elif r < 0.06:
                    rarity = "epic"
                elif r < 0.18:
                    rarity = "rare"
                elif r < 0.45:
                    rarity = "uncommon"
                else:
                    rarity = "common"
        
        if not item_id:
            if rarity == "legendary":
                item_id = banner["rate_up_item"] if random.random() < 0.5 else f"random_legendary_{random.choice(banner['pool_item_levels'])}"
            elif rarity == "epic":
                item_id = random.choice(banner["featured_items"])
            else:
                item_id = f"random_{rarity}_{random.choice(banner['pool_item_levels'])}"
                
        result = {
            "user_name": user,
            "banner_id": banner_id,
            "item_id": item_id,
            "rarity": rarity,
            "pity_count": current_pity,
            "is_pity": is_pity
        }
        database.insert_gacha_pull(result)
        results.append(result)
        
    return results
```

## Step 3: Create `raid_engine.py`
Create `raid_engine.py` for cooperative boss fights.

```python
import random
from datetime import datetime, timedelta, timezone
import database

RAID_BOSSES = {
    "caffeine_kraken": {
        "id": "caffeine_kraken",
        "name": "🦑 The Caffeine Kraken",
        "hp": 20_000,
        "element": "water",
        "weakness_drink": "iced",
        "rewards": {"gold": 500, "xp": 300, "loot_rarity_min": "epic"},
    },
    "sugar_colossus": {
        "id": "sugar_colossus",
        "name": "🗿 The Sugar Colossus",
        "hp": 25_000,
        "element": "earth",
        "weakness_drink": "tea",
        "rewards": {"gold": 650, "xp": 400, "loot_rarity_min": "epic"},
    },
    "decaf_lich": {
        "id": "decaf_lich",
        "name": "💀 The Decaf Lich King",
        "hp": 30_000,
        "element": "dark",
        "weakness_drink": "coffee",
        "rewards": {"gold": 800, "xp": 500, "loot_rarity_min": "legendary"},
    },
    "matcha_hydra": {
        "id": "matcha_hydra",
        "name": "🐍 The Matcha Hydra",
        "hp": 35_000,
        "element": "nature",
        "weakness_drink": None,
        "rewards": {"gold": 1000, "xp": 600, "loot_rarity_min": "legendary"},
    },
}

def get_active_raid():
    raids = database.get_active_boss_raids()
    if raids:
        return raids[0]
    return None

def calculate_damage(hero_atk: int, caffeine_today: float, drink_pref: str, boss: dict) -> int:
    dmg = hero_atk + random.randint(0, int(hero_atk / 2)) + int(caffeine_today / 10)
    if boss["weakness_drink"] and drink_pref == boss["weakness_drink"]:
        dmg = int(dmg * 1.5)
    return dmg

def start_raid_attack(user: str, raid_id: str, hero_atk: int, caffeine_today: float, drink_pref: str, boss_id: str) -> dict:
    boss = RAID_BOSSES[boss_id]
    damage = calculate_damage(hero_atk, caffeine_today, drink_pref, boss)
    
    attack = {
        "raid_id": raid_id,
        "user_name": user,
        "damage_dealt": damage,
        "caffeine_at_attack": caffeine_today,
        "hero_atk_snapshot": hero_atk,
        "duration_min": 30.0,
        "expected_end": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
        "status": "active"
    }
    
    return database.insert_boss_raid_attack(attack)

def process_completed_attacks(raid_id: str):
    attacks = database.get_active_attacks_for_raid(raid_id)
    now = datetime.now(timezone.utc)
    
    total_new_damage = 0
    for atk in attacks:
        if datetime.fromisoformat(atk["expected_end"]).astimezone(timezone.utc) <= now:
            database.update_raid_attack_status(atk["id"], "completed")
            total_new_damage += atk["damage_dealt"]
            
    if total_new_damage > 0:
        raid = database.get_raid_by_id(raid_id)
        new_hp = raid["damage_taken"] + total_new_damage
        status = "defeated" if new_hp >= raid["boss_max_hp"] else "active"
        database.update_raid_damage(raid_id, total_new_damage, status)

def get_raid_mvp(raid_id: str) -> str | None:
    leaderboard = database.get_raid_leaderboard(raid_id)
    if leaderboard:
        return leaderboard[0]["user_name"]
    return None
```

## Step 4: Add SQL Tables
Run these in Supabase SQL editor:
```sql
CREATE TABLE rpg_hero_skills (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_name   TEXT NOT NULL,
    skill_id    TEXT NOT NULL,
    unlocked_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT unique_user_skill UNIQUE (user_name, skill_id)
);

CREATE TABLE gacha_pulls (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_name   TEXT NOT NULL,
    banner_id   TEXT NOT NULL,
    item_id     TEXT NOT NULL,
    rarity      TEXT NOT NULL,
    pity_count  INTEGER NOT NULL,
    is_pity     BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE boss_raids (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    boss_id     TEXT NOT NULL,
    boss_max_hp INTEGER NOT NULL,
    damage_taken INTEGER NOT NULL DEFAULT 0,
    started_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ NOT NULL,
    status      TEXT NOT NULL DEFAULT 'active',
    defeated_at TIMESTAMPTZ
);

CREATE TABLE boss_raid_attacks (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    raid_id         UUID NOT NULL REFERENCES boss_raids(id),
    user_name       TEXT NOT NULL,
    damage_dealt    INTEGER DEFAULT 0,
    caffeine_at_attack FLOAT NOT NULL DEFAULT 0,
    hero_atk_snapshot INTEGER NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    duration_min    FLOAT NOT NULL,
    expected_end    TIMESTAMPTZ NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active',
    completed_at    TIMESTAMPTZ
);
```

## Step 5: Update `database.py`
Add these functions to the end of `database.py`:

```python
# Add to database.py

def insert_gacha_pull(pull_data: dict):
    supabase = get_supabase_client()
    return supabase.table("gacha_pulls").insert(pull_data).execute()

def get_gacha_pulls(user: str, banner_id: str):
    supabase = get_supabase_client()
    res = supabase.table("gacha_pulls").select("*").eq("user_name", user).eq("banner_id", banner_id).order("created_at").execute()
    return res.data

def get_active_boss_raids():
    supabase = get_supabase_client()
    res = supabase.table("boss_raids").select("*").eq("status", "active").execute()
    return res.data

def insert_boss_raid_attack(attack_data: dict):
    supabase = get_supabase_client()
    return supabase.table("boss_raid_attacks").insert(attack_data).execute().data[0]

def get_active_attacks_for_raid(raid_id: str):
    supabase = get_supabase_client()
    res = supabase.table("boss_raid_attacks").select("*").eq("raid_id", raid_id).eq("status", "active").execute()
    return res.data

def update_raid_attack_status(attack_id: str, status: str):
    supabase = get_supabase_client()
    supabase.table("boss_raid_attacks").update({"status": status, "completed_at": datetime.now(timezone.utc).isoformat()}).eq("id", attack_id).execute()

def get_raid_by_id(raid_id: str):
    supabase = get_supabase_client()
    res = supabase.table("boss_raids").select("*").eq("id", raid_id).execute()
    return res.data[0] if res.data else None

def update_raid_damage(raid_id: str, new_damage: int, status: str):
    supabase = get_supabase_client()
    raid = get_raid_by_id(raid_id)
    if raid:
        update_data = {"damage_taken": raid["damage_taken"] + new_damage, "status": status}
        if status == "defeated":
            update_data["defeated_at"] = datetime.now(timezone.utc).isoformat()
        supabase.table("boss_raids").update(update_data).eq("id", raid_id).execute()

def get_raid_leaderboard(raid_id: str):
    supabase = get_supabase_client()
    res = supabase.table("boss_raid_attacks").select("user_name, damage_dealt").eq("raid_id", raid_id).execute()
    
    totals = {}
    for r in res.data:
        totals[r["user_name"]] = totals.get(r["user_name"], 0) + r["damage_dealt"]
        
    sorted_totals = [{"user_name": k, "damage_dealt": v} for k, v in sorted(totals.items(), key=lambda item: item[1], reverse=True)]
    return sorted_totals

def get_hero_skills(user: str):
    supabase = get_supabase_client()
    res = supabase.table("rpg_hero_skills").select("*").eq("user_name", user).execute()
    return [r["skill_id"] for r in res.data]

def insert_hero_skill(user: str, skill_id: str):
    supabase = get_supabase_client()
    return supabase.table("rpg_hero_skills").insert({"user_name": user, "skill_id": skill_id}).execute()
```

## Step 6: Create `pages/7_🎰_Gacha.py`
```python
import streamlit as st
import gacha_engine
import database

st.set_page_config(page_title="Gacha", page_icon="🎰")
st.title("🎰 Gacha Banner")

user = st.sidebar.selectbox("Select User", ["matis", "alex", "john"])
banner = gacha_engine.get_active_banner()

if not banner:
    st.warning("No active banners at this time.")
    st.stop()

st.header(banner["name"])
st.write(f"**Rate Up Item:** {banner['rate_up_name']}")

pity = gacha_engine.get_pity_counter(user, banner["id"])
st.progress(min(pity / 90, 1.0))
st.caption(f"Pity: {pity}/90 (Legendary at 90)")

col1, col2 = st.columns(2)
with col1:
    if st.button("Single Pull (50 🪙)"):
        results = gacha_engine.pull_gacha(user, banner["id"], 1)
        st.success(f"Pulled: {results[0]['item_id']} ({results[0]['rarity']})")
with col2:
    if st.button("10x Pull (450 🪙)"):
        results = gacha_engine.pull_gacha(user, banner["id"], 10)
        for r in results:
            st.write(f"- {r['item_id']} ({r['rarity']})")
```

## Step 7: Create `pages/8_🐉_Boss_Raids.py`
```python
import streamlit as st
import raid_engine
import database

st.set_page_config(page_title="Boss Raids", page_icon="🐉")
st.title("🐉 Boss Raids")

user = st.sidebar.selectbox("Select User", ["matis", "alex", "john"])
raid = raid_engine.get_active_raid()

if not raid:
    st.info("The realm is peaceful. No active boss raids.")
    st.stop()

raid_engine.process_completed_attacks(raid["id"])
raid = raid_engine.get_active_raid() or raid # Refresh

boss_info = raid_engine.RAID_BOSSES[raid["boss_id"]]
st.header(boss_info["name"])

hp_pct = max(0, min(1.0, 1.0 - (raid["damage_taken"] / raid["boss_max_hp"])))
st.progress(hp_pct)
st.write(f"**HP:** {raid['boss_max_hp'] - raid['damage_taken']} / {raid['boss_max_hp']}")

if st.button("Attack Boss!"):
    # Assuming basic stats for demo purposes, integrate with actual hero data
    raid_engine.start_raid_attack(user, raid["id"], 100, 150.0, "iced", boss_info["id"])
    st.success("Attack started! It will complete in 30 minutes.")

st.subheader("Leaderboard")
leaderboard = database.get_raid_leaderboard(raid["id"])
for i, l in enumerate(leaderboard):
    st.write(f"{i+1}. {l['user_name']} - {l['damage_dealt']} DMG")
```

## Step 8: Update `data_processing.py`
Add Gacha Collector track and Secret Feats to `ACHIEVEMENTS_CONFIG` and `SECRET_FEATS` in `data_processing.py`.

```python
# In data_processing.py, under ACHIEVEMENTS_CONFIG:
"gacha_collector": {
    "tiers": [
        {"level": "Bronze",  "name": "🎰 First Pull",     "threshold": 1},
        {"level": "Silver",  "name": "📦 Collector",       "threshold": 50},
        {"level": "Gold",    "name": "🎯 Jackpot",         "threshold": 200},
        {"level": "Diamond", "name": "🐋 Gacha Whale",     "threshold": 500},
        {"level": "Master",  "name": "👑 Completionist",   "threshold": 1000},
    ],
}

# Under SECRET_FEATS:
{"id": "pity_party",       "title": "😭 Pity Party",       "condition": "Hit pity at exactly 90 pulls"},
{"id": "beginners_luck",   "title": "🌟 Beginner's Luck",  "condition": "Legendary on first-ever gacha pull"},
{"id": "party_carry",      "title": "⚔️ Party Carry",      "condition": "Deal 70%+ of total boss damage solo"},
{"id": "the_fellowship",   "title": "🤝 The Fellowship",    "condition": "All 3 users contribute 25%+ damage"},
{"id": "all_bosses",       "title": "🐲 Monster Hunter",   "condition": "Defeat all 4 unique raid bosses"},
```
