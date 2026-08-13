import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime
import time

from database import get_data, get_transactions, insert_transaction
from data_processing import process_raw_data, get_coin_balances, get_user_preferences, get_unlocked_themes
from utils import verify_pin, is_pin_verified, enforce_user_identity
from components.ui import inject_custom_css, ALL_THEMES, ALL_STYLES, THEME_METADATA

st.set_page_config(page_title="Theme Boutique & Studio", page_icon="🎨", layout="wide")

users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

data = get_data()
transactions = get_transactions()

prefs = get_user_preferences(transactions, users)
user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")

df, _, _, _, _ = process_raw_data(data, users)
coin_balances = get_coin_balances(df, transactions, users)
balance = coin_balances.get(selected_user, 0)
unlocked_themes = get_unlocked_themes(transactions, selected_user)

# Session state for live preview studio
if "theme_shop_picker" not in st.session_state:
    st.session_state.theme_shop_picker = user_theme if user_theme in ALL_THEMES else "Latte (Light)"

if "theme_shop_style_picker" not in st.session_state:
    st.session_state.theme_shop_style_picker = user_style if user_style in ALL_STYLES else "Modern Flat"

def set_theme_preview(t, s):
    st.session_state.theme_shop_picker = t
    st.session_state.theme_shop_style_picker = s

# Active preview configuration
preview_theme = st.session_state.theme_shop_picker
preview_style = st.session_state.theme_shop_style_picker

# Inject preview CSS live
inject_custom_css(preview_theme, preview_style)

# --- Header ---
st.title("🎨 Theme Boutique & Studio")
st.markdown(f"#### 👤 Logged in as: <span class='user-highlight'>{selected_user}</span> | 🪙 Balance: **`{balance} Coins`**", unsafe_allow_html=True)
st.caption("Browse handcrafted beverage aesthetics. Test any theme and UI morphism combination live on real components before buying or equipping.")
st.divider()

# --- 1. Studio Controls & Quick Presets ---
with st.container(border=True):
    ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 3])
    with ctrl1:
        st.selectbox(
            "🎨 Select Theme to Preview",
            ALL_THEMES,
            key="theme_shop_picker"
        )
            
    with ctrl2:
        st.selectbox(
            "✨ Select Morphism Style",
            ALL_STYLES,
            key="theme_shop_style_picker"
        )
            
    with ctrl3:
        st.markdown("**⚡ 1-Click Quick Presets:**")
        p_b1, p_b2, p_b3 = st.columns(3)
        with p_b1:
            st.button("☕ Latte", on_click=set_theme_preview, args=("Latte (Light)", "Modern Flat"), use_container_width=True)
            st.button("🍯 Caramel", on_click=set_theme_preview, args=("Caramel Macchiato (Amber)", "Glassmorphism"), use_container_width=True)
        with p_b2:
            st.button("🌙 Espresso", on_click=set_theme_preview, args=("Espresso (Dark)", "Neumorphism"), use_container_width=True)
            st.button("🌸 Strawberry", on_click=set_theme_preview, args=("Strawberry Frappé (Pink)", "Modern Flat"), use_container_width=True)
        with p_b3:
            st.button("🍵 Matcha", on_click=set_theme_preview, args=("Matcha (Green)", "Glassmorphism"), use_container_width=True)
            st.button("⚡ Cyber", on_click=set_theme_preview, args=("Midnight Cyber Brew (Dark Neon)", "Glassmorphism"), use_container_width=True)

# --- 2. Status & Action Card (Buy or Equip) ---
t_meta = THEME_METADATA.get(preview_theme, {"price": 0, "desc": "", "icon": "🎨", "swatch": ["#FFFFFF", "#000000", "#FF0000"]})
is_owned = preview_theme in unlocked_themes
is_active = (user_theme == preview_theme and user_style == preview_style)

