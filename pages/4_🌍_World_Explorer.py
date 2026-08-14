import streamlit as st
import pandas as pd
from feature_flags import is_unlocked, is_dev_mode, get_countdown_text
from world_data import (
    TRAVEL_COUNTRIES, 
    DEFAULT_COUNTRY, 
    get_user_default_country,
    get_user_default_city,
    get_city_coordinates,
    get_option_from_code,
    get_flag_img_html,
    compute_passport_stats, 
    get_travel_leaderboard
)
from database import get_data, get_transactions
from data_processing import (
    process_raw_data, 
    get_user_preferences, 
    get_coin_balances, 
    get_gamification_metrics, 
    resolve_user_title
)
from utils import enforce_user_identity
from components.ui import inject_custom_css, render_app_header

# 1. Page Configuration
st.set_page_config(page_title="World Explorer", page_icon="🌍", layout="wide")

users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

# 2. Guard Pattern — Fer has automatic dev bypass
if not is_unlocked("world_update", dev_bypass=is_dev_mode(selected_user)):
    st.markdown(f"### {get_countdown_text('world_update')}")
    st.info("The 🌍 **World Update** is scheduled to unlock on **September 1, 2026**! Preview is available for Fer or via `?dev=1`.")
    st.stop()

# 3. Data Loading & Styling
data = get_data()
transactions = get_transactions()
df, df_coffee, df_tea, _, _ = process_raw_data(data, users)
trophies = get_gamification_metrics(df_coffee, df_tea, users, transactions=transactions)
coin_balances = get_coin_balances(df, transactions, users)
prefs = get_user_preferences(transactions, users)

user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")
inject_custom_css(user_theme, user_style, user=selected_user)

user_coins = coin_balances.get(selected_user, 0)
user_streak = trophies.get("streaks", {}).get(selected_user, 0)
user_emoji = prefs.get(selected_user, {}).get("emoji", "☕")
user_title = resolve_user_title(selected_user, prefs, trophies)

# 4. App Header
render_app_header(
    selected_user=selected_user,
    coin_balance=user_coins,
    streak_days=user_streak,
    custom_emoji=user_emoji,
    custom_title=user_title
)

default_country = prefs.get(selected_user, {}).get("default_country", get_user_default_country(selected_user))
default_city = prefs.get(selected_user, {}).get("default_city", get_user_default_city(selected_user))
passport = compute_passport_stats(transactions or [], selected_user, default_country, default_city)
home_info = TRAVEL_COUNTRIES.get(default_country, TRAVEL_COUNTRIES.get(DEFAULT_COUNTRY))

st.title(f"🌍 World Explorer — {selected_user}'s Travel Passport")
st.caption(f"Track the global footprint of your coffee & tea adventures. Home Base: {get_flag_img_html(default_country, 20, 14)} **{default_city}, {home_info['name']}**", unsafe_allow_html=True)
st.divider()

# --- 1. Interactive Folium World Map with City Pins ---
st.subheader("🗺️ Global Travel Footprint")

try:
    import folium
    from streamlit_folium import st_folium

    # Base coordinates centered around home city
    home_lat, home_lon = get_city_coordinates(default_country, default_city)

    m = folium.Map(
        location=[home_lat, home_lon],
        zoom_start=2 if len(passport["cities_visited"]) > 1 else 4,
        tiles="CartoDB positron",
        prefer_canvas=True
    )

    # Plot all visited cities
    plotted_locations = set()
    for (c_code, c_city), count in passport["city_counts"].items():
        c_lat, c_lon = get_city_coordinates(c_code, c_city)
        c_info = TRAVEL_COUNTRIES.get(c_code, {"name": c_code, "flag": "🏳️", "continent": "Global"})
        is_home_city = (c_code == default_country and c_city.lower() == default_city.lower())
        
        # Slight jitter if multiple unique entries share exact coordinates
        loc_key = (round(c_lat, 3), round(c_lon, 3))
        if loc_key in plotted_locations:
            c_lat += 0.02
            c_lon += 0.02
        plotted_locations.add(loc_key)

        if is_home_city:
            folium.Marker(
                location=[c_lat, c_lon],
                popup=folium.Popup(f"<b>🏠 Home Base: {c_city}, {c_info['name']} {c_info['flag']}</b><br/>{count} drinks logged", max_width=250),
                tooltip=f"🏠 Home Base: {c_city}, {c_info['name']}",
                icon=folium.Icon(color="blue", icon="home", prefix="fa")
            ).add_to(m)
        else:
            folium.Marker(
                location=[c_lat, c_lon],
                popup=folium.Popup(f"<b>✈️ {c_city}, {c_info['name']} {c_info['flag']}</b><br/>{count} drinks logged<br/><i>{c_info['continent']}</i>", max_width=250),
                tooltip=f"{c_info['flag']} {c_city}, {c_info['name']} ({count} drinks)",
                icon=folium.Icon(color="red", icon="coffee", prefix="fa")
            ).add_to(m)

    # If user hasn't logged yet, at least plot their home base
    if not passport["city_counts"]:
        folium.Marker(
            location=[home_lat, home_lon],
            popup=folium.Popup(f"<b>🏠 Home Base: {default_city}, {home_info['name']} {home_info['flag']}</b><br/>Ready for your first brew!", max_width=250),
            tooltip=f"🏠 Home Base: {default_city}, {home_info['name']}",
            icon=folium.Icon(color="blue", icon="home", prefix="fa")
        ).add_to(m)

    st_folium(m, width="100%", height=430)

