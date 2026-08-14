import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Import refactored modules
from database import get_data, insert_click, get_transactions, insert_transaction, get_preferences, save_user_preference
from data_processing import (
    process_raw_data, 
    get_gamification_metrics, 
    get_user_titles, 
    resolve_user_title,
    get_coin_balances, 
    get_active_perks, 
    get_user_preferences
)
from utils import enforce_user_identity
from world_data import (
    TRAVEL_COUNTRIES, 
    get_country_options, 
    get_option_from_code, 
    get_country_code_from_option, 
    get_user_default_country,
    get_user_default_city,
    get_cities_for_country,
    normalize_city_name,
    get_flag_img_html
)
from feature_flags import is_unlocked, is_dev_mode, is_patch_notes_active, get_current_madrid_time
from components.ui import (
    inject_custom_css, 
    render_app_header, 
    render_daily_fact_quote,
    render_circular_caffeine_gauge, 
    render_coffee_tea_fuel_bar
)
from components.celebrations import (
    get_user_achievement_snapshot, 
    compute_new_unlocks, 
    trigger_celebration_popup_if_pending,
    get_ui_2_0_welcome_payload
)

# 1. Page Configuration
st.set_page_config(page_title="Coffee is my best friend", page_icon="☕", layout="wide")

# User Configuration
users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

# 2. Data Fetching & Processing
data = get_data()
transactions = get_transactions()
db_prefs = get_preferences()
df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)

prefs = get_user_preferences(transactions, users, db_preferences=db_prefs)
user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")

# Inject Active Theme & CSS (with surprise sidebar concealment for non-devs)
inject_custom_css(user_theme, user_style, user=selected_user)

# Check and render any pending celebration popup dialogs
trigger_celebration_popup_if_pending(selected_user)

trophies = get_gamification_metrics(df_coffee, df_tea, users)
coin_balances = get_coin_balances(df, transactions, users)
active_perks = get_active_perks(transactions, users)

user_coins = coin_balances.get(selected_user, 0)
user_streak = trophies.get("streaks", {}).get(selected_user, 0)
user_emoji = prefs.get(selected_user, {}).get("emoji", "☕")
user_title = resolve_user_title(selected_user, prefs, trophies)

# --- 1. Top Status App Header ---
render_app_header(
    selected_user=selected_user, 
    coin_balance=user_coins, 
    streak_days=user_streak, 
    custom_emoji=user_emoji, 
    custom_title=user_title
)

# --- 1.1 Standalone Daily Trivia Quote (Outside the header box) ---
render_daily_fact_quote()

# --- 📜 COMPREHENSIVE DROP 1 & UI 2.0 PATCH NOTES ---
with st.expander("🎉 **Drop 1 Patch Notes — World Explorer & UI 2.0 (Tap to expand)**", expanded=False):
    pn1, pn2, pn3 = st.columns(3)
    with pn1:
        st.markdown("""
        #### 🌍 **World Explorer & Passport**
        - ✈️ **Real-Time Travel Logging**: Log beverages with exact **Country & City** directly from the beverage bar!
        - 🏠 **Personalized Home Bases**: Configured per explorer (**Bea**: 🇳🇱 Amsterdam, **Fer**: 🇫🇷 Paris, **Cris**: 🇨🇿 Prague) with dynamic geocoding.
        - 🗺️ **Interactive Travel Map**: Open [🌍 World Explorer](pages/4_🌍_World_Explorer.py) to view city markers, multi-crew explorer filters, and beverage views.
        - 🔒 **Location Privacy Controls**: Instant toggle in [⚙️ Settings](pages/99_⚙️_Settings.py) to control whether your live feed broadcasts your city/country.
        """)
    with pn2:
        st.markdown("""
        #### 🎨 **UI 2.0 & Dynamic Morphism**
        - ✨ **Dynamic Morphism Engine**: Switch between **Modern Flat**, **Glassmorphism**, and **Neumorphism** styles!
        - 🛍️ **Theme Boutique**: 8 handcrafted color palettes (*Latte, Espresso, Matcha, Caramel Macchiato, Strawberry Frappé, Taro Boba, Midnight Cyber Brew, Velvet Mocha*) in [🎨 Theme Boutique](pages/3_🎨_Theme_Shop.py).
        - ⚡ **Synchronized Activity Feed**: Pure `clicks` source of truth updating instantly upon beverage logging or modifications.
        """)
    with pn3:
        st.markdown("""
        #### 🏆 **Achievements & Dynasty Hall of Fame**
        - 🎖️ **13 Progressive Mastery Tracks**: Featuring *World Explorer*, *Metropolis Explorer*, *Espresso Mastery*, *Zen Tea Garden*, *Sub-Zero Frost*, *Streak Sovereign*, and more.
        - ⬆️ **Tier Upgrade Celebrations**: Live modal alerts comparing previous vs newly unlocked tiers with 1-tap emoji badge equipping!
        - 👑 **Dynasty Hall of Fame**: Direct in-place rankings on all 13 cards in [🏆 Trophy Room](pages/2_🏆_Trophy_Room.py) with lifetime +250 🪙 crown rewards.
        - 🕵️ **Arcane Secret Feats**: Concealed easter eggs and cryptic riddles hidden in Tab 3!
        """)

