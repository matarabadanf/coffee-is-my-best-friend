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
        crowns.add("👑 Caffeine Emperor")
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

def compute_new_unlocks(user, before_snapshot, after_snapshot, is_dev_test=False):
    """
    Compares snapshots and returns a list of celebration items.
    """
    unlocks = []
    
    # Dev test trigger for Fer (or dev mode testing)
    if is_dev_test and user == "Fer":
        unlocks.append({
            "type": "dev_test",
            "category": "🛠️ DEV PREVIEW UNLOCK PROTOCOL",
            "title": "🧪 Quantum Brew Pioneer",
            "tier": "Legendary",
            "icon": "🚀",
            "badge": "🧪 Quantum Brew Pioneer",
            "desc": "Triggered real-time quantum beverage synthesis in Developer Preview mode. All systems nominal!",
            "reward_coins": 100,
            "can_equip_title": True,
            "title_to_equip": "🧪 Quantum Brew Pioneer"
        })
        
    # 1. New Tiers
    new_tiers = after_snapshot["tiers"] - before_snapshot["tiers"]
    for track_id, level, name in new_tiers:
        coins = 50 if level in ["Bronze", "Silver"] else (100 if level == "Gold" else 200)
        unlocks.append({
            "type": "tier",
            "category": "🎖️ ACHIEVEMENT TIER UNLOCKED!",
            "title": f"{level}: {name}",
            "tier": level,
            "icon": "🏆",
            "badge": name,
            "desc": f"New mastery unlocked in {track_id.replace('_', ' ').title()}! Progressing towards the next milestone!",
            "reward_coins": coins,
            "can_equip_title": True,
            "title_to_equip": name
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
        
    # 3. New Monarch Crowns
    new_crowns = after_snapshot["crowns"] - before_snapshot["crowns"]
    for crown in new_crowns:
        unlocks.append({
            "type": "monarch",
            "category": "👑 GLOBAL MONARCH CROWN CLAIMED!",
            "title": crown,
            "tier": "Monarch",
            "icon": "👑",
            "badge": crown,
            "desc": f"You have claimed the sovereign throne as {crown}!",
            "reward_coins": 250,
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
        
        with st.container(border=True):
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

def trigger_celebration_popup_if_pending(user):
    """
    Checks if there are pending unlocks in st.session_state and renders the celebration modal.
    """
    if "celebration_unlocks" in st.session_state and st.session_state["celebration_unlocks"]:
        items = list(st.session_state["celebration_unlocks"])
        _render_dialog_modal(user, items)
