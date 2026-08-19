import streamlit as st
import pandas as pd
from world_data import (
    TRAVEL_COUNTRIES, 
    DEFAULT_COUNTRY, 
    get_user_default_country, 
    get_user_default_city, 
    compute_passport_stats,
    is_coffee_capital
)

# Re-export all gamification models, configs, Hall of Fame, and engine functions
from gamification import (
    ACHIEVEMENT_TIERS,
    SECRET_FEATS,
    ACHIEVEMENTS_START_DATE,
    compute_monarch_hall_of_fame,
    compute_all_trophy_hall_of_fames,
    get_gamification_metrics,
    get_user_titles,
    resolve_user_title
)

@st.cache_data(show_spinner=False)
def process_raw_data(data, users):
    if not data:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, {}

    df = pd.DataFrame(data)
    
    # Ensure drink_id exists (fill with 1 for Coffee if missing)
    if "drink_id" not in df.columns:
        df["drink_id"] = 1
    else:
        df["drink_id"] = df["drink_id"].fillna(1)
    
    # Convert timestamps
    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)

    # Extract location (country & city) from JSON or dedicated columns if present
    if not df.empty:
        if "location" in df.columns:
            def _extract_loc(loc):
                if isinstance(loc, dict):
                    return loc.get("country"), loc.get("city")
                return None, None
            loc_tuples = df["location"].apply(_extract_loc)
            if "country" not in df.columns or df["country"].isna().all():
                df["country"] = [t[0] for t in loc_tuples]
            else:
                df["country"] = df["country"].fillna(pd.Series([t[0] for t in loc_tuples], index=df.index))
                
            if "city" not in df.columns or df["city"].isna().all():
                df["city"] = [t[1] for t in loc_tuples]
            else:
                df["city"] = df["city"].fillna(pd.Series([t[1] for t in loc_tuples], index=df.index))
    
    # Separate Dataframes (1: Hot Coffee, 3: Iced Coffee, 2: Hot Tea, 4: Iced Tea)
    df_coffee = df[df["drink_id"].isin([1, 3])]
    df_tea = df[df["drink_id"].isin([2, 4])]
    
    # Calculate Scores
    coffee_scores = df_coffee.groupby("user_name")["value"].sum().to_dict()
    tea_scores = df_tea.groupby("user_name")["value"].sum().to_dict()

    return df, df_coffee, df_tea, coffee_scores, tea_scores

@st.cache_data(show_spinner=False)
def get_cumulative_data(data, start_date, end_date, users, freq="D"):
    # 1. Normalize dates to clean midnight intervals so reindex matches resampled timestamps
    start_date = pd.to_datetime(start_date).normalize()
    end_date = pd.to_datetime(end_date).normalize()
    full_index = pd.date_range(start=start_date, end=end_date, freq=freq)
    
    # 2. Filter data within normalized boundaries
    mask = (data["created_at"] >= start_date) & (data["created_at"] <= (end_date + pd.Timedelta(days=1)))
    filtered_df = data.loc[mask].copy()
    
    if filtered_df.empty:
        empty_df = pd.DataFrame(0, index=full_index, columns=users)
        return empty_df.cumsum()

    # Pivot to [Time, User] = Count
    pivot = filtered_df.pivot_table(index="created_at", columns="user_name", values="value", aggfunc="sum", fill_value=0)
    
    # 3. Ensure all users exist
    for u in users:
        if u not in pivot.columns:
            pivot[u] = 0
            
    # 4. Resample & Reindex
    resampled = pivot.resample(freq).sum()
    resampled = resampled.reindex(full_index, fill_value=0)
    
    # 5. Cumulative Sum
    cumulative = resampled.cumsum()
    cumulative = cumulative.astype(float)
    
    return cumulative

def get_expense_and_caffeine(coffee_scores, tea_scores):
    # Assumptions
    COFFEE_MG = 95
    COFFEE_COST = 2.50
    TEA_MG = 30
    TEA_COST = 1.50
    
    metrics = {}
    for user in set(list(coffee_scores.keys()) + list(tea_scores.keys())):
        coffees = coffee_scores.get(user, 0)
        teas = tea_scores.get(user, 0)
        
        total_mg = (coffees * COFFEE_MG) + (teas * TEA_MG)
        total_cost = (coffees * COFFEE_COST) + (teas * TEA_COST)
        
        metrics[user] = {
            "total_mg": total_mg,
            "total_cost": total_cost,
            "coffee_cost": coffees * COFFEE_COST,
            "tea_cost": teas * TEA_COST,
            "coffee_mg": coffees * COFFEE_MG,
            "tea_mg": teas * TEA_MG
        }
        
    return metrics

@st.cache_data(show_spinner=False)
def get_coin_balances(df, transactions, users):
    balances = {u: 0 for u in users}
    
    if not df.empty:
        counts = df.groupby("user_name").size()
        for u, count in counts.items():
            if u in balances:
                balances[u] += count * 10
                
    if transactions:
        tx_df = pd.DataFrame(transactions)
        if not tx_df.empty and "amount" in tx_df.columns:
            tx_sums = tx_df.groupby("user_name")["amount"].sum()
            for u, amt in tx_sums.items():
                if u in balances:
                    balances[u] += amt
                    
    return balances