with st.container(border=True):
    s_col1, s_col2 = st.columns([3, 2])
    with s_col1:
        st.markdown(f"### {t_meta['icon']} {preview_theme}")
        st.write(t_meta["desc"])
        st.caption(f"Active Morphism Style: **`{preview_style}`**")
        
        # Swatch visual
        swatches_html = " ".join([f"<span style='display:inline-block; width:22px; height:22px; border-radius:50%; background:{c}; border:1px solid rgba(0,0,0,0.2); vertical-align:middle; margin-right:6px;'></span>" for c in t_meta["swatch"]])
        st.markdown(f"**Palette:** {swatches_html}", unsafe_allow_html=True)
        
    with s_col2:
        if is_active:
            st.success("🌟 **Equipped as Active Theme!**")
            st.caption("This is your currently active theme across all pages.")
        elif is_owned:
            st.info("✅ **Theme Owned!**")
            if st.button(f"⚡ Equip `{preview_theme}` Now", use_container_width=True, key="equip_theme_btn"):
                insert_transaction(selected_user, 0, "preference", {"theme": preview_theme, "ui_style": preview_style})
                st.success(f"Equipped {preview_theme} ({preview_style}) as default!")
                st.rerun()
        else:
            price = t_meta["price"]
            st.warning(f"🔒 **Locked Shop Theme** — Price: 🪙 `{price:,} Coins`")
            
            pin_input = ""
            if not is_pin_verified(selected_user):
                pin_input = st.text_input(
                    "Security PIN:", 
                    type="password", 
                    placeholder="Enter PIN to unlock",
                    key=f"buy_pin_{preview_theme}"
                )
            else:
                st.caption("🔓 *Security session verified.*")
                
            if st.button(f"🪙 Unlock & Equip for {price:,} Coins", key=f"btn_buy_{preview_theme}", use_container_width=True):
                if balance < price:
                    st.error(f"❌ Not enough coins! You have 🪙 {balance:,} but need 🪙 {price:,}.")
                elif verify_pin(selected_user, pin_input):
                    insert_transaction(selected_user, -price, "shop", {"theme_unlock": preview_theme, "item": f"theme_{preview_theme}"})
                    insert_transaction(selected_user, 0, "preference", {"theme": preview_theme, "ui_style": preview_style})
                    st.balloons()
                    st.success(f"🎉 Unlocked and equipped **{preview_theme}**!")
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error("❌ Incorrect PIN! Please enter your profile PIN to confirm purchase.")

st.divider()

# --- 3. Live Component Showcase Canvas ---
st.subheader(f"🖥️ Live Component Preview Canvas (`{preview_theme}` + `{preview_style}`)")
st.caption("All interactive controls and charts below are rendered with the live preview theme.")

# A. Metric Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Coffee", "142", delta="+12 Today")
with c2:
    st.metric("Total Tea", "58", delta="+3 Today")
with c3:
    st.metric("Coins Balance", f"🪙 {balance}", delta="+150 This Week")
with c4:
    st.metric("Streak Leader", "Cris", delta="🔥 8 Days")

# B. Action Buttons & Form Controls
f_col1, f_col2 = st.columns(2)
with f_col1:
    with st.container(border=True):
        st.subheader("Action Hub & Interactive Buttons")
        b1, b2 = st.columns(2)
        with b1:
            st.button("☕ Log Espresso", use_container_width=True, key="demo_btn1")
            st.download_button("📥 Export Logs (CSV)", "sample,csv\n1,2", "sample.csv", use_container_width=True, key="demo_btn3")
        with b2:
            st.button("🍵 Log Green Tea", use_container_width=True, key="demo_btn2")
            with st.popover("⚙️ Quick Options", use_container_width=True):
                st.write("Popover dialog content rendered with matching theme aesthetics.")
                st.button("Confirm Option", key="demo_pop_btn")

with f_col2:
    with st.container(border=True):
        st.subheader("Form Controls & Segmented Pickers")
        st.segmented_control("Segmented Profile Switcher", ["👤 Cris", "👤 Bea", "👤 Fer"], default="👤 Cris", key="demo_seg_profile")
        st.segmented_control("Timeframe Filter", ["⚡ 24 Hours", "📅 7 Days", "🌙 30 Days", "🌟 All Time"], default="⚡ 24 Hours", key="demo_seg_time")
        st.text_input("Favorite Roast / Drink Name", value="Iced Oat Vanilla Cortado", key="demo_text_in")
        st.selectbox("Selectbox Dropdown", ["Single Origin Ethiopia", "Colombian Geisha", "Sumatra Dark Roast", "Matcha Ceremonial"], key="demo_sel_in")
        st.multiselect("Drink Add-ons", ["Oat Milk", "Brown Sugar", "Cinnamon", "Extra Shot"], default=["Oat Milk", "Extra Shot"], key="demo_multi_in")

