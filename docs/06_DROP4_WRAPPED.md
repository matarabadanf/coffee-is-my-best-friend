# Drop 4 — 🎁 Coffee Wrapped 2026 Implementation Specification

This document provides step-by-step, exact code implementations for Drop 4.

## Step 1: Create `wrapped_engine.py`

```python
from datetime import datetime, timezone
import pandas as pd
import io
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    pass # Will handle gracefully in UI

WRAPPED_START = "2026-01-01T00:00:00+01:00"
WRAPPED_END = "2026-10-31T23:59:59+01:00"

PERSONALITY_ARCHETYPES = {
    "midnight_alchemist": {
        "id": "midnight_alchemist",
        "name": "🌙 The Midnight Alchemist",
        "quote": "You brew in the witching hour when the world sleeps. Creativity flows when caffeine meets moonlight.",
        "condition": "30%+ of 2026 drinks logged after 20:00",
    },
    "gacha_gremlin": {
        "id": "gacha_gremlin",
        "name": "🎰 The Gacha Gremlin",
        "quote": "You drink coffee just to fund your next pull. Was the Legendary worth it? Always.",
        "condition": "50+ gacha pulls in 2026",
    },
    "frost_monarch": {
        "id": "frost_monarch",
        "name": "🧊 The Frost Monarch",
        "quote": "Temperature is just a suggestion. You've chosen your side: ice cold. Even in January.",
        "condition": "75%+ iced drinks in 2026",
    },
    "tea_sommelier": {
        "id": "tea_sommelier",
        "name": "🍵 The Tea Sommelier",
        "quote": "Leaves over beans. Elegant, refined, hydrated. You sip while the world gulps.",
        "condition": "70%+ tea (drink_ids 2,4) in 2026",
    },
    "espresso_sprinter": {
        "id": "espresso_sprinter",
        "name": "⚡ The Espresso Sprinter",
        "quote": "You wake up and choose velocity. Sleep is for the un-caffeinated.",
        "condition": "Total caffeine > 25,000mg AND 50%+ drinks before 10:00",
    },
    "war_hero": {
        "id": "war_hero",
        "name": "🐉 The War Hero",
        "quote": "While others sipped, you fought. Your quest log reads like an epic saga — heart attacks and all.",
        "condition": "100+ quests completed AND 3+ heart attacks in 2026",
    },
    "wandering_bean": {
        "id": "wandering_bean",
        "name": "🗺️ The Wandering Bean",
        "quote": "Every cup is a passport stamp. You taste the world one country at a time.",
        "condition": "8+ countries on passport in 2026",
    },
    "balanced_bean": {
        "id": "balanced_bean",
        "name": "☕ The Balanced Bean",
        "quote": "Perfectly balanced, as all brews should be. No extremes, just good vibes.",
        "condition": "FALLBACK",
    },
}

def filter_2026(df: pd.DataFrame, date_col: str = "created_at") -> pd.DataFrame:
    """Filters a dataframe to ONLY contain records between WRAPPED_START and WRAPPED_END."""
    if df.empty or date_col not in df.columns:
        return df
    
    # Ensure datetime format and filter
    try:
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col], utc=True)
        
        start = pd.to_datetime(WRAPPED_START, utc=True)
        end = pd.to_datetime(WRAPPED_END, utc=True)
        
        return df[(df[date_col] >= start) & (df[date_col] <= end)]
    except Exception:
        return df

def compute_wrapped_metrics(user: str, clicks_df: pd.DataFrame, gacha_pulls: list, rpg_quests: list) -> dict:
    """Computes all metrics required for the Wrapped cards and personality archetype."""
    df_2026 = filter_2026(clicks_df[clicks_df["user_name"] == user])
    
    total_drinks = len(df_2026)
    if total_drinks == 0:
        return {"total_drinks": 0}
        
    hot_drinks = len(df_2026[df_2026["drink_id"].isin([1, 2])])
    iced_drinks = len(df_2026[df_2026["drink_id"].isin([3, 4])])
    coffee_drinks = len(df_2026[df_2026["drink_id"].isin([1, 3])])
    tea_drinks = len(df_2026[df_2026["drink_id"].isin([2, 4])])
    
    # Time analysis
    df_2026["hour"] = df_2026["created_at"].dt.hour
    night_drinks = len(df_2026[df_2026["hour"] >= 20])
    morning_drinks = len(df_2026[df_2026["hour"] < 10])
    
    # Caffeine (rough approx)
    total_caffeine = (coffee_drinks * 95) + (tea_drinks * 35)
    
    # Quests & Gacha
    # Assuming quests and gacha pulls are lists of dicts
    q_df = pd.DataFrame(rpg_quests) if rpg_quests else pd.DataFrame()
    g_df = pd.DataFrame(gacha_pulls) if gacha_pulls else pd.DataFrame()
    
    q_2026 = filter_2026(q_df, "created_at") if not q_df.empty else pd.DataFrame()
    g_2026 = filter_2026(g_df, "created_at") if not g_df.empty else pd.DataFrame()
    
    completed_quests = len(q_2026[q_2026["status"] == "completed"]) if not q_2026.empty else 0
    failed_quests = len(q_2026[q_2026["status"] == "failed_heart_attack"]) if not q_2026.empty else 0
    total_pulls = len(g_2026) if not g_2026.empty else 0

    return {
        "total_drinks": total_drinks,
        "iced_pct": (iced_drinks / total_drinks) * 100,
        "tea_pct": (tea_drinks / total_drinks) * 100,
        "night_pct": (night_drinks / total_drinks) * 100,
        "morning_pct": (morning_drinks / total_drinks) * 100,
        "total_caffeine": total_caffeine,
        "quests_completed": completed_quests,
        "heart_attacks": failed_quests,
        "gacha_pulls": total_pulls,
        "countries_visited": 1 # Mock for now
    }

def determine_personality(metrics: dict) -> dict:
    if metrics.get("night_pct", 0) >= 30:
        return PERSONALITY_ARCHETYPES["midnight_alchemist"]
    if metrics.get("gacha_pulls", 0) >= 50:
        return PERSONALITY_ARCHETYPES["gacha_gremlin"]
    if metrics.get("iced_pct", 0) >= 75:
        return PERSONALITY_ARCHETYPES["frost_monarch"]
    if metrics.get("tea_pct", 0) >= 70:
        return PERSONALITY_ARCHETYPES["tea_sommelier"]
    if metrics.get("total_caffeine", 0) > 25000 and metrics.get("morning_pct", 0) >= 50:
        return PERSONALITY_ARCHETYPES["espresso_sprinter"]
    if metrics.get("quests_completed", 0) >= 100 and metrics.get("heart_attacks", 0) >= 3:
        return PERSONALITY_ARCHETYPES["war_hero"]
    if metrics.get("countries_visited", 0) >= 8:
        return PERSONALITY_ARCHETYPES["wandering_bean"]
    return PERSONALITY_ARCHETYPES["balanced_bean"]

def generate_wrapped_card(user_name: str, emoji: str, metrics: dict, archetype: dict) -> bytes:
    try:
        img = Image.new("RGB", (1080, 1920), color=(20, 20, 30))
        draw = ImageDraw.Draw(img)
        
        # We would use a real font here, but for fallback:
        # font = ImageFont.truetype("arial.ttf", 60)
        font = ImageFont.load_default()
        
        draw.text((100, 200), f"Coffee Wrapped 2026", fill="white", font=font)
        draw.text((100, 300), f"{emoji} {user_name}", fill="white", font=font)
        
        draw.text((100, 500), f"Total Drinks: {metrics.get('total_drinks', 0)}", fill="white", font=font)
        draw.text((100, 600), f"Archetype:", fill="white", font=font)
        draw.text((100, 700), archetype["name"], fill="gold", font=font)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        return b""
```