# Calculate today's stats
today_coffees = 0
today_teas = 0
today_hot_coffees = 0
today_iced_coffees = 0
today_hot_teas = 0
today_iced_teas = 0
today_df = pd.DataFrame()

if not df.empty:
    if df["created_at"].dt.tz is None:
        df["created_at"] = df["created_at"].dt.tz_localize("UTC")
    df["created_at"] = df["created_at"].dt.tz_convert("Europe/Madrid")
    
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_df = df[df["created_at"] >= today_start]
    
    today_hot_coffees = int(today_df[today_df["drink_id"] == 1]["value"].sum()) if not today_df.empty else 0
    today_iced_coffees = int(today_df[today_df["drink_id"] == 3]["value"].sum()) if not today_df.empty else 0
    today_coffees = today_hot_coffees + today_iced_coffees
    
    today_hot_teas = int(today_df[today_df["drink_id"] == 2]["value"].sum()) if not today_df.empty else 0
    today_iced_teas = int(today_df[today_df["drink_id"] == 4]["value"].sum()) if not today_df.empty else 0
    today_teas = today_hot_teas + today_iced_teas

# Selected user today's caffeine
user_today = today_df[today_df["user_name"] == selected_user] if not today_df.empty else pd.DataFrame()
user_caff_today = (int(user_today[user_today["drink_id"].isin([1, 3])]["value"].sum()) * 95) + (int(user_today[user_today["drink_id"].isin([2, 4])]["value"].sum()) * 35) if not user_today.empty else 0

# Cooldown check for selected user
last_click_time = None
if not df.empty:
    user_clicks = df[df["user_name"] == selected_user]
    if not user_clicks.empty:
        last_click_time = user_clicks["created_at"].max()

def handle_drink_log(drink_id, drink_name, temp_name, country_code, city_name):
    if last_click_time and (now - last_click_time).total_seconds() < 60:
        st.warning(f"Wait {int(60 - (now - last_click_time).total_seconds())}s before logging again!")
        return
    try:
        # 0. Capture Before Snapshot for celebration detection
        before_snapshot = get_user_achievement_snapshot(selected_user, df_coffee, df_tea, transactions, users)

        # 1. Insert Click Record with location columns
        insert_click(selected_user, 1, drink_id, country=country_code, city=city_name)
        
        # 2. Insert Coin Transaction with explicit temperature, country, and city metadata
        insert_transaction(
            selected_user, 
            10, 
            "drink_log", 
            {
                "drink": drink_name.lower(), 
                "temperature": temp_name.lower(), 
                "drink_id": drink_id,
                "country": country_code,
                "city": city_name
            }
        )

        # 3. Capture After Snapshot & Detect Unlocks
        fresh_data = get_data()
        fresh_tx = get_transactions()
        fresh_df, fresh_coffee, fresh_tea, _, _ = process_raw_data(fresh_data, users)
        after_snapshot = get_user_achievement_snapshot(selected_user, fresh_coffee, fresh_tea, fresh_tx, users)

        new_unlocks = compute_new_unlocks(
            selected_user, 
            before_snapshot, 
            after_snapshot, 
            transactions=fresh_tx
        )

        # Automatic first-time Welcome to UI 2.0 celebration & feature tour trigger on first drink logged in UI 2.0
        user_seen_ui2 = prefs.get(selected_user, {}).get("has_seen_ui_2_0", False)
        if not user_seen_ui2:
            if new_unlocks is None:
                new_unlocks = []
            new_unlocks.extend(get_ui_2_0_welcome_payload(selected_user))
            save_user_preference(selected_user, {"has_seen_ui_2_0": True})

        if new_unlocks:
            st.session_state["celebration_unlocks"] = new_unlocks
            for item in new_unlocks:
                if item.get("reward_coins", 0) > 0:
                    insert_transaction(
                        selected_user, 
                        item["reward_coins"], 
                        "shop", 
                        {
                            "item": item.get("reward_item_key", f"reward_{item.get('title')}"), 
                            "reward_unlock": item.get('title'),
                            "monarch_crown": item.get("title") if item.get("type") == "monarch" else None
                        }
                    )

        if "tea" in drink_name.lower():
            st.snow()
        else:
            st.balloons()
        st.success(f"**{temp_name} {drink_name} Logged in {city_name}, {get_option_from_code(country_code)}!** (+10 🪙)")
        time.sleep(1.0)
        st.rerun()
    except Exception as e:
        st.error(f"Error logging drink: {e}")

