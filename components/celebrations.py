import streamlit as st
import pandas as pd
import time
from database import save_user_preference, insert_transaction
from data_processing import get_gamification_metrics, SECRET_FEATS

def get_user_achievement_snapshot(user, df_coffee, df_tea, transactions, users):
    """
    Returns a comprehensive snapshot dictionary of all unlocked items for a given user:
    - tiers: set of (track_id, tier_level, tier_name)
    - secrets: set of feat_id
    - crowns: set of crown_title
    """
    trophies = get_gamification_metrics(df_coffee, df_tea, users, transactions=transactions)
    user_achieve = trophies.get("personal_achievements", {}).get(user, {})
    
    unlocked_tiers = set()
    for track_id, track_data in user_achieve.items():
        for tier in track_data.get("tiers", []):
            if tier.get("unlocked"):
                unlocked_tiers.add((track_id, tier.get("level"), tier.get("name")))
                
    unlocked_secrets = set()
    user_secrets = trophies.get("secret_feats", {}).get(user, {})
    for feat_id, is_unlocked in user_secrets.items():
        if is_unlocked:
            unlocked_secrets.add(feat_id)
            
    # Crowns / Monarch titles
    crowns = set()
    if trophies.get("caffeine_addict") == user:
        crowns.add("👑 Caffeine Monarch")
    if trophies.get("tea_purist") == user:
        crowns.add("🍵 Tea Dynasty Sovereign")
    if trophies.get("ice_monarch") == user:
        crowns.add("🧊 Sub-Zero Monarch")
    if trophies.get("combustion_monarch") == user:
        crowns.add("🔥 Combustion Monarch")
        
    return {
        "tiers": unlocked_tiers,
        "secrets": unlocked_secrets,
        "crowns": crowns,
        "trophies": trophies
    }

def get_dev_test_payload(user):
    """Test payload for basic dev unlock demonstration."""
    return [{
        "type": "dev_test",
        "category": "🛠️ DEV PREVIEW UNLOCK PROTOCOL",
        "title": "🧪 Quantum Brew Pioneer",
        "tier": "Legendary",
        "icon": "🧪",
        "badge": "🧪 Quantum Brew Pioneer",
        "desc": "Triggered real-time quantum beverage synthesis in Developer Preview mode. All systems nominal!",
        "reward_coins": 100,
        "can_equip_title": True,
        "title_to_equip": "🧪 Quantum Brew Pioneer"
    }]

def get_tier_upgrade_test_payload(user):
    """Test payload demonstrating a badge tier upgrade from Silver to Gold."""
    return [{
        "type": "tier",
        "is_upgrade": True,
        "category": "🎖️ BADGE TIER UPGRADE!",
        "title": "🚇 Metropolitan (Gold)",
        "tier": "Gold",
        "icon": "🚇",
        "badge": "🚇 Metropolitan (Gold)",
        "previous_tier": "🚲 City Hopper (Silver)",
        "desc": "Advanced from 🚲 City Hopper (Silver) to 🚇 Metropolitan (Gold)! You have logged drinks across 18 unique cities!",
        "reward_coins": 150,
        "can_equip_title": True,
        "title_to_equip": "🚇 Metropolitan (Gold)"
    }]

def get_ui_2_0_welcome_payload(user):
    """Interactive tour and celebration welcome for UI 2.0."""
    return [{
        "type": "ui_2_0_welcome",
        "category": "✨ WELCOME TO COFFEE V2.0! ✨",
        "title": "🌟 UI 2.0 Pioneer",
        "tier": "Special",
        "icon": "🚀",
        "badge": "🌟 UI 2.0 Pioneer",
        "desc": (
            "Welcome to the next generation of Coffee is my best friend! "
            "Explore 8 boutique themes, glassmorphism & neumorphism aesthetics, "
            "the world explorer coffee passport, live unlock celebrations, and instant badge equipping!"
        ),
        "features": [
            ("🎨 Theme Boutique & Morphism", "Glassmorphism, Neumorphism, and 8 handcrafted color palettes."),
            ("🌍 World Explorer & Passport", "Track visits across countries and cities with interactive beverage maps."),
            ("🎉 Unlock Celebrations", "Live modal alerts, badge celebrations, and secret arcane feats."),
            ("🔒 Privacy & Identity", "Real-time feed broadcast controls, custom avatars, and dedicated preferences.")
        ],
        "reward_coins": 100,
        "can_equip_title": True,
        "title_to_equip": "🌟 UI 2.0 Pioneer"
    }]

