import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Import refactored modules
from database import get_data, insert_click, get_transactions, insert_transaction
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
from world_data import get_country_options, get_option_from_code, get_country_code_from_option, get_user_default_country
from feature_flags import is_unlocked, is_dev_mode
from components.ui import (
    inject_custom_css, 
    render_app_header, 
    render_daily_fact_quote,
    render_circular_caffeine_gauge, 
    render_coffee_tea_fuel_bar
)

# 1. Page Configuration
st.set_page_config(page_title="Coffee is my best friend", page_icon="☕", layout="wide")

# User Configuration
users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

# 2. Data Fetching & Processing
data = get_data()
transactions = get_transactions()
df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)

prefs = get_user_preferences(transactions, users)
user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")

# Inject Active Theme & CSS
inject_custom_css(user_theme, user_style)

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

now = pd.Timestamp.now(tz="Europe/Madrid") if df.empty else pd.Timestamp.now(tz="UTC").tz_convert("Europe/Madrid")

# --- What's New Announcement Banner (Active during launch week: Aug 14 - Aug 21, 2026) ---
launch_week_end = pd.Timestamp("2026-08-21 23:59:59", tz="Europe/Madrid")
if now <= launch_week_end:
    with st.expander("✨ **What's New in Version 2.0 & Launch Week PIN Setup! (Tap to expand)**", expanded=True):
        w1, w2, w3 = st.columns(3)
        with w1:
            st.markdown("""
            #### 🎨 **Fresh Look & Atmosphere**
            - ✨ **Smoother & Sleeker Interface**: A completely refreshed visual experience that is cleaner, smoother, and much nicer to use every day.
            - 🛍️ **Theme Boutique**: Unlock **Espresso (Dark)** for just 🪙 **20 Coins** as a tutorial unlock (plus 6 handcrafted themes & 3 visual styles) in [`pages/3_🎨_Theme_Shop.py`](file:///wsl.localhost/Ubuntu-26.04/home/matis-ubuntu/bin/coffee-is-my-best-friend/pages/3_🎨_Theme_Shop.py).
            """)
        with w2:
            st.markdown("""
            #### ☕ **Beverage & Velocity Engine**
            - 🧊 **Hot vs. Iced Split**: Log **Hot** and **Iced** versions of Coffee & Tea with full temperature breakdown!
            - ⚡ **High-Speed Velocity Meter**: No health lectures—pure speed! Reaching 400+ mg triggers an epic **🔥 ON-FIRE! Warp Speed** state.
            - 🧭 **Unified App Header**: Live Madrid time context, active streaks, and coin balances.
            """)
        with w3:
            st.markdown("""
            #### 🏆 **Gamification & Secrets**
            - 👑 **Global Monarch Crowns**: Gender-neutral crowns including **🧊 Sub-Zero** and **🔥 Combustion** (Fer with 9 On-Fire days)!
            - 🎖️ **11 Mastery Tracks**: Calibrated progress bars for Total, Espresso, Tea, Sub-Zero, Streaks, and Combustion.
            - 🕵️ **11 Arcane Secrets**: Concealed achievements and cryptic riddles hidden within Tab 3 of the Trophy Room for those clever enough to uncover them!
            """)
        
        st.info("💡 **Pro-Tip & Direct Bookmark:** You can bookmark `/?user=Cris`, `/?user=Bea`, or `/?user=Fer` in your browser to skip the profile selector and open straight into your dashboard!")
        
        st.divider()
        
        # --- Friendly PIN Hasher Tool for Launch Week ---
        st.markdown("### 🔐 **Launch Week Security: Setup Your Profile PIN**")
        st.markdown("""
        **Why is a PIN required?**
        - 🛡️ **Profile Customization**: Your custom titles, theme aesthetics, and emojis are tied to your personal identity so no one can accidentally overwrite your setup.
        - 🪙 **Coin Economy & Bot Shield**: **Coins WILL be heavily relevant in upcoming updates!** (Powering upcoming perks, mystery drops, shop items, and interactive features). When spending coins, your PIN acts as a firewall so random web bots or visitors cannot tamper with your account or drain your hard-earned coin treasury!
        """)
        
        pin_col1, pin_col2 = st.columns([1, 2])
        with pin_col1:
            desired_pin = st.text_input(
                f"Enter secret PIN for **{selected_user}**:", 
                type="password", 
                placeholder="4-6 digits or secret word",
                key="launch_pin_input"
            )
        
        with pin_col2:
            if desired_pin:
                import hashlib
                pin_hash = hashlib.sha256(desired_pin.encode()).hexdigest()
                st.markdown(f"**Generated SHA-256 Hash for `{selected_user}`:**")
                st.code(f'{selected_user} = "{pin_hash}"', language="toml")
                st.caption("📋 *Copy the line above and send it to the admin (or add it directly to `.streamlit/secrets.toml` under `[pins]`)*")
            else:
                st.info("💡 Type a PIN on the left to instantly generate your copyable SHA-256 security hash.")
        
        st.caption("📢 *This release briefing and PIN helper will remain pinned to the landing page for the next 7 days.*")

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

def handle_drink_log(drink_id, drink_name, temp_name, country_code):
    if last_click_time and (now - last_click_time).total_seconds() < 60:
        st.warning(f"Wait {int(60 - (now - last_click_time).total_seconds())}s before logging again!")
        return
    try:
        # 1. Insert Click Record (1: Hot Coffee, 3: Iced Coffee, 2: Hot Tea, 4: Iced Tea)
        insert_click(selected_user, 1, drink_id)
        # 2. Insert Coin Transaction with explicit temperature and country metadata
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
        if "tea" in drink_name.lower():
            st.snow()
        else:
            st.balloons()
        st.success(f"**{temp_name} {drink_name} Logged in {get_option_from_code(country_code)}!** (+10 🪙)")
        time.sleep(1.2)
        st.rerun()
    except Exception as e:
        st.error(f"Error logging drink: {e}")

# --- 2. Hero Quick-Tap Beverage Section (Coffee & Tea - Hot & Iced) ---
st.subheader("⚡ Log Your Beverage")

if "coffee_break" in active_perks.get(selected_user, []):
    st.error("🚫 You are on a mandatory Coffee Break! You cannot log drinks right now.")
else:
    # --- COUNTRY SELECTOR WITH FLAGS ---
    default_country_code = prefs.get(selected_user, {}).get("default_country", get_user_default_country(selected_user))
    default_option = get_option_from_code(default_country_code)
    all_options = get_country_options()
    
    selected_option = st.selectbox(
        "📍 Drinking in:",
        all_options,
        index=all_options.index(default_option) if default_option in all_options else 0,
        key="country_drink_selector",
        help="Select the country where you are physically drinking this cup."
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
        if not df.empty:
            recent = df.sort_values(by="created_at", ascending=False).head(5)
            for _, row in recent.iterrows():
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
                
                st.markdown(f"- **{u}** enjoyed a **{d}** &bull; *{time_str}*")
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
