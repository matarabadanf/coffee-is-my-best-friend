import streamlit as st
import pandas as pd
from feature_flags import is_unlocked, is_dev_mode, get_countdown_text
from world_data import (
    TRAVEL_COUNTRIES, 
    DEFAULT_COUNTRY, 
    USER_MAP_COLORS,
    get_user_default_country,
    get_user_default_city,
    get_city_coordinates,
    get_option_from_code,
    get_flag_img_html,
    compute_passport_stats, 
    get_travel_leaderboard
)
from database import get_data, get_transactions, get_preferences
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

# 2. Guard Pattern
if not is_unlocked("world_update"):
    st.markdown(f"### {get_countdown_text('world_update')}")
    st.info("The 🌍 **World Update** is scheduled to unlock **Tonight at Midnight (00:00 Madrid Time)**!")
    st.stop()

# 3. Data Loading & Styling
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

st.title("🌍 World Explorer — Global Beverage Footprint")
st.caption("Explore international travel and coffee & tea adventures across the team.")

# --- Filter Toolbar (Explorer & Beverage Type) ---
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    explorer_options = ["👥 All Crew (Combined)", "Cris", "Bea", "Fer"]
    selected_explorer_option = st.selectbox(
        "👤 Explorer View:",
        explorer_options,
        index=0,
        key="world_explorer_user_filter",
        help="Select 'All Crew' to view combined team logs, or pick an explorer for individual passport stats."
    )
with filter_col2:
    beverage_options = ["☕ & 🍵 All Beverages", "☕ Coffee Only", "🍵 Tea Only"]
    selected_beverage_option = st.selectbox(
        "☕ Beverage Filter:",
        beverage_options,
        index=0,
        key="world_explorer_beverage_filter",
        help="Filter the map and passport statistics by beverage category."
    )

active_user_filter = None if "All Crew" in selected_explorer_option else selected_explorer_option
drink_type_filter = "all"
if "Coffee Only" in selected_beverage_option:
    drink_type_filter = "coffee"
elif "Tea Only" in selected_beverage_option:
    drink_type_filter = "tea"

# Compute passport statistics with active filters
user_def_country = prefs.get(active_user_filter, {}).get("default_country", get_user_default_country(active_user_filter)) if active_user_filter else DEFAULT_COUNTRY
user_def_city = prefs.get(active_user_filter, {}).get("default_city", get_user_default_city(active_user_filter)) if active_user_filter else "Madrid"

passport = compute_passport_stats(
    transactions or [], 
    user=active_user_filter, 
    default_country=user_def_country, 
    default_city=user_def_city,
    drink_type=drink_type_filter,
    clicks_data=data
)

# Subtitle banner
if active_user_filter:
    home_info = TRAVEL_COUNTRIES.get(user_def_country, TRAVEL_COUNTRIES.get(DEFAULT_COUNTRY, {"name": user_def_country, "flag": "🏳️"}))
    home_flag = home_info.get("flag", "🏳️")
    st.info(f"Viewing **{active_user_filter}**'s Passport ({selected_beverage_option}) &bull; Home Base: {home_flag} **{user_def_city}, {home_info['name']}**")
else:
    st.info(f"Viewing **All Crew Combined** ({selected_beverage_option}) &bull; Explorers: **Cris** 🇨🇿, **Bea** 🇳🇱, **Fer** 🇫🇷")

st.divider()

# --- 1. Interactive Folium World Map with User Colors ---
st.subheader("🗺️ Interactive Travel Map")

# Map Legend
st.markdown("""
<div style="display: flex; gap: 12px; align-items: center; margin-bottom: 10px; flex-wrap: wrap;">
    <span style="font-weight: 600; font-size: 13px;">Explorer Pin Colors:</span>
    <span style="background-color: #0284C7; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">🟦 Cris</span>
    <span style="background-color: #F43F5E; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">🟥 Bea</span>
    <span style="background-color: #663399; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">🟪 Fer</span>
</div>
""", unsafe_allow_html=True)