# C. Themed Chart Preview
with st.container(border=True):
    st.subheader("Themed Data Visualization (Altair Chart)")
    sample_chart_df = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Coffee": [12, 18, 15, 22, 20, 8, 14],
        "Tea": [4, 6, 8, 5, 7, 10, 9]
    })
    chart_melted = sample_chart_df.melt("Day", var_name="Drink", value_name="Count")
    
    accent_c = t_meta["swatch"][1] if len(t_meta["swatch"]) > 1 else "#E24A00"
    
    chart = alt.Chart(chart_melted).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("Day:N", sort=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], title="Day of Week"),
        y=alt.Y("Count:Q", title="Total Drinks Logged"),
        color=alt.Color("Drink:N", scale=alt.Scale(range=[accent_c, "#78533D"] if preview_theme != "Matcha (Green)" else ["#3B6B35", "#85B07E"])),
        tooltip=["Day", "Drink", "Count"]
    ).properties(
        height=280
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        labelColor=t_meta["swatch"][0] if "Dark" in preview_theme else "#4A3B32",
        titleColor=t_meta["swatch"][0] if "Dark" in preview_theme else "#4A3B32",
        gridColor="rgba(128, 128, 128, 0.15)"
    )
    
    st.altair_chart(chart, use_container_width=True)

# --- 4. Catalog of All Themes ---
st.divider()
st.subheader("📚 Complete Theme Collection")
cat_cols = st.columns(4)
for idx, (t_name, meta) in enumerate(THEME_METADATA.items()):
    with cat_cols[idx % 4]:
        with st.container(border=True):
            st.markdown(f"#### {meta['icon']} {t_name}")
            st.caption(meta["desc"])
            
            # Swatch visual
            swatches = " ".join([f"<span style='display:inline-block; width:16px; height:16px; border-radius:50%; background:{c}; border:1px solid rgba(0,0,0,0.2); vertical-align:middle; margin-right:4px;'></span>" for c in meta["swatch"]])
            st.markdown(f"Colors: {swatches}", unsafe_allow_html=True)
            
            if t_name in unlocked_themes:
                st.success("✅ Owned")
                st.button(f"👁️ Preview `{meta['icon']}`", on_click=set_theme_preview, args=(t_name, preview_style), key=f"prev_cat_{t_name}", use_container_width=True)
            else:
                st.info(f"🪙 `{meta['price']:,} Coins`")
                cat_b1, cat_b2 = st.columns(2)
                with cat_b1:
                    st.button(f"👁️ Preview", on_click=set_theme_preview, args=(t_name, preview_style), key=f"prev_cat_{t_name}", use_container_width=True)
                with cat_b2:
                    with st.popover("🪙 Buy", use_container_width=True):
                        st.write(f"Unlock **{t_name}** for 🪙 `{meta['price']:,}`?")
                        cat_pin = ""
                        if not is_pin_verified(selected_user):
                            cat_pin = st.text_input("PIN", type="password", key=f"cat_pin_{t_name}")
                        if st.button("Confirm", key=f"cat_confirm_{t_name}", use_container_width=True):
                            if balance < meta["price"]:
                                st.error("Not enough coins!")
                            elif verify_pin(selected_user, cat_pin):
                                insert_transaction(
                                    selected_user, 
                                    -meta["price"], 
                                    "shop", 
                                    {"theme_unlock": t_name, "item": f"theme_{t_name}"}
                                )
                                insert_transaction(
                                    selected_user, 
                                    0, 
                                    "preference", 
                                    {"theme": t_name, "ui_style": preview_style}
                                )
                                st.session_state.theme_shop_picker = t_name
                                st.success(f"Unlocked {t_name}!")
                                st.rerun()
                            else:
                                st.error("Incorrect PIN!")

