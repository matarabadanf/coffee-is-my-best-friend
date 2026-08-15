import streamlit as st
import pandas as pd

from database import get_data, get_transactions, insert_transaction, get_preferences, save_user_preference
from data_processing import process_raw_data, get_coin_balances, get_gamification_metrics, get_user_titles, resolve_user_title, get_active_perks, get_user_preferences, get_unlocked_themes
from utils import verify_pin, is_pin_verified, enforce_user_identity
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
from components.ui import inject_custom_css, render_app_header

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

data = get_data()
transactions = get_transactions()
db_prefs = get_preferences()
df, df_coffee, df_tea, _, _ = process_raw_data(data, users)
trophies = get_gamification_metrics(df_coffee, df_tea, users, transactions=transactions)
coin_balances = get_coin_balances(df, transactions, users)

prefs = get_user_preferences(transactions, users, db_preferences=db_prefs)
user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")
inject_custom_css(user_theme, user_style, user=selected_user)

balance = coin_balances.get(selected_user, 0)
user_streak = trophies.get("streaks", {}).get(selected_user, 0)
user_emoji = prefs.get(selected_user, {}).get("emoji", "☕")
user_title = resolve_user_title(selected_user, prefs, trophies)

# Native App Header
render_app_header(
    selected_user=selected_user, 
    coin_balance=balance, 
    streak_days=user_streak, 
    custom_emoji=user_emoji, 
    custom_title=user_title
)

st.title("⚙️ Profile & Preferences")

# PIN Verification
if not is_pin_verified(selected_user):
    st.warning("Settings are locked. Please enter your PIN to access.")
    pin = st.text_input("Enter PIN:", type="password", key="settings_pin")
    if st.button("Unlock"):
        if verify_pin(selected_user, pin):
            st.success("Unlocked!")
            st.rerun()
        else:
            st.error("Incorrect PIN!")
    st.stop()

# --- Settings Content Below (Only visible if unlocked) ---
st.success("🔓 Settings Unlocked")

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔒 Lock Device", width="stretch"):
        st.session_state[f"pin_verified_time_{selected_user}"] = 0
        st.rerun()

st.write("---")

# Fetch Data
data = get_data()
transactions = get_transactions()
df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)
trophies = get_gamification_metrics(df_coffee, df_tea, users)
earned_titles = get_user_titles(selected_user, trophies, return_all=True)
active_perks = get_active_perks(transactions, users)
coin_balances = get_coin_balances(df, transactions, users)

st.header("🎨 Appearance")
with st.container(border=True):
    unlocked_themes = get_unlocked_themes(transactions, selected_user)
    user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
    if user_theme not in unlocked_themes:
        user_theme = "Latte (Light)"
    user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")
    if user_style not in ["Modern Flat", "Glassmorphism", "Neumorphism"]:
        user_style = "Modern Flat"
    
    theme = st.selectbox(
        "Active Theme (Colors)", 
        unlocked_themes, 
        index=unlocked_themes.index(user_theme) if user_theme in unlocked_themes else 0
    )
    ui_style = st.selectbox(
        "UI Style (Effects)", 
        ["Modern Flat", "Glassmorphism", "Neumorphism"], 
        index=["Modern Flat", "Glassmorphism", "Neumorphism"].index(user_style)
    )
    
    if st.button("Save Appearance", use_container_width=True):
        save_user_preference(selected_user, {"theme": theme, "ui_style": ui_style})
        st.success("Appearance saved! Refreshing...")
        st.rerun()

    st.caption("💡 *Looking for more themes? Unlock Caramel Macchiato, Strawberry Frappé, Taro Boba, Cyber Brew, and Velvet Mocha in the **🎨 Theme Shop**!*")

