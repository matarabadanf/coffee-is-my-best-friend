import streamlit as st
import pandas as pd

# Import refactored modules
from database import get_data
from data_processing import process_raw_data, get_gamification_metrics
from components.ui import inject_custom_css

# Setup Page Configuration
st.set_page_config(page_title="Coffee is my best friend", page_icon="🏆")
inject_custom_css()

users = ["Cris", "Bea", "Fer"]

data = get_data()
df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)

st.title("Trophy Room 🏆")

trophies = get_gamification_metrics(df_coffee, df_tea, users)

# 1. Streaks
st.header("🔥 Active Streaks")
st.write("Consecutive days logging *any* drink.")

cols = st.columns(len(users))
for idx, user in enumerate(users):
    streak = trophies["streaks"].get(user, 0)
    with cols[idx]:
        st.metric(label=f"{user}'s Streak", value=f"{streak} Days", delta=None if streak == 0 else f"🔥")

st.divider()

# 2. Weekly Achievements
st.header("Weekly Achievements")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👑 Caffeine Addict of the Week")
    if trophies.get("caffeine_addict"):
        st.success(f"**{trophies['caffeine_addict']}** has logged the most coffees in the last 7 days!")
    else:
        st.info("No data for the last 7 days yet.")

with col2:
    st.markdown("### 🍵 Tea Purist")
    if trophies.get("tea_purist"):
        st.success(f"**{trophies['tea_purist']}** has the highest Tea-to-Coffee ratio!")
    else:
        st.info("No tea data found.")

st.divider()

# 3. Trophy Room
st.header("🏆 Trophy Room")
funny = trophies.get("funny_stats", {})

st.markdown("<br>", unsafe_allow_html=True)
r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    st.markdown("### 🥇 Longest Streak")
    longest_streak = trophies.get("longest_historical_streak")
    if longest_streak:
        st.success(f"**{longest_streak['user']}** holds the record with an unbroken **{longest_streak['days']}-day** streak!")
    else:
        st.info("No streaks recorded yet.")

with r1c2:
    st.markdown("### ⚡ Most in a Day")
    most_coffees = trophies.get("most_coffees_in_a_day")
    if most_coffees:
        st.success(f"**{most_coffees['user']}** drank **{most_coffees['count']}** coffees on {most_coffees['date']}!")
    else:
        st.info("No records yet.")

with r1c3:
    st.markdown("### ☕ The Monogamist")
    monogamist = trophies.get("monogamist")
    if monogamist:
        st.success(f"**{monogamist['user']}** drank only **{monogamist['drink']}** for **{monogamist['streak']}** consecutive drinks!")
    else:
        st.info("No records yet.")

st.markdown("<br>", unsafe_allow_html=True)
r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    st.markdown("### 🥱 Monday Grump")
    monday = trophies.get("monday_grump")
    if monday:
        st.info(f"**{monday['user']}** has logged **{monday['count']}** coffees on Mondays.")
    else:
        st.write("No Monday data.")

with r2c2:
    st.markdown("### 🗓️ Weekend Warrior")
    weekend = trophies.get("weekend_warrior")
    if weekend:
        st.info(f"**{weekend['user']}** dominates the weekends, averaging **{weekend['count']}** drinks.")
    else:
        st.write("No weekend data.")

with r2c3:
    st.markdown("### 🏢 Weekday Warrior")
    weekday = trophies.get("weekday_warrior")
    if weekday:
        st.info(f"**{weekday['user']}** logs heavily on workdays, averaging **{weekday['count']}** drinks.")
    else:
        st.write("No weekday data.")

st.markdown("<br>", unsafe_allow_html=True)
r3c1, r3c2, r3c3 = st.columns(3)

with r3c1:
    st.markdown("### 🏜️ Longest Dry Spell")
    dry = trophies.get("dry_spell")
    if dry:
        st.warning(f"**{dry['user']}** once went **{dry['days']} days** without logging a single drink.")
    else:
        st.write("No dry spells.")

with r3c2:
    st.markdown("### 🦇 Midnight Oil")
    midnight = trophies.get("midnight_oil")
    if midnight:
        st.warning(f"**{midnight['user']}** logged the absolute latest drink at **{midnight['time']} AM**.")
    else:
        st.write("No late-night logs.")

with r3c3:
    st.markdown("### 🌞 Afternoon Slump")
    slump = trophies.get("afternoon_slump")
    if slump:
        st.warning(f"**{slump['user']}** fights the post-lunch crash with **{slump['count']}** afternoon drinks.")
    else:
        st.write("No afternoon data.")

st.markdown("<br>", unsafe_allow_html=True)
r4c1, r4c2, r4c3 = st.columns(3)

with r4c1:
    st.markdown("### 🦉 Night Owl")
    if funny.get("night_owl"):
        st.info(f"**{funny['night_owl']}** logs the most drinks between 8 PM and 4 AM.")
    else:
        st.write("No night owls yet.")

with r4c2:
    st.markdown("### 🌅 Early Bird")
    if funny.get("early_bird"):
        st.info(f"**{funny['early_bird']}** logs the most drinks between 4 AM and 8 AM.")
    else:
        st.write("No early birds yet.")

with r4c3:
    st.markdown("### ⚖️ Perfectly Balanced")
    if funny.get("balanced"):
        st.info(f"**{funny['balanced']}** has the most even split of Coffee and Tea.")
    else:
        st.write("No one is perfectly balanced.")

st.markdown("<br>", unsafe_allow_html=True)
r5c1, r5c2 = st.columns(2)

with r5c1:
    st.markdown("### 🚀 Speedrunner")
    if funny.get("speedrunner"):
        sp = funny["speedrunner"]
        st.success(f"**{sp['user']}** logged **{sp['count']}** drinks in a single hour on **{sp['date']}** at **{sp['hour']:02d}:00**!")
    else:
        st.write("No speedrunners yet.")

with r5c2:
    st.markdown("### 🐢 Marathon Drinker")
    if funny.get("marathon"):
        st.success(f"**{funny['marathon']}** spaces their drinks out the most on average.")
    else:
        st.write("No marathon drinkers yet.")

st.divider()

# 5. Hall of Fame
if trophies.get("monthly_records"):
    st.header("🏛️ Hall of Fame (Monthly Records)")
    st.dataframe(pd.DataFrame(trophies["monthly_records"]), hide_index=True, use_container_width=True)
