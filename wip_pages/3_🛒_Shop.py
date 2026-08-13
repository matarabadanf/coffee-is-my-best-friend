import streamlit as st
import pandas as pd

from database import get_data, get_transactions, insert_transaction
from data_processing import process_raw_data, get_coin_balances, get_user_preferences
from utils import verify_pin, is_pin_verified, enforce_user_identity
from components.ui import inject_custom_css

st.set_page_config(page_title="Power-up Shop", page_icon="🛒", layout="centered")

users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

data = get_data()
transactions = get_transactions()

prefs = get_user_preferences(transactions, users)
user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")
inject_custom_css(user_theme, user_style)

st.title("🛒 The Power-up Shop")
st.markdown(f"#### 👤 Logged in as: <span class='user-highlight'>{selected_user}</span>", unsafe_allow_html=True)
st.markdown("Spend your hard-earned coins on tactical perks, leaderboard flexes, and mild sabotage.")
st.caption("🎨 *Looking for beverage themes and visual styles? Check out the dedicated **🎨 Theme Shop** in the sidebar!*")
st.divider()

df, _, _, _, _ = process_raw_data(data, users)
coin_balances = get_coin_balances(df, transactions, users)
balance = coin_balances.get(selected_user, 0)

st.subheader(f"Your Balance: 🪙 `{balance} Coins`")
st.divider()

shop_items = [
    {
        "id": "golden_mug",
        "name": "🏆 Golden Mug",
        "price": 150,
        "desc": "Flex on everyone with a golden mug badge for 24 hours.",
        "duration_hours": 24
    },
    {
        "id": "coffee_break",
        "name": "🚫 Coffee Break",
        "price": 300,
        "desc": "Force another user to take a break. They cannot log drinks for 2 hours.",
        "duration_hours": 2,
        "requires_target": True
    },
    {
        "id": "tax_the_rich",
        "name": "🤑 Tax the Rich",
        "price": 500,
        "desc": "Take 10% of the richest player's coins and claim them for yourself.",
        "duration_hours": 0
    }
]

for item in shop_items:
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {item['name']}")
            st.write(item['desc'])
            st.markdown(f"**Price:** 🪙 `{item['price']} Coins`")
            
            target = None
            if item.get("requires_target"):
                target = st.selectbox(
                    f"Select Target for {item['name']}:", 
                    [u for u in users if u != selected_user], 
                    key=f"target_{item['id']}"
                )
                
        with col2:
            with st.popover(f"🪙 Buy for {item['price']}", use_container_width=True):
                pin = ""
                if not is_pin_verified(selected_user):
                    st.write("Confirm purchase with PIN:")
                    pin = st.text_input("PIN", type="password", key=f"pin_{item['id']}")
                else:
                    st.success("🔓 PIN session verified.")
                    
                if st.button("Confirm", key=f"btn_{item['id']}", use_container_width=True):
                    if balance < item["price"]:
                        st.error("Not enough coins!")
                    elif verify_pin(selected_user, pin):
                        # Process Tax the Rich
                        if item["id"] == "tax_the_rich":
                            richest = max(coin_balances, key=coin_balances.get)
                            if richest == selected_user:
                                st.error("You are the richest! You can't tax yourself.")
                            else:
                                tax_amount = int(coin_balances[richest] * 0.1)
                                insert_transaction(selected_user, -item["price"], "shop", {"item": item["id"]})
                                insert_transaction(richest, -tax_amount, "tax_penalty", {"by": selected_user})
                                insert_transaction(selected_user, tax_amount, "tax_reward", {"from": richest})
                                st.success(f"Taxed {richest} for {tax_amount} coins!")
                                st.rerun()
                        else:
                            meta = {"item": item["id"], "perk": item["id"]}
                            if item["duration_hours"] > 0:
                                expires = pd.Timestamp.now(tz="UTC") + pd.Timedelta(hours=item["duration_hours"])
                                meta["expires_at"] = expires.isoformat()
                            
                            if item.get("requires_target"):
                                insert_transaction(selected_user, -item["price"], "shop", {"item": item["id"]})
                                insert_transaction(target, 0, "shop", meta)
                                st.success(f"Applied {item['name']} to {target}!")
                            else:
                                insert_transaction(selected_user, -item["price"], "shop", meta)
                                st.success("Purchase successful!")
                        
                        st.rerun()