st.header("🏷️ Profile & Badges")
with st.container(border=True):
    p_col1, p_col2 = st.columns([1, 2])
    with p_col1:
        current_emoji = prefs.get(selected_user, {}).get("emoji", "☕")
        emoji = st.text_input("Avatar Emoji", max_chars=2, value=current_emoji, help="Single character/emoji representing you.")
    
    with p_col2:
        current_title = prefs.get(selected_user, {}).get("title")
        
        # Build titles list: Random Option first, then earned crowns, tier achievements, secrets, and base tags
        random_option = "🎲 Random Mystery Tag (Changes Every Visit)"
        title_options = [random_option] + earned_titles
        
        if not current_title or current_title not in title_options:
            default_idx = 0
        else:
            default_idx = title_options.index(current_title)
            
        selected_title = st.selectbox(
            "Active Title / Badge", 
            title_options, 
            index=default_idx,
            help="Showcase your unlocked achievements, monarch crowns, secret feats, or pick Random!"
        )
        
    st.caption(f"🏆 *You have **{len(earned_titles)}** unique titles and achievement badges unlocked!*")
    
    if st.button("Save Profile Settings", use_container_width=True):
        save_user_preference(selected_user, {"emoji": emoji, "title": selected_title})
        st.success("Profile saved! Refreshing...")
        st.rerun()

st.header("🌍 Location Settings")
with st.container(border=True):
        st.markdown("### 🌍 Home Base Location")
        st.caption("Your default physical location for drink logs and home passport registry.")
        
        country_info = TRAVEL_COUNTRIES.get(default_country_code, {"name": default_country_code, "flag": "🏳️"})
        country_flag = country_info.get("flag", "🏳️")
        st.caption(f"Current Home Base: {country_flag} **{default_city}, {country_info.get('name', default_country_code)}**")
        
        set_col1, set_col2 = st.columns(2)
        with set_col1:
            default_option = get_option_from_code(default_country_code)
            all_options = get_country_options()
            
            selected_country_option = st.selectbox(
                "Default Home Country",
                all_options,
                index=all_options.index(default_option) if default_option in all_options else 0,
                key="settings_default_country_select",
                help="Sets your pre-selected country when logging beverages."
            )
            new_country_code = get_country_code_from_option(selected_country_option)
            
        with set_col2:
            available_cities = list(get_cities_for_country(new_country_code))
            if default_city and default_city not in available_cities and new_country_code == default_country_code:
                available_cities.insert(0, default_city)
            available_cities.append("✍️ Custom City...")
            
            city_idx = available_cities.index(default_city) if default_city in available_cities else 0
            selected_city_choice = st.selectbox(
                "Default Home City",
                available_cities,
                index=city_idx,
                key=f"settings_default_city_select_{new_country_code}",
                help="Sets your pre-selected city when logging beverages."
            )
            
            if selected_city_choice == "✍️ Custom City...":
                custom_city = st.text_input("Enter Custom City:", value=default_city if default_city not in available_cities else "", placeholder="e.g. Oxford, Plzen...")
                new_city_name = custom_city.strip() if custom_city.strip() else available_cities[0]
            else:
                new_city_name = selected_city_choice
                
        new_city_name = normalize_city_name(new_city_name)
        
        st.divider()
        st.markdown("#### 🔒 Location Privacy")
        st.caption("Control whether your physical city and country are broadcasted in the real-time activity feed.")
        
        current_share_loc = prefs.get(selected_user, {}).get("share_live_location", True)
        share_loc_toggle = st.toggle(
            "📡 Broadcast location in real-time activity feed",
            value=current_share_loc,
            help="When enabled, your live drink logs in the feed will show your city and flag. When disabled, your location is kept private from the live feed (your drinks are still plotted on the World Explorer map)."
        )
        
        if st.button("💾 Save Location & Privacy Settings", use_container_width=True):
            save_user_preference(selected_user, {
                "default_country": new_country_code,
                "default_city": new_city_name,
                "share_live_location": share_loc_toggle
            })
            st.success(f"Location & privacy settings saved for {selected_user}! Refreshing...")
            st.rerun()

st.header("🎒 Active Inventory & Perks")
with st.container(border=True):
    user_perks = active_perks.get(selected_user, [])
    if not user_perks:
        st.info("You don't have any active perks. Visit the **🛒 Shop** to equip streak freezes and boosts!")
    else:
        for perk in user_perks:
            st.markdown(f"- **{perk['item']}** (Expires: {pd.to_datetime(perk['expires_at']).strftime('%b %d, %H:%M') if perk.get('expires_at') else 'Never'})")