try:
    import folium
    from streamlit_folium import st_folium

    # Center map on Europe/Madrid
    m = folium.Map(
        location=[48.0, 10.0],
        zoom_start=3,
        tiles="CartoDB positron",
        prefer_canvas=True
    )

    def create_custom_icon(user_name, count=1, is_home=False, drink_filter="all", drink_breakdown=None):
        color = USER_MAP_COLORS.get(user_name, "#663399")
        
        # Determine icon symbol: strictly tea 🍵 if tea only, coffee ☕ if coffee only, or majority
        if drink_filter == "tea":
            symbol = "🍵"
        elif drink_filter == "coffee":
            symbol = "☕"
        elif drink_breakdown:
            tea_cnt = drink_breakdown.get("tea", 0)
            caff_cnt = drink_breakdown.get("coffee", 0)
            if tea_cnt > 0 and caff_cnt == 0:
                symbol = "🍵"
            elif caff_cnt > 0 and tea_cnt == 0:
                symbol = "☕"
            elif tea_cnt > caff_cnt:
                symbol = "🍵"
            elif caff_cnt > tea_cnt:
                symbol = "☕"
            else:
                symbol = "🏠" if is_home else "☕"
        elif is_home:
            symbol = "🏠"
        else:
            symbol = "☕"

        html = f"""
        <div style="
            background-color: {color};
            color: white;
            border: 2px solid white;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 3px 6px rgba(0,0,0,0.35);
            cursor: pointer;
            position: relative;
            transition: transform 0.18s ease-out, box-shadow 0.18s ease-out;
        " onmouseover="this.style.transform='scale(1.22)'; if(this.parentElement) this.parentElement.style.zIndex='999999';" onmouseout="this.style.transform='scale(1)'; if(this.parentElement) this.parentElement.style.zIndex='';" title="{user_name}: {count} drinks">
            {symbol}
            <span style="
                position: absolute;
                top: -6px;
                right: -6px;
                background: #0f172a;
                color: #f8fafc;
                border-radius: 10px;
                padding: 1px 5px;
                font-size: 10px;
                font-weight: 700;
                border: 1px solid white;
                line-height: 1.2;
                box-shadow: 0 1px 4px rgba(0,0,0,0.4);
            ">{count}</span>
        </div>
        """
        return folium.DivIcon(html=html, icon_size=(32, 32), icon_anchor=(16, 16))

    city_latest_time = passport.get("city_latest_time", {})
    city_user_latest_time = passport.get("city_user_latest_time", {})
    default_ts = pd.Timestamp("2020-01-01", tz="UTC")

    markers_to_plot = []

    # Prepare city markers
    if active_user_filter is None:
        # All Crew Mode: Plot pins for each user who drank in each city
        for (c_code, c_city), user_breakdown in passport.get("city_users_breakdown", {}).items():
            base_lat, base_lon = get_city_coordinates(c_code, c_city)
            c_info = TRAVEL_COUNTRIES.get(c_code, {"name": c_code, "flag": "🏳️", "continent": "Global"})
            
            user_list = list(user_breakdown.items())
            num_users = len(user_list)
            
            for u_idx, (u_name, u_cnt) in enumerate(user_list):
                u_home_country = get_user_default_country(u_name)
                u_home_city = get_user_default_city(u_name)
                is_home = (c_code == u_home_country and c_city.lower() == u_home_city.lower())
                
                # Small offset if multiple users drank in the same city
                offset_lat = (u_idx - (num_users - 1) / 2) * 0.02 if num_users > 1 else 0.0
                offset_lon = (u_idx - (num_users - 1) / 2) * 0.02 if num_users > 1 else 0.0
                
                pin_lat = base_lat + offset_lat
                pin_lon = base_lon + offset_lon
                
                u_breakdown = passport.get("city_user_drink_types", {}).get((c_code, c_city), {}).get(u_name, {"coffee": 0, "tea": 0})
                c_cnt = u_breakdown.get("coffee", 0)
                t_cnt = u_breakdown.get("tea", 0)
                
                if c_cnt > 0 and t_cnt > 0:
                    drink_detail = f"<b>{c_cnt}</b> ☕ coffees &bull; <b>{t_cnt}</b> 🍵 teas"
                    tooltip_detail = f"☕ {c_cnt} coffees, 🍵 {t_cnt} teas"
                elif t_cnt > 0:
                    drink_detail = f"<b>{t_cnt}</b> 🍵 {'tea' if t_cnt == 1 else 'teas'}"
                    tooltip_detail = f"🍵 {t_cnt} teas"
                else:
                    tot = c_cnt or u_cnt
                    drink_detail = f"<b>{tot}</b> ☕ {'coffee' if tot == 1 else 'coffees'}"
                    tooltip_detail = f"☕ {tot} coffees"

                u_color = USER_MAP_COLORS.get(u_name, "#663399")
                popup_html = f"""
                <div style="font-family: sans-serif; min-width: 180px;">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                        <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:{u_color};"></span>
                        <b>{u_name}</b>
                    </div>
                    <b>{c_city}, {c_info['name']} {c_info['flag']}</b><br/>
                    <span>{'🏠 Home Base &bull; ' if is_home else '✈️ '}{drink_detail}</span><br/>
                    <small style="color: #64748b;">{c_info['continent']}</small>
                </div>
                """
                
                # Fetch latest beverage timestamp for this user in this city
                u_ts = city_user_latest_time.get((c_code, c_city), {}).get(u_name, city_latest_time.get((c_code, c_city), default_ts))

                markers_to_plot.append({
                    "lat": pin_lat,
                    "lon": pin_lon,
                    "popup": popup_html,
                    "tooltip": f"{u_name} in {c_city}, {c_info['name']} ({tooltip_detail})",
                    "user_name": u_name,
                    "count": u_cnt,
                    "is_home": is_home,
                    "drink_breakdown": u_breakdown,
                    "timestamp": u_ts
                })
    else:
        # Single User Mode
        u_home_country = get_user_default_country(active_user_filter)
        u_home_city = get_user_default_city(active_user_filter)
        
        for (c_code, c_city), cnt in passport["city_counts"].items():
            c_lat, c_lon = get_city_coordinates(c_code, c_city)
            c_info = TRAVEL_COUNTRIES.get(c_code, {"name": c_code, "flag": "🏳️", "continent": "Global"})
            is_home = (c_code == u_home_country and c_city.lower() == u_home_city.lower())
            
            u_breakdown = passport.get("city_drink_types", {}).get((c_code, c_city), {"coffee": 0, "tea": 0})
            c_cnt = u_breakdown.get("coffee", 0)
            t_cnt = u_breakdown.get("tea", 0)
            
            if c_cnt > 0 and t_cnt > 0:
                drink_detail = f"<b>{c_cnt}</b> ☕ coffees &bull; <b>{t_cnt}</b> 🍵 teas"
                tooltip_detail = f"☕ {c_cnt} coffees, 🍵 {t_cnt} teas"
            elif t_cnt > 0:
                drink_detail = f"<b>{t_cnt}</b> 🍵 {'tea' if t_cnt == 1 else 'teas'}"
                tooltip_detail = f"🍵 {t_cnt} teas"
            else:
                tot = c_cnt or cnt
                drink_detail = f"<b>{tot}</b> ☕ {'coffee' if tot == 1 else 'coffees'}"
                tooltip_detail = f"☕ {tot} coffees"

            u_color = USER_MAP_COLORS.get(active_user_filter, "#663399")
            popup_html = f"""
            <div style="font-family: sans-serif; min-width: 180px;">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                    <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:{u_color};"></span>
                    <b>{active_user_filter}</b>
                </div>
                <b>{c_city}, {c_info['name']} {c_info['flag']}</b><br/>
                <span>{'🏠 Home Base &bull; ' if is_home else '✈️ '}{drink_detail}</span><br/>
                <small style="color: #64748b;">{c_info['continent']}</small>
            </div>
            """
            
            c_ts = city_latest_time.get((c_code, c_city), default_ts)

            markers_to_plot.append({
                "lat": c_lat,
                "lon": c_lon,
                "popup": popup_html,
                "tooltip": f"{active_user_filter} in {c_city}, {c_info['name']} ({tooltip_detail})",
                "user_name": active_user_filter,
                "count": cnt,
                "is_home": is_home,
                "drink_breakdown": u_breakdown,
                "timestamp": c_ts
            })

    # Sort markers chronologically ascending: older coffees added first, latest added last & given highest z_index_offset
    markers_to_plot.sort(key=lambda m_item: m_item["timestamp"])

    for rank_idx, pin in enumerate(markers_to_plot):
        # Calculate positive z_index_offset: latest coffee gets highest z-index
        z_offset = int(rank_idx * 100 + 10)
        
        folium.Marker(
            location=[pin["lat"], pin["lon"]],
            popup=folium.Popup(pin["popup"], max_width=280),
            tooltip=pin["tooltip"],
            z_index_offset=z_offset,
            icon=create_custom_icon(
                pin["user_name"], 
                count=pin["count"], 
                is_home=pin["is_home"], 
                drink_filter=drink_type_filter, 
                drink_breakdown=pin["drink_breakdown"]
            )
        ).add_to(m)

    st_folium(m, width="100%", height=450, returned_objects=[])