# --- 2. Hero Quick-Tap Beverage Section (Coffee & Tea - Hot & Iced) ---
st.subheader("⚡ Log Your Beverage")

if "coffee_break" in active_perks.get(selected_user, []):
    st.error("🚫 You are on a mandatory Coffee Break! You cannot log drinks right now.")
else:
    # --- LOCATION SELECTOR (Country & City) ---
    loc_c1, loc_c2 = st.columns([1.1, 1])
    with loc_c1:
        default_country_code = prefs.get(selected_user, {}).get("default_country", get_user_default_country(selected_user))
        default_option = get_option_from_code(default_country_code)
        all_options = get_country_options()
        
        selected_country_option = st.selectbox(
            "🌍 Location (Country)", 
            all_options, 
            index=all_options.index(default_option) if default_option in all_options else 0,
            key="beverage_log_country_select",
            help="Choose the country where you are enjoying your brew."
        )
        selected_country_code = get_country_code_from_option(selected_country_option)
        
    with loc_c2:
        default_city = prefs.get(selected_user, {}).get("default_city", get_user_default_city(selected_user))
        available_cities = list(get_cities_for_country(selected_country_code))
        if default_city and default_city not in available_cities and selected_country_code == default_country_code:
            available_cities.insert(0, default_city)
        available_cities.append("✍️ Custom City...")
        
        city_default_idx = available_cities.index(default_city) if default_city in available_cities else 0
        selected_city_choice = st.selectbox(
            "🏙️ City", 
            available_cities, 
            index=city_default_idx,
            key=f"beverage_log_city_select_{selected_country_code}",
            help="Choose or enter the city for this brew."
        )
        
        if selected_city_choice == "✍️ Custom City...":
            custom_city_input = st.text_input("Enter City Name:", placeholder="e.g. Oxford, Florence, Kyoto...")
            selected_city = custom_city_input.strip() if custom_city_input.strip() else available_cities[0]
        else:
            selected_city = selected_city_choice
            
    selected_city = normalize_city_name(selected_city)

    b_col1, b_col2 = st.columns(2)
    
    # ☕ COFFEE ZONE
    with b_col1:
        with st.container(border=True):
            st.markdown("### ☕ Coffee Section")
            st.caption("Rich roast &bull; **95mg** Caffeine &bull; 🪙 `+10 Coins`")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("☕ Hot Coffee", key="btn_hot_coffee", use_container_width=True):
                    handle_drink_log(1, "Coffee", "Hot", selected_country_code, selected_city)
            with c_btn2:
                if st.button("🧊 Iced Coffee", key="btn_iced_coffee", use_container_width=True):
                    handle_drink_log(3, "Coffee", "Iced", selected_country_code, selected_city)
                    
    # 🍵 TEA ZONE
    with b_col2:
        with st.container(border=True):
            st.markdown("### 🍵 Tea Section")
            st.caption("Fresh steep &bull; **35mg** Caffeine &bull; 🪙 `+10 Coins`")
            
            t_btn1, t_btn2 = st.columns(2)
            with t_btn1:
                if st.button("🍵 Hot Tea", key="btn_hot_tea", use_container_width=True):
                    handle_drink_log(2, "Tea", "Hot", selected_country_code, selected_city)
            with t_btn2:
                if st.button("🧊 Iced Tea", key="btn_iced_tea", use_container_width=True):
                    handle_drink_log(4, "Tea", "Iced", selected_country_code, selected_city)

st.divider()

# --- 3. Today's Scoreboard & Caffeine Meter ---
dash_col1, dash_col2 = st.columns([1, 1])

with dash_col1:
    with st.container(border=True):
        st.markdown("#### ⚡ Daily Velocity & Combustion Meter")
        render_circular_caffeine_gauge(user_caff_today, max_mg=400)

with dash_col2:
    with st.container(border=True):
        st.markdown("#### ⚔️ Today's Beverage Battle")
        render_coffee_tea_fuel_bar(today_coffees, today_teas)
        st.markdown(
            f"**☕ Coffee Breakdown:** `{today_hot_coffees} Hot` · `{today_iced_coffees} Iced` &nbsp;|&nbsp; "
            f"**🍵 Tea Breakdown:** `{today_hot_teas} Hot` · `{today_iced_teas} Iced`"
        )

st.divider()