def compute_new_unlocks(user, before_snapshot, after_snapshot, is_dev_test=False, transactions=None):
    """
    Compares snapshots and returns a list of celebration items with weekly crown limits and upgrade detection.
    """
    unlocks = []
    
    # Dev test trigger (generic dev mode testing)
    if is_dev_test:
        unlocks.extend(get_dev_test_payload(user))
        
    # 1. New Tiers & Tier Upgrades
    new_tiers = after_snapshot["tiers"] - before_snapshot["tiers"]
    # Map before_snapshot tiers by track_id to detect upgrades
    prev_track_tiers = {}
    for track_id, level, name in before_snapshot["tiers"]:
        prev_track_tiers[track_id] = (level, name)

    for track_id, level, name in new_tiers:
        coins = 50 if level in ["Bronze", "Silver"] else (100 if level == "Gold" else 200)
        
        is_upgrade = track_id in prev_track_tiers
        prev_level, prev_name = prev_track_tiers.get(track_id, (None, None))
        
        category = "🎖️ BADGE TIER UPGRADE!" if is_upgrade else "🎖️ ACHIEVEMENT TIER UNLOCKED!"
        desc = (
            f"Advanced from {prev_name} ({prev_level}) to {name} ({level}) in {track_id.replace('_', ' ').title()}!"
            if is_upgrade else
            f"New mastery unlocked in {track_id.replace('_', ' ').title()}! Progressing towards the next milestone!"
        )
        
        unlocks.append({
            "type": "tier",
            "is_upgrade": is_upgrade,
            "previous_tier": f"{prev_name} ({prev_level})" if is_upgrade else None,
            "category": category,
            "title": f"{name} ({level})",
            "tier": level,
            "icon": "🏆",
            "badge": f"{name} ({level})",
            "desc": desc,
            "reward_coins": coins,
            "can_equip_title": True,
            "title_to_equip": f"{name} ({level})"
        })
        
    # 2. New Secret Feats
    new_secrets = after_snapshot["secrets"] - before_snapshot["secrets"]
    secret_map = {f["id"]: f for f in SECRET_FEATS}
    for feat_id in new_secrets:
        f_info = secret_map.get(feat_id, {"title": feat_id, "desc": "Arcane secret unlocked!"})
        unlocks.append({
            "type": "secret",
            "category": "🕵️ ARCANE SECRET UNCOVERED!",
            "title": f_info["title"],
            "tier": "Secret",
            "icon": "✨",
            "badge": f_info["title"],
            "desc": f_info["desc"],
            "reward_coins": 150,
            "can_equip_title": True,
            "title_to_equip": f_info["title"]
        })
        
    # 3. New Monarch Crowns (Coin Bonus awarded ONLY once in lifetime per crown)
    new_crowns = after_snapshot["crowns"] - before_snapshot["crowns"]
    
    for crown in new_crowns:
        # Check if user has EVER received bonus coins for this crown
        already_rewarded = False
        if transactions:
            for t in transactions:
                if t.get("user_name") == user and t.get("transaction_type") == "shop":
                    meta = t.get("metadata", {})
                    if isinstance(meta, dict):
                        if meta.get("monarch_crown") == crown or meta.get("monarch_title") == crown:
                            already_rewarded = True
                            break
                        if meta.get("item", "").startswith(f"reward_monarch_{crown}"):
                            already_rewarded = True
                            break
                        if meta.get("monarch_week", "").startswith(f"{crown}_"):
                            already_rewarded = True
                            break

        reward_coins = 250 if not already_rewarded else 0
        desc = (
            f"You have claimed the sovereign throne as {crown}!" 
            if not already_rewarded else 
            f"You have claimed the sovereign throne as {crown}! (+250 🪙 crown bonus already collected previously)"
        )
        
        unlocks.append({
            "type": "monarch",
            "category": "👑 GLOBAL MONARCH CROWN CLAIMED!",
            "title": crown,
            "tier": "Monarch",
            "icon": "👑",
            "badge": crown,
            "desc": desc,
            "reward_coins": reward_coins,
            "reward_item_key": f"reward_monarch_{crown}",
            "can_equip_title": True,
            "title_to_equip": crown
        })
        
    return unlocks

# Streamlit Dialog celebration modal
if hasattr(st, "dialog"):
    @st.dialog("🎉 LEVEL UP & UNLOCKED! 🎉", width="large")
    def _render_dialog_modal(user, items):
        _render_celebration_content(user, items)
else:
    def _render_dialog_modal(user, items):
        with st.container(border=True):
            _render_celebration_content(user, items)

