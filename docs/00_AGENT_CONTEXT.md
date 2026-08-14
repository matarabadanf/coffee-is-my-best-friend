# Agent Context: Coffee Is My Best Friend — Feature Drops Implementation

> **Purpose**: Read this document at the start of any implementation session to gain full context for building the 4 seasonal feature drops. This is a session-portable context anchor designed to be explicit enough for less capable AI models.

---

## 🗂️ Document Index

All design specifications live in the `docs/` directory of the project. Read these BEFORE implementing:

| Document | Path | Purpose |
|---|---|---|
| **Agent Context** | `docs/00_AGENT_CONTEXT.md` | Session bootstrap (you are here) |
| **Architecture** | `docs/01_ARCHITECTURE.md` | Feature flags, file map, economy, achievements |
| **Data Models** | `docs/02_DATA_MODELS.md` | All SQL schemas, ER diagram, key queries |

---

## 🏗️ Existing Codebase Architecture

### Project Location
```
\\wsl.localhost\Ubuntu-26.04\home\matis-ubuntu\bin\coffee-is-my-best-friend
```

### Exact Current File Structure
```
coffee-is-my-best-friend/
├── .streamlit/
│   └── secrets.toml
├── components/
│   ├── ui.py
│   └── charts.py
├── pages/
│   ├── 1_📈_Graphs!_Graphs!_Graphs!.py
│   ├── 2_🏆_Trophy_Room.py
│   ├── 3_🎨_Theme_Shop.py
│   └── 99_⚙️_Settings.py
├── 0_Coffee_is_my_best_friend_：).py
├── data_processing.py
├── database.py
├── requirements.txt
└── utils.py
```

### Exact Function Signatures from database.py
```python
def get_supabase_client() -> Client:
def get_data():
def insert_click(user: str, value: int, drink_id: int):
def get_transactions():
def insert_transaction(user: str, amount: int, transaction_type: str, metadata: dict = None):
```

### Exact Function Signatures from data_processing.py (Key ones)
```python
def process_raw_data(data, users):
def get_cumulative_data(data, start_date, end_date, users, freq="D"):
def get_expense_and_caffeine(coffee_scores, tea_scores):
def get_user_titles(user, trophies, return_all=False):
def resolve_user_title(user, prefs, trophies):
def get_coin_balances(df, transactions, users):
```

### Exact Current Table Schemas

#### `clicks` — Raw drink logs
| Column | Type | Notes |
|---|---|---|
| `id` | bigint/uuid | PK, auto |
| `created_at` | timestamptz | UTC |
| `user_name` | text | "Cris", "Bea", "Fer" |
| `value` | integer | Always 1 |
| `drink_id` | integer | 1=Hot Coffee, 2=Hot Tea, 3=Iced Coffee, 4=Iced Tea |

#### `coin_transactions` — Economy, preferences, metadata
| Column | Type | Notes |
|---|---|---|
| `id` | bigint/uuid | PK, auto |
| `created_at` | timestamptz | UTC |
| `user_name` | text | "Cris", "Bea", "Fer" |
| `amount` | integer | +10 earn, -600 spend, 0 preference |
| `transaction_type` | text | "drink_log", "shop", "preference" |
| `metadata` | jsonb | Context-dependent payload |

### Drink Metabolism & `drink_id` Mapping

| drink_id | Name | Caffeine | Cost |
|---|---|---|---|
| 1 | Hot Coffee | 95 mg | €2.50 |
| 2 | Hot Tea | 30 mg | €1.50 |
| 3 | Iced Coffee | 95 mg | €2.50 |
| 4 | Iced Tea | 30 mg | €1.50 |

### Users and Defaults
There are exactly 3 users:
- **Cris**
- **Bea**
- **Fer**

Default country for all 3 users is `"ES"` (Spain/Madrid).

---

## ⚠️ Non-Negotiable Design Rules

1. **Travel, not origin**: Drop 1 country = WHERE the user physically IS, not where coffee comes from.
2. **One-time class pick**: Free at first unlock, then requires Scroll of Reclass (rare quest drop).
3. **NO multi-questing**: One active quest at a time, always, no exceptions.
4. **Leveled items**: Lv.1-5 from quests (Drop 2), Lv.6-10 gacha/raid exclusive (Drop 3).
5. **Level cap**: 50 in Drop 2, raised to 100 in Drop 3.
6. **Wrapped = 2026 only**: All queries filtered Jan 1 - Oct 31, 2026.
7. **Madrid timezone**: All time-gating uses `Europe/Madrid`.
8. **Default country**: All 3 users default to `"ES"` (Spain/Madrid).

---

## 📋 Implementation Order

### Phase 1: Shared Infrastructure
1. Create `feature_flags.py` (Implementation in Architecture doc).
2. Update `requirements.txt` (Add folium, streamlit-folium, Pillow).

### Phase 2: Drop 1 — World Update
1. Create `world_data.py`.
2. Modify landing page (country selector).
3. Modify Settings (default country).
4. Modify `data_processing.py` (achievements, feats, prefs).
5. Create `pages/4_🌍_World_Explorer.py`.
6. Modify Graphs page (Travel tab).
7. Modify Trophy Room (World Explorer track).

### Phase 3: Drop 2 — RPG Quest Engine
1. Create `rpg_data.py`.
2. Create `rpg_engine.py`.
3. Create Supabase tables (`rpg_heroes`, `rpg_inventory`, `rpg_quests`).
4. Update `database.py` (RPG CRUD).
5. Create `pages/5_⚔️_Quest_Board.py`.
6. Create `pages/6_🎒_Hero_Inventory.py`.
7. Update landing page (quest widget).
8. Update `data_processing.py` (RPG achievements + feats).

### Phase 4: Drop 3 — Gacha & Boss Raids
1. Update `rpg_data.py` (level cap 100, skill trees, Lv.6-10 items).
2. Create `gacha_engine.py`.
3. Create `raid_engine.py`.
4. Create Supabase tables (`rpg_hero_skills`, `gacha_pulls`, `boss_raids`, `boss_raid_attacks`).
5. Update `database.py` (gacha + raid CRUD).
6. Create `pages/7_🎰_Gacha.py`.
7. Create `pages/8_🐉_Boss_Raids.py`.
8. Update `pages/6_🎒_Hero_Inventory.py` (skill tree UI).
9. Update `data_processing.py` (gacha achievements + feats).

### Phase 5: Drop 4 — Coffee Wrapped
1. Create `wrapped_engine.py`.
2. Create `pages/10_🎁_Wrapped.py`.
3. Update `data_processing.py` (Wrapped feats).

---

## 🌿 Branch Strategy

```text
main ─── production (Streamlit Cloud live app)
  └── dev ─── staging (Streamlit Cloud dev app)
       └── feat/drop-1-world-update
       └── feat/drop-2-rpg-quests
       └── feat/drop-3-gacha-raids
       └── feat/drop-4-wrapped
```

1. Create feature branch from `dev`.
2. Implement + test on feature branch.
3. Merge to `dev` → smoke test on Streamlit dev app.
4. Merge `dev` to `main` when ready → push to production.
5. Keep feature branch alive until confirmed working.