# --- 4. Crew Leaderboard & Status ---
st.subheader("👥 Crew Leaderboard")
p_cols = st.columns(len(users))

for idx, user in enumerate(users):
    c_score = coffee_scores.get(user, 0)
    t_score = tea_scores.get(user, 0)
    
    user_pref = prefs.get(user, {})
    custom_title = resolve_user_title(user, prefs, trophies)
    custom_emoji = user_pref.get("emoji", "☕")
    
    # Calculate user's today caffeine
    caff = 0
    if not today_df.empty:
        user_logs = today_df[today_df["user_name"] == user]
        caff = (int(user_logs[user_logs["drink_id"].isin([1, 3])]["value"].sum()) * 95) + (int(user_logs[user_logs["drink_id"].isin([2, 4])]["value"].sum()) * 35)
        
    prog_val = min(caff, 400) / 400.0
    u_streak = trophies.get("streaks", {}).get(user, 0)
    is_fire = caff >= 400
    
    with p_cols[idx]:
        with st.container(border=True):
            st.markdown(f"### {custom_emoji} {user}")
            st.caption(f"🏷️ **{custom_title}**")
            
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"☕ `{c_score}` | 🍵 `{t_score}`")
            with m2:
                st.markdown(f"🪙 `{coin_balances.get(user, 0):,}` Coins")
                
            perks = active_perks.get(user, [])
            if perks:
                st.caption(f"🎒 Perks: **{', '.join(perks)}**")
                
            st.caption(f"🔥 Streak: **{u_streak}d** &bull; Velocity: **{caff}mg** {'🔥 `[ON FIRE!]`' if is_fire else ''}")
            st.progress(prog_val)

st.divider()

# --- 5. Live Activity Feed & Quick Links ---
feed_col, nav_col = st.columns([3, 2])

with feed_col:
    with st.container(border=True):
        st.markdown("#### 📡 Real-time Activity Feed")
        # Pull recent activity directly from clicks table (df)
        if not df.empty:
            recent_clicks = df.sort_values(by="created_at", ascending=False).head(5)
            for _, row in recent_clicks.iterrows():
                u = row["user_name"]
                did = row.get("drink_id", 1)
                
                if did == 1:
                    d = "Hot Coffee ☕"
                elif did == 3:
                    d = "Iced Coffee 🧊☕"
                elif did == 2:
                    d = "Hot Tea 🍵"
                elif did == 4:
                    d = "Iced Tea 🧊🍵"
                else:
                    d = "Beverage ☕"
                    
                # Extract location from row or JSON column
                c_code = None
                c_city = None
                if "location" in row and isinstance(row["location"], dict):
                    c_code = row["location"].get("country")
                    c_city = row["location"].get("city")
                if not c_code and "country" in row and pd.notna(row["country"]):
                    c_code = row["country"]
                if not c_city and "city" in row and pd.notna(row["city"]):
                    c_city = row["city"]

                # Privacy Setting Check for User: share_live_location (defaults to True)
                user_share_loc = prefs.get(u, {}).get("share_live_location", True)
                loc_html = ""
                if user_share_loc and c_code:
                    c_city_display = c_city or get_cities_for_country(c_code)[0]
                    c_info = TRAVEL_COUNTRIES.get(c_code, {})
                    c_name = c_info.get("name", c_code)
                    loc_html = f" in **{c_city_display}, {c_name}** {get_flag_img_html(c_code, 16, 12)}"
                
                t = row["created_at"]
                diff = now - t
                mins = int(diff.total_seconds() / 60)
                if mins < 1:
                    time_str = "Just now"
                elif mins < 60:
                    time_str = f"{mins}m ago"
                elif mins < 1440:
                    time_str = f"{mins // 60}h ago"
                else:
                    time_str = t.strftime("%b %d, %H:%M")
                
                st.markdown(f"- **{u}** enjoyed a **{d}**{loc_html} &bull; *{time_str}*", unsafe_allow_html=True)
        else:
            st.write("No activity recorded yet.")

with nav_col:
    with st.container(border=True):
        st.markdown("#### 🧭 Quick App Navigation")
        n1, n2 = st.columns(2)
        with n1:
            st.page_link("pages/1_📈_Graphs!_Graphs!_Graphs!.py", label="Analytics & Charts", icon="📈")
            st.page_link("pages/2_🏆_Trophy_Room.py", label="Trophies & Badges", icon="🏆")
        with n2:
            st.page_link("pages/4_🌍_World_Explorer.py", label="World Explorer", icon="🌍")
            st.page_link("pages/3_🎨_Theme_Shop.py", label="Theme Boutique", icon="🎨")
            st.page_link("pages/99_⚙️_Settings.py", label="Settings", icon="⚙️")