except ImportError:
    st.info("💡 Interactive map requires `folium` and `streamlit-folium`. Country statistics and stamps are fully operational below!")

st.divider()

# --- 2. Passport Statistics Cards ---
st.subheader("🛂 Passport Statistics")

c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.container(border=True):
        st.metric(
            "🗺️ Countries Visited", 
            f"{len(passport['countries_visited'])} / {len(TRAVEL_COUNTRIES)}",
            delta=f"{len([c for c in passport['countries_visited'] if c != default_country])} Abroad"
        )
with c2:
    with st.container(border=True):
        st.metric(
            "🏙️ Cities Explored", 
            f"{len(passport['cities_visited'])} Cities",
            delta="Urban Footprint"
        )
with c3:
    with st.container(border=True):
        st.metric(
            "🌎 Continents Reached", 
            f"{len(passport['continents_reached'])} / 6",
            delta="Global Span"
        )
with c4:
    with st.container(border=True):
        st.metric(
            "✈️ Drinks Logged Abroad", 
            f"{passport['drinks_abroad']:,} Drinks",
            delta="Outside Home Base"
        )

c5, c6 = st.columns(2)
with c5:
    with st.container(border=True):
        mvf = passport["most_visited_foreign"]
        mvc = passport["most_visited_city"]
        
        top_dest_text = []
        if mvc:
            top_dest_text.append(f"🏙️ **Top City:** {mvc[0][1]} ({mvc[1]} drinks)")
        if mvf:
            top_dest_text.append(f"✈️ **Top Foreign Country:** {get_option_from_code(mvf[0])} ({mvf[1]} drinks)")
            
        if top_dest_text:
            st.markdown("#### 🏆 Top Destinations")
            for t in top_dest_text:
                st.write(t)
        else:
            st.metric("🏆 Top Destination", "Home Turf", "Log foreign drinks to expand!")
with c6:
    with st.container(border=True):
        st.metric(
            "📊 World Diversity Score", 
            f"{passport['diversity_score']:.2f}%", 
            delta=f"{len(passport['countries_visited'])} countries &bull; {len(passport['cities_visited'])} cities"
        )

st.divider()

# --- 3. Passport Stamps Collection Gallery (City & Country) ---
st.subheader("📬 Collected Passport Stamps")

city_items = sorted(passport["city_counts"].items(), key=lambda x: x[1], reverse=True)
if not city_items:
    st.info("No drinks logged with travel location yet. Log a beverage on the landing page to collect your first stamp!")
else:
    stamp_cols = st.columns(4)
    for idx, ((c_code, c_city), cnt) in enumerate(city_items):
        info = TRAVEL_COUNTRIES.get(c_code, {"name": c_code, "flag": "🏳️", "continent": "Unknown"})
        is_home = (c_code == default_country and c_city.lower() == default_city.lower())
        
        with stamp_cols[idx % 4]:
            with st.container(border=True):
                st.markdown(f"### {get_flag_img_html(c_code, 26, 20)} {c_city}", unsafe_allow_html=True)
                st.markdown(f"**{info['name']}** &bull; *{info['continent']}*")
                if is_home:
                    st.caption(f"🏠 **Home Base** &bull; `{cnt}` drinks")
                else:
                    st.caption(f"✈️ **Abroad** &bull; `{cnt}` drinks")

st.divider()

# --- 4. Travel Leaderboard ---
st.subheader("🏆 Crew Travel Leaderboard")
st.caption("Compare international reach, urban coverage, and passport diversity across the team.")

leaderboard = get_travel_leaderboard(transactions or [], users)
lb_df = pd.DataFrame(leaderboard)
lb_df.index = lb_df.index + 1
lb_df = lb_df.rename(columns={
    "user": "Explorer",
    "cities": "🏙️ Cities",
    "countries": "🗺️ Countries",
    "continents": "🌎 Continents",
    "drinks_abroad": "✈️ Drinks Abroad",
    "diversity": "📊 Diversity (%)"
})

st.dataframe(lb_df, use_container_width=True)
