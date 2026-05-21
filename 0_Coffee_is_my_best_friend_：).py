import streamlit as st
import pandas as pd
from datetime import datetime
import time
import random
import randfacts

# Import refactored modules
from database import get_data, insert_click
from data_processing import process_raw_data, get_gamification_metrics, get_user_titles
from components.ui import inject_custom_css, render_header_and_quotes

# 1. Setup Page Configuration
st.set_page_config(page_title="Coffee is my best friend", page_icon=":coffee:", layout="centered")

# Inject CSS and Render Header
inject_custom_css()
render_header_and_quotes()

# User Configuration
users = ["Cris", "Bea", "Fer"]

# 2. Data Fetching & Processing
data = get_data()
df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)
trophies = get_gamification_metrics(df_coffee, df_tea, users)

now = pd.Timestamp.now(tz="Europe/Madrid") if df.empty else pd.Timestamp.now(tz="UTC").tz_convert("Europe/Madrid")

# Calculate today's stats
today_coffees = 0
today_teas = 0
today_df = pd.DataFrame()

if not df.empty:
    # Ensure timezone awareness for filtering
    if df["created_at"].dt.tz is None:
        df["created_at"] = df["created_at"].dt.tz_localize("UTC")
    df["created_at"] = df["created_at"].dt.tz_convert("Europe/Madrid")
    
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_df = df[df["created_at"] >= today_start]
    today_coffees = len(today_df[today_df["drink_id"] == 1])
    today_teas = len(today_df[today_df["drink_id"] == 2])


# 4. Unified Mobile-Friendly Log Hub
st.subheader("Log a Drink ☕")
with st.container(border=True):
    selected_user = st.radio("Who is drinking?", users, horizontal=True)
    
    # Cooldown check for selected user
    last_click_time = None
    if not df.empty:
        user_clicks = df[df["user_name"] == selected_user]
        if not user_clicks.empty:
            last_click_time = user_clicks["created_at"].max()
            
    col_c, col_d = st.columns(2)
    
    with col_c:
        if st.button("☕ Coffee", use_container_width=True):
            if last_click_time:
                time_diff = (now - last_click_time).total_seconds()
                if time_diff < 60:
                    st.warning(f"Wait {int(60 - time_diff)}s before adding another!")
                    st.stop()
            try:
                insert_click(selected_user, 1, 1) # 1 for Coffee
                st.balloons()
                st.success("**Coffee Counted!**")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
                
    with col_d:
        if st.button("🍵 Tea", use_container_width=True):
            if last_click_time:
                time_diff = (now - last_click_time).total_seconds()
                if time_diff < 60:
                    st.warning(f"Wait {int(60 - time_diff)}s before adding another!")
                    st.stop()
            try:
                insert_click(selected_user, 1, 2) # 2 for Tea
                st.snow()
                st.success("**Tea Counted!**")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()

# 5. Player Cards
st.subheader("Who are we?")
cols = st.columns(len(users))

for idx, user in enumerate(users):
    c_score = coffee_scores.get(user, 0)
    t_score = tea_scores.get(user, 0)
    user_title = get_user_titles(user, trophies)
    
    # Calculate today's caffeine
    caff = 0
    if not today_df.empty:
        user_today = today_df[today_df["user_name"] == user]
        caff = len(user_today[user_today["drink_id"] == 1]) * 95 + len(user_today[user_today["drink_id"] == 2]) * 30
        
    prog_val = min(caff, 400) / 400.0 # Assuming 400mg is the daily max for the bar
    
    with cols[idx]:
        with st.container(border=True):
            st.markdown(f"<h3 style='margin-bottom: 0;'>{user}</h3>", unsafe_allow_html=True)
            st.page_link("pages/2_🏆_Trophy_Room.py", label=user_title)
            
            st.write(f"**☕ {c_score}** | **🍵 {t_score}** *(All-time)*")
            
            st.caption(f"**Caffeine Today: {caff}mg** / 400mg")
            st.progress(prog_val)

st.divider()

# 3. Hero Stats
st.markdown("<h2 style='text-align: center;'>Today's Scoreboard</h2>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)
col_a.metric("Today's Coffees ☕", today_coffees)
col_b.metric("Today's Teas 🍵", today_teas)

total_coffees = sum(coffee_scores.values())
total_teas = sum(tea_scores.values())
st.markdown(f"<p style='text-align: center; color: #6F4E37; font-size: 0.9em;'><em>All-Time Total: {total_coffees} Coffees | {total_teas} Teas</em></p>", unsafe_allow_html=True)
st.divider()

# 6. Live Activity Feed
st.subheader("Live Activity Feed 📡")
with st.container(border=True):
    if not df.empty:
        recent = df.sort_values(by="created_at", ascending=False).head(7)
        for _, row in recent.iterrows():
            u = row["user_name"]
            d = "Coffee ☕" if row["drink_id"] == 1 else "Tea 🍵"
            t = row["created_at"]
            
            diff = now - t
            mins = int(diff.total_seconds() / 60)
            if mins < 1:
                time_str = "Just now"
            elif mins < 60:
                time_str = f"{mins} min{'s' if mins > 1 else ''} ago"
            elif mins < 1440:
                hours = mins // 60
                time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                time_str = t.strftime("%b %d, %H:%M")
            
            st.markdown(f"- **{u}** grabbed a **{d}** *({time_str})*")
    else:
        st.write("No activity yet.")

st.divider()
st.info("Discover more insights and historical records below:")
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.page_link("pages/1_📈_Graphs!_Graphs!_Graphs!.py", label="Graphs! Graphs! Graphs!", icon="📈")
with col_info2:
    st.page_link("pages/2_🏆_Trophy_Room.py", label="Trophy Room", icon="🏆")