@st.cache_data(show_spinner=False)
def get_active_perks(transactions, users):
    perks = {u: [] for u in users}
    if not transactions:
        return perks
        
    tx_df = pd.DataFrame(transactions)
    if tx_df.empty or "transaction_type" not in tx_df.columns:
        return perks
        
    perk_txs = tx_df[tx_df["transaction_type"] == "perk"]
    if not perk_txs.empty:
        for _, row in perk_txs.iterrows():
            u = row.get("user_name")
            meta = row.get("metadata", {})
            if u in perks and isinstance(meta, dict) and "perk" in meta:
                perks[u].append(meta["perk"])
                
    return perks

BASE_THEMES = ["Latte (Light)"]
ALL_VALID_THEMES = [
    "Latte (Light)",
    "Espresso (Dark)",
    "Matcha (Green)",
    "Caramel Macchiato (Amber)",
    "Strawberry Frappé (Pink)",
    "Taro Boba (Purple)",
    "Midnight Cyber Brew (Dark Neon)",
    "Velvet Mocha (Cocoa)"
]

@st.cache_data(show_spinner=False)
def get_unlocked_themes(transactions, user):
    """Returns list of themes unlocked by a specific user (always includes base themes)."""
    unlocked = set(BASE_THEMES)
    if not transactions:
        return [t for t in ALL_VALID_THEMES if t in unlocked]
        
    tx_df = pd.DataFrame(transactions)
    if tx_df.empty or "transaction_type" not in tx_df.columns:
        return [t for t in ALL_VALID_THEMES if t in unlocked]
        
    user_shop_txs = tx_df[(tx_df["transaction_type"] == "shop") & (tx_df["user_name"] == user)]
    if not user_shop_txs.empty:
        for _, row in user_shop_txs.iterrows():
            meta = row.get("metadata", {})
            if isinstance(meta, dict):
                theme_unlocked = meta.get("theme_unlock") or meta.get("unlocked_theme")
                if theme_unlocked and theme_unlocked in ALL_VALID_THEMES:
                    unlocked.add(theme_unlocked)
                    
    # Return in standardized order
    return [t for t in ALL_VALID_THEMES if t in unlocked]

@st.cache_data(show_spinner=False)
def get_user_preferences(transactions=None, users=None, db_preferences=None):
    if db_preferences is None:
        try:
            from database import get_preferences
            db_preferences = get_preferences()
        except Exception:
            db_preferences = []

    if users is None:
        users = ["Cris", "Bea", "Fer"]
        
    prefs = {
        u: {
            "theme": "Latte (Light)", 
            "emoji": "☕", 
            "title": None, 
            "ui_style": "Modern Flat", 
            "default_country": get_user_default_country(u),
            "default_city": get_user_default_city(u),
            "share_live_location": True
        } for u in users
    }
    
    # 1. Apply preferences from coin_transactions (legacy fallback)
    if transactions:
        tx_df = pd.DataFrame(transactions)
        if not tx_df.empty and "transaction_type" in tx_df.columns:
            pref_txs = tx_df[tx_df["transaction_type"] == "preference"]
            for _, row in pref_txs.iterrows():
                u = row.get("user_name")
                meta = row.get("metadata", {})
                if u in prefs and isinstance(meta, dict):
                    if "theme" in meta:
                        theme_val = meta["theme"]
                        unlocked_for_u = get_unlocked_themes(transactions, u)
                        if theme_val not in unlocked_for_u:
                            theme_val = "Latte (Light)"
                        prefs[u]["theme"] = theme_val
                    if "emoji" in meta:
                        prefs[u]["emoji"] = meta["emoji"]
                    if "title" in meta:
                        prefs[u]["title"] = meta["title"]
                    if "ui_style" in meta:
                        style_val = meta["ui_style"]
                        if style_val not in ["Modern Flat", "Glassmorphism", "Neumorphism"]:
                            style_val = "Modern Flat"
                        prefs[u]["ui_style"] = style_val
                    if "default_country" in meta:
                        prefs[u]["default_country"] = meta["default_country"]
                    if "default_city" in meta:
                        prefs[u]["default_city"] = meta["default_city"]
                    if "share_live_location" in meta:
                        prefs[u]["share_live_location"] = bool(meta["share_live_location"])

    # 2. Apply from dedicated user_preferences table (takes primary precedence)
    if db_preferences:
        for row in db_preferences:
            u = row.get("user_name")
            if u in prefs:
                if row.get("theme"):
                    theme_val = row["theme"]
                    unlocked_for_u = get_unlocked_themes(transactions or [], u)
                    if theme_val not in unlocked_for_u:
                        theme_val = "Latte (Light)"
                    prefs[u]["theme"] = theme_val
                if row.get("emoji"):
                    prefs[u]["emoji"] = row["emoji"]
                if "title" in row and row["title"] is not None:
                    prefs[u]["title"] = row["title"]
                if row.get("ui_style"):
                    style_val = row["ui_style"]
                    if style_val in ["Modern Flat", "Glassmorphism", "Neumorphism"]:
                        prefs[u]["ui_style"] = style_val
                if row.get("default_country"):
                    prefs[u]["default_country"] = row["default_country"]
                if row.get("default_city"):
                    prefs[u]["default_city"] = row["default_city"]
                if "share_live_location" in row and row["share_live_location"] is not None:
                    prefs[u]["share_live_location"] = bool(row["share_live_location"])
                if isinstance(row.get("metadata"), dict):
                    meta = row["metadata"]
                    for k, v in meta.items():
                        prefs[u][k] = v

    return prefs
