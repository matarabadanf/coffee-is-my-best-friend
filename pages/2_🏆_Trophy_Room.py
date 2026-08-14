import streamlit as st
import pandas as pd

# Import refactored modules
from database import get_data, get_transactions
from data_processing import (
    process_raw_data, 
    get_gamification_metrics, 
    get_user_titles, 
    resolve_user_title,
    get_user_preferences, 
    get_coin_balances,
    ACHIEVEMENT_TIERS,
    SECRET_FEATS
)
from utils import enforce_user_identity
from components.ui import inject_custom_css, render_app_header

# Setup Page Configuration
st.set_page_config(page_title="Trophy Room", page_icon="🏆", layout="wide")

users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

data = get_data()
transactions = get_transactions()

prefs = get_user_preferences(transactions, users)
user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")
inject_custom_css(user_theme, user_style, user=selected_user)

df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)
trophies = get_gamification_metrics(df_coffee, df_tea, users, transactions=transactions)
coin_balances = get_coin_balances(df, transactions, users)

user_coins = coin_balances.get(selected_user, 0)
user_streak = trophies.get("streaks", {}).get(selected_user, 0)
user_emoji = prefs.get(selected_user, {}).get("emoji", "☕")
user_title = resolve_user_title(selected_user, prefs, trophies)

# --- 1. Persistent Top Bar ---
render_app_header(
    selected_user=selected_user, 
    coin_balance=user_coins, 
    streak_days=user_streak, 
    custom_emoji=user_emoji, 
    custom_title=user_title
)

st.title("🏆 Trophy Room & Hall of Fame")
st.caption("Celebrate reigning monarchs, track individual tiered milestones, discover secret easter eggs, and inspect historical monthly crowns.")
st.divider()

# --- 2. Interactive 4-Tab Trophy Room ---
tab1, tab2, tab3, tab4 = st.tabs([
    "👑 Global Reigning Monarchs",
    "🎖️ Personal Achievements",
    "🕵️ Secret Easter Eggs",
    "🏛️ Monthly Hall of Fame"
])

funny = trophies.get("funny_stats", {})