## Step 2: Create `pages/10_🎁_Wrapped.py`

```python
import streamlit as st
import wrapped_engine
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Coffee Wrapped 2026", page_icon="🎁")

now = datetime.now()
unlock_date = datetime(2026, 10, 31)

if now < unlock_date:
    st.markdown("### 🎁 Something is coming...")
    st.markdown("🔒 LOCKED")
    st.markdown(f"Unlocks in: {unlock_date - now}")
    st.markdown('"The beans are whispering..."')
    st.stop()

# --- Wrapped Experience ---
if "wrapped_card_index" not in st.session_state:
    st.session_state.wrapped_card_index = 0
    st.balloons()

user = st.sidebar.selectbox("Select User", ["matis", "alex", "john"])

# Mock fetching data (replace with actual database calls)
df = pd.DataFrame() 
gacha_pulls = []
rpg_quests = []

metrics = wrapped_engine.compute_wrapped_metrics(user, df, gacha_pulls, rpg_quests)
archetype = wrapped_engine.determine_personality(metrics)

cards = [
    f"### ☕ COFFEE WRAPPED 2026\n\n{user}, you've been on quite the journey.\n\nTotal beverages this year: ☕ {metrics.get('total_drinks', 0)}",
    f"### ⚡ Total Caffeine\n\nYou consumed {metrics.get('total_caffeine', 0)}mg of caffeine this year!",
    f"### 🏆 Top Drink\n\nYour go-to choice.",
    f"### ☕ vs 🍵 The Eternal Battle\n\nCoffee: {100 - metrics.get('tea_pct', 0):.1f}% | Tea: {metrics.get('tea_pct', 0):.1f}%",
    f"### 🔥 vs 🧊 Temperature Wars\n\nHot: {100 - metrics.get('iced_pct', 0):.1f}% | Iced: {metrics.get('iced_pct', 0):.1f}%",
    f"### ⏰ Your Rhythm\n\nMorning person? {metrics.get('morning_pct', 0):.1f}% of your drinks were before 10 AM.",
    f"### 🔥 The Streak\n\nConsistency is key.",
    f"### 🌍 The Explorer\n\nYou tasted beans from {metrics.get('countries_visited', 0)} countries.",
    f"### ⚔️ The Hero\n\nQuests Completed: {metrics.get('quests_completed', 0)}\nHeart Attacks: {metrics.get('heart_attacks', 0)}",
    f"### 🗡️ The Arsenal\n\nYour legendary items gathered this year.",
    f"### 🎰 The Gacha & Raids\n\nTotal Pulls: {metrics.get('gacha_pulls', 0)}",
    f"### 🎭 Your Personality\n\n**{archetype['name']}**\n\n_{archetype['quote']}_"
]

current_card = st.session_state.wrapped_card_index

st.progress((current_card + 1) / 12)
st.markdown(cards[current_card])

col1, col2 = st.columns(2)
with col1:
    if current_card > 0:
        if st.button("← Prev"):
            st.session_state.wrapped_card_index -= 1
            st.rerun()
with col2:
    if current_card < 11:
        if st.button("Next →"):
            st.session_state.wrapped_card_index += 1
            st.rerun()
    elif current_card == 11:
        png_bytes = wrapped_engine.generate_wrapped_card(user, "☕", metrics, archetype)
        if png_bytes:
            st.download_button("📸 Save & Share", png_bytes, "coffee_wrapped_2026.png", "image/png")
```

## Step 3: Update `data_processing.py`
Add Wrapped secret feats to `SECRET_FEATS`.

```python
# In data_processing.py, under SECRET_FEATS:
{"id": "wrapped_viewer", "title": "🎁 Unwrapped",          "condition": "View Coffee Wrapped 2026"},
{"id": "wrapped_sharer", "title": "📸 Show Off",            "condition": "Download the shareable card"},
{"id": "full_journey",   "title": "🌟 The Complete Journey", "condition": "View all 12 cards"},
```