def _render_celebration_content(user, items):
    st.balloons()
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1.2rem;">
        <span style="font-size: 2.8rem; line-height: 1;">🌟 🏆 🌟</span>
        <h2 style="margin: 0.4rem 0 0 0; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em;">
            WOW! WE GOT SOMETHING!
        </h2>
        <p style="color: var(--text-muted, #71717A); font-size: 0.9rem; margin-top: 4px; font-weight: 600;">
            Incredible feat logged by <strong>{user}</strong>!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    for idx, item in enumerate(items):
        category = item.get("category", "🎉 UNLOCK!")
        title = item.get("title", "New Achievement")
        icon = item.get("icon", "🏆")
        desc = item.get("desc", "")
        coins = item.get("reward_coins", 0)
        title_to_equip = item.get("title_to_equip")
        is_upgrade = item.get("is_upgrade", False)
        prev_tier = item.get("previous_tier")
        features = item.get("features", [])
        
        with st.container(border=True):
            if is_upgrade and prev_tier:
                st.markdown(f"""
                <div style="
                    background: rgba(226, 74, 0, 0.08); 
                    border: 1px solid var(--accent-color, #E24A00); 
                    border-radius: 10px; 
                    padding: 6px 12px; 
                    margin-bottom: 10px; 
                    font-size: 0.85rem; 
                    font-weight: 700;
                    color: var(--accent-color, #E24A00);
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <span>⬆️ TIER UPGRADE:</span>
                    <span style="text-decoration: line-through; opacity: 0.7;">{prev_tier}</span>
                    <span>➔</span>
                    <span style="font-weight: 800;">{title}</span>
                </div>
                """, unsafe_allow_html=True)

            col_icon, col_txt = st.columns([1, 4])
            with col_icon:
                st.markdown(f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    width: 64px; 
                    height: 64px; 
                    background: var(--input-bg, #FFFFFF); 
                    border: 2px solid var(--accent-color, #E24A00); 
                    border-radius: 18px; 
                    font-size: 2.2rem; 
                    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
                    margin: auto;
                ">
                    {icon}
                </div>
                """, unsafe_allow_html=True)
            with col_txt:
                st.caption(f"**{category}**")
                st.markdown(f"### {title}")
                st.markdown(f"*{desc}*")
                if coins > 0:
                    st.markdown(f"🪙 **Bonus Reward:** `+{coins:,} Coins`")

            # If UI 2.0 Welcome, render interactive highlights
            if features:
                st.divider()
                st.markdown("#### 🚀 What's New in UI 2.0:")
                f_col1, f_col2 = st.columns(2)
                for f_idx, (f_title, f_desc) in enumerate(features):
                    with (f_col1 if f_idx % 2 == 0 else f_col2):
                        st.markdown(f"**{f_title}**")
                        st.caption(f_desc)

            # Action Buttons
            btn_col1, btn_col2 = st.columns([1.2, 1])
            with btn_col1:
                if title_to_equip and st.button(f"✨ Equip '{title_to_equip}'", key=f"equip_modal_btn_{idx}_{user}_{title}", use_container_width=True):
                    try:
                        save_user_preference(user, {"title": title_to_equip})
                        st.success(f"🎉 Equipped **{title_to_equip}** as your active badge!")
                        st.session_state.pop("celebration_unlocks", None)
                        time.sleep(0.8)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving badge: {e}")
            with btn_col2:
                if st.button("🚀 Awesome! Let's Go!", key=f"dismiss_modal_btn_{idx}_{user}_{title}", use_container_width=True):
                    st.session_state.pop("celebration_unlocks", None)
                    st.rerun()
                    
    # Bottom dismiss all button if multiple items
    if len(items) > 1:
        if st.button("Dismiss All Celebrations", key=f"dismiss_all_modal_{user}", use_container_width=True):
            st.session_state.pop("celebration_unlocks", None)
            st.rerun()

def open_celebration_dialog(user, items):
    """
    Sets pending celebration unlocks in session state and triggers an immediate rerun to display the modal safely.
    """
    if items:
        st.session_state["celebration_unlocks"] = items
        st.rerun()

def trigger_celebration_popup_if_pending(user):
    """
    Checks if there are pending unlocks in st.session_state and renders the celebration modal safely.
    """
    if "celebration_unlocks" in st.session_state and st.session_state["celebration_unlocks"]:
        items = list(st.session_state["celebration_unlocks"])
        try:
            _render_dialog_modal(user, items)
        except Exception:
            pass