# =========================================================================
# TAB 1: GLOBAL REIGNING MONARCHS
# =========================================================================
with tab1:
    st.subheader("👑 Current Global Record Holders")
    st.caption("Reigning champions who dominate all-time and weekly beverage statistics.")
    
    # Active Streak Quick Deck
    st.markdown("#### 🔥 Active Daily Streaks")
    str_cols = st.columns(len(users))
    for idx, u in enumerate(users):
        u_str = trophies["streaks"].get(u, 0)
        u_em = prefs.get(u, {}).get("emoji", "☕")
        with str_cols[idx]:
            with st.container(border=True):
                st.metric(f"{u_em} {u}'s Streak", f"{u_str} Days", delta="🔥 Active" if u_str > 0 else "💤 Idle")
                
    st.divider()
    
    # Monarch Record Cards Grid
    st.markdown("#### 🌟 Hall of Fame Titles")
    
    # Row 1 (Core Beverage Monarchs)
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        with st.container(border=True):
            st.markdown("### 👑 Caffeine Monarch")
            addict = trophies.get("caffeine_addict")
            if addict:
                u_em = prefs.get(addict, {}).get("emoji", "☕")
                st.success(f"**{u_em} {addict}** reigns supreme with the most coffees in the past 7 days!")
            else:
                st.info("No coffee logged in the past 7 days.")
            st.caption("🏆 *Weekly Caffeine Champion*")

    with r1c2:
        with st.container(border=True):
            st.markdown("### 🍵 Tea Monarch")
            purist = trophies.get("tea_purist")
            if purist:
                u_em = prefs.get(purist, {}).get("emoji", "🍵")
                st.success(f"**{u_em} {purist}** holds the highest Tea-to-Coffee ratio across all logs.")
            else:
                st.info("No tea data found.")
            st.caption("🌿 *Supreme Tea Dedication*")

    with r1c3:
        with st.container(border=True):
            st.markdown("### 🧊 Sub-Zero Monarch")
            ice = trophies.get("ice_monarch")
            if ice:
                u_em = prefs.get(ice["user"], {}).get("emoji", "🧊")
                st.success(f"**{u_em} {ice['user']}** leads the frost realm with **{ice['count']}** iced drinks logged!")
            else:
                st.info("No iced drinks logged yet.")
            st.caption("❄️ *Iced Beverage Master*")

    with r1c4:
        with st.container(border=True):
            st.markdown("### 🔥 Combustion Monarch")
            fire = trophies.get("combustion_monarch")
            if fire:
                u_em = prefs.get(fire["user"], {}).get("emoji", "🔥")
                st.success(f"**{u_em} {fire['user']}** reached Warp Speed with **{fire['count']}** On-Fire days (400+ mg)!")
            else:
                st.info("No On-Fire days recorded yet.")
            st.caption("🌋 *Most All-Time Days Over 400mg*")

    # Row 2
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        with st.container(border=True):
            st.markdown("### 🥇 Streak Sovereign")
            longest_streak = trophies.get("longest_historical_streak")
            if longest_streak:
                u_em = prefs.get(longest_streak["user"], {}).get("emoji", "🔥")
                st.success(f"**{u_em} {longest_streak['user']}** set the all-time record with an unbroken **{longest_streak['days']}-day** streak!")
            else:
                st.info("No streaks recorded yet.")
            st.caption("🔥 *Longest daily logging streak in history.*")

    with r2c2:
        with st.container(border=True):
            st.markdown("### ⚡ Velocity Monarch")
            most_coffees = trophies.get("most_coffees_in_a_day")
            if most_coffees:
                u_em = prefs.get(most_coffees["user"], {}).get("emoji", "☕")
                st.success(f"**{u_em} {most_coffees['user']}** drank **{most_coffees['count']}** coffees in a single day on {most_coffees['date']}!")
            else:
                st.info("No records yet.")
            st.caption("🚀 *Most coffees in a single calendar day.*")

    with r2c3:
        with st.container(border=True):
            st.markdown("### 💍 The Monogamist")
            monogamist = trophies.get("monogamist")
            if monogamist:
                u_em = prefs.get(monogamist["user"], {}).get("emoji", "☕")
                st.success(f"**{u_em} {monogamist['user']}** drank only **{monogamist['drink']}** for **{monogamist['streak']}** consecutive logs!")
            else:
                st.info("No monogamist streaks yet.")
            st.caption("🎯 *Longest unbroken single-beverage loyalty.*")

    # Row 3
    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1:
        with st.container(border=True):
            st.markdown("### 🥱 Monday Grump")
            monday = trophies.get("monday_grump")
            if monday:
                u_em = prefs.get(monday["user"], {}).get("emoji", "☕")
                st.info(f"**{u_em} {monday['user']}** has logged **{monday['count']}** coffees fighting Monday morning blues.")
            else:
                st.write("No Monday logs.")
            st.caption("☕ *Most caffeine consumed on Mondays.*")

    with r3c2:
        with st.container(border=True):
            st.markdown("### 🦉 Night Owl")
            if funny.get("night_owl"):
                u_em = prefs.get(funny["night_owl"], {}).get("emoji", "🦉")
                st.info(f"**{u_em} {funny['night_owl']}** logs the most drinks between 20:00 and 04:00.")
            else:
                st.write("No night owl activity.")
            st.caption("🌙 *Dominates the late night shift.*")

    with r3c3:
        with st.container(border=True):
            st.markdown("### 🌅 Early Bird")
            if funny.get("early_bird"):
                u_em = prefs.get(funny["early_bird"], {}).get("emoji", "☀️")
                st.info(f"**{u_em} {funny['early_bird']}** logs the most drinks between 04:00 and 08:00.")
            else:
                st.write("No early bird activity.")
            st.caption("☀️ *First to brew in the morning.*")

    # Row 4
    r4c1, r4c2, r4c3 = st.columns(3)
    with r4c1:
        with st.container(border=True):
            st.markdown("### 🦇 Midnight Oil")
            midnight = trophies.get("midnight_oil")
            if midnight:
                u_em = prefs.get(midnight["user"], {}).get("emoji", "🕯️")
                st.warning(f"**{u_em} {midnight['user']}** logged the absolute latest drink at **{midnight['time']}**!")
            else:
                st.write("No midnight logs.")
            st.caption("🕯️ *Timestamp record for latest log.*")

    with r4c2:
        with st.container(border=True):
            st.markdown("### 🐢 Marathon Drinker")
            if funny.get("marathon"):
                st.info(f"**{funny['marathon']}** spaces their drinks out the most on average.")
            else:
                st.write("No marathon drinkers yet.")
            st.caption("⏳ *Longest average interval between drinks.*")

    with r4c3:
        with st.container(border=True):
            st.markdown("### ⚖️ Equilibrium Monarch")
            if funny.get("balanced"):
                u_em = prefs.get(funny["balanced"], {}).get("emoji", "⚖️")
                st.info(f"**{u_em} {funny['balanced']}** maintains the closest to a 50/50 balance of Coffee and Tea.")
            else:
                st.write("No balanced drinkers yet.")
            st.caption("☯️ *Harmony between coffee and tea.*")