except ImportError:
    st.info("💡 Interactive map requires `folium` and `streamlit-folium`. Country statistics and stamps are fully operational below!")

st.divider()

# --- 2. Passport Statistics Cards (Filtered) ---
st.subheader("🛂 Passport Statistics")

c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.container(border=True):
        terrestrial_total = len([c for c in TRAVEL_COUNTRIES if c != "PLANE"])
        st.metric(
            "🗺️ Countries Visited", 
            f"{len(passport['countries_visited'])} / {terrestrial_total}",
            delta=f"{len([c for c in passport['countries_visited'] if c != user_def_country])} Abroad"
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
        in_flight_cnt = passport.get("in_flight_drinks", 0)
        in_flight_txt = f" ({in_flight_cnt} ✈️ in flight)" if in_flight_cnt > 0 else ""
        st.metric(
            "✈️ Drinks Logged Abroad", 
            f"{passport['drinks_abroad']:,} Drinks",
            delta=f"Outside Home Base{in_flight_txt}"
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
    st.info(f"No {selected_beverage_option.lower()} travel logs found for {selected_explorer_option}. Log a beverage to collect your first stamp!")
else:
    stamp_cols = st.columns(4)
    for idx, ((c_code, c_city), cnt) in enumerate(city_items):
        info = TRAVEL_COUNTRIES.get(c_code, {"name": c_code, "flag": "🏳️", "continent": "Unknown"})
        is_home = (c_code == user_def_country and c_city.lower() == user_def_city.lower()) if active_user_filter else False
        
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

leaderboard = get_travel_leaderboard(transactions or [], users, clicks_data=data)
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