# =========================================================================
# TAB 2: PERSONAL ACHIEVEMENTS
# =========================================================================
with tab2:
    st.subheader("🎖️ Individual Milestone Tiers")
    st.caption("Track your personal journey across 10 balanced mastery tracks, tailored for consistency, volume, and brewing style.")
    
    # User Switcher
    active_profile = st.segmented_control(
        "Select User Profile", 
        users, 
        default=selected_user,
        key="ach_user_selector"
    )
    if active_profile is None:
        active_profile = selected_user
        
    p_ach = trophies.get("personal_achievements", {}).get(active_profile, {})
    
    # Calculate Total Unlocked Badges
    total_tiers = 0
    unlocked_tiers = 0
    for cat_data in p_ach.values():
        for t in cat_data["tiers"]:
            total_tiers += 1
            if t["unlocked"]:
                unlocked_tiers += 1
                
    pct_complete = int((unlocked_tiers / max(1, total_tiers)) * 100)
    
    with st.container(border=True):
        st.markdown(f"### 🏆 **{active_profile}'s Trophy Progress: `{unlocked_tiers} / {total_tiers}` Badges ({pct_complete}%)**")
        st.progress(unlocked_tiers / max(1, total_tiers))
        
    st.divider()
    
    # Grid of Mastery Paths
    ach_cols = st.columns(2)
    for idx, (cat_key, cat_data) in enumerate(p_ach.items()):
        with ach_cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"### {cat_data['icon']} {cat_data['title']}")
                if cat_data.get("desc"):
                    st.caption(f"ℹ️ {cat_data['desc']}")
                
                for t in cat_data["tiers"]:
                    t_col1, t_col2 = st.columns([3, 1])
                    with t_col1:
                        if t["unlocked"]:
                            st.markdown(f"**✅ {t['level']} Tier — {t['name']}**")
                            st.caption(f"Goal: `{t['target']}` &bull; Current: `{t['current']}`")
                        else:
                            st.markdown(f"**🔒 {t['level']} Tier — {t['name']}**")
                            st.caption(f"Goal: `{t['target']}` &bull; Current: `{t['current']}` (`{int(t['progress_pct']*100)}%`)")
                        st.progress(t["progress_pct"])
                    with t_col2:
                        if t["unlocked"]:
                            st.success(f"**{t['level']}**")
                        else:
                            st.info(f"`{t['current']}/{t['target']}`")


# =========================================================================
# TAB 3: SECRET EASTER EGGS
# =========================================================================
with tab3:
    st.subheader("🕵️ Secret Easter Eggs & Arcane Feats")
    st.caption("Concealed achievements unlocked only by unearthing peculiar cosmic alignments, rare timing rituals, or alchemical feats.")
    
    sec_user = st.segmented_control(
        "Select User Profile", 
        users, 
        default=selected_user,
        key="secret_user_selector"
    )
    if sec_user is None:
        sec_user = selected_user
        
    user_secrets = trophies.get("secret_feats", {}).get(sec_user, {})
    unlocked_count = sum(1 for fid in user_secrets if user_secrets[fid])
    
    with st.container(border=True):
        st.markdown(f"### 🔮 **{sec_user}'s Grimoire: `{unlocked_count} / {len(SECRET_FEATS)}` Mysteries Deciphered**")
        st.progress(unlocked_count / len(SECRET_FEATS))
        
    st.divider()
    
    sec_cols = st.columns(2)
    for idx, feat in enumerate(SECRET_FEATS):
        fid = feat["id"]
        is_unlocked = user_secrets.get(fid, False)
        
        with sec_cols[idx % 2]:
            with st.container(border=True):
                if is_unlocked:
                    st.markdown(f"### 🌟 {feat['title']}")
                    st.success(f"**Deciphered Lore:** {feat['desc']}")
                    st.caption(f"🏅 *{sec_user} has conquered this arcane mystery!*")
                else:
                    st.markdown("### 🔒 ??? Arcane Mystery")
                    st.info(f"📜 **Cryptic Riddle:** *\"{feat['hint']}\"*")
                    st.caption("🗝️ *The achievement and its lore remain shrouded in mist until fulfilled.*")


# =========================================================================
# TAB 4: MONTHLY HALL OF FAME LEDGER
# =========================================================================
with tab4:
    st.subheader("🏛️ Monthly Hall of Fame Ledger")
    st.caption("Historical record of monthly monarchs reigning since inception.")
    
    records = trophies.get("monthly_records", [])
    if records:
        for rec in records:
            with st.container(border=True):
                m_col1, m_col2, m_col3 = st.columns([1, 1, 1])
                with m_col1:
                    st.markdown(f"### 📅 {rec['Month']}")
                with m_col2:
                    st.markdown(f"**☕ Coffee Monarch:**")
                    st.markdown(f"#### 👑 {rec['☕ Coffee Monarch']}")
                with m_col3:
                    st.markdown(f"**🍵 Tea Monarch:**")
                    st.markdown(f"#### 👑 {rec['🍵 Tea Monarch']}")
    else:
        st.info("No historical monthly records available yet.")
