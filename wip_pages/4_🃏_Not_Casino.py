import streamlit as st
import random

from database import get_data, get_transactions, insert_transaction
from data_processing import process_raw_data, get_coin_balances, get_user_preferences, get_gamification_metrics, get_user_titles
from utils import verify_pin, is_pin_verified, enforce_user_identity
from components.ui import inject_custom_css, render_app_header

st.set_page_config(page_title="Not Casino", page_icon="🃏", layout="wide")

users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

data = get_data()
transactions = get_transactions()

prefs = get_user_preferences(transactions, users)
user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")
inject_custom_css(user_theme, user_style)

df, df_coffee, df_tea, _, _ = process_raw_data(data, users)
trophies = get_gamification_metrics(df_coffee, df_tea, users)
coin_balances = get_coin_balances(df, transactions, users)
balance = coin_balances.get(selected_user, 0)
user_streak = trophies.get("streaks", {}).get(selected_user, 0)
user_emoji = prefs.get(selected_user, {}).get("emoji", "☕")
user_title = prefs.get(selected_user, {}).get("title") or get_user_titles(selected_user, trophies)

# Native App Header
render_app_header(
    selected_user=selected_user, 
    coin_balance=balance, 
    streak_days=user_streak, 
    custom_emoji=user_emoji, 
    custom_title=user_title
)

st.title("🃏 Not Casino (Blackjack & Games)")

st.divider()

# Blackjack logic using session state
if "deck" not in st.session_state:
    st.session_state.deck = []
if "player_hand" not in st.session_state:
    st.session_state.player_hand = []
if "dealer_hand" not in st.session_state:
    st.session_state.dealer_hand = []
if "game_over" not in st.session_state:
    st.session_state.game_over = True
if "bet" not in st.session_state:
    st.session_state.bet = 0

def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [{'rank': r, 'suit': s} for s in suits for r in ranks]
    random.shuffle(deck)
    return deck

def card_value(card):
    if card['rank'] in ['J', 'Q', 'K']: return 10
    if card['rank'] == 'A': return 11
    return int(card['rank'])

def hand_value(hand):
    val = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c['rank'] == 'A')
    while val > 21 and aces > 0:
        val -= 10
        aces -= 1
    return val

def render_card(card, hidden=False):
    if hidden:
        return """<div style="display: inline-block; width: 60px; height: 90px; border: 1px solid #444; border-radius: 5px; background-color: #2c3e50; background-image: repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(255,255,255,.1) 5px, rgba(255,255,255,.1) 10px); margin: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.5);"></div>"""
    
    color = '#d32f2f' if card['suit'] in ['♥', '♦'] else '#111'
    
    return f"""<div style="display: inline-block; width: 60px; height: 90px; border: 1px solid #ccc; border-radius: 5px; background-color: white; margin: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); position: relative; color: {color}; font-family: Arial, sans-serif;">
<div style="position: absolute; top: 5px; left: 5px; font-size: 14px; font-weight: bold; line-height: 1;">{card['rank']}<br>{card['suit']}</div>
<div style="position: absolute; bottom: 5px; right: 5px; font-size: 14px; font-weight: bold; line-height: 1; transform: rotate(180deg);">{card['rank']}<br>{card['suit']}</div>
<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 24px;">{card['suit']}</div>
</div>"""

def render_hand(hand, hide_second=False):
    html = '<div style="display: flex; flex-direction: row; flex-wrap: wrap;">'
    for i, card in enumerate(hand):
        if hide_second and i == 1:
            html += render_card(card, hidden=True)
        else:
            html += render_card(card)
    html += '</div>'
    return html

if st.session_state.game_over:
    if len(st.session_state.player_hand) > 0:
        st.write("### Last Game Result")
        
        col_d, col_p = st.columns(2)
        with col_d:
            st.write(f"**Dealer's Final Hand:** (Total: {hand_value(st.session_state.dealer_hand)})")
            st.markdown(render_hand(st.session_state.dealer_hand), unsafe_allow_html=True)
            
        with col_p:
            st.write(f"**Your Final Hand:** (Total: {hand_value(st.session_state.player_hand)})")
            st.markdown(render_hand(st.session_state.player_hand), unsafe_allow_html=True)
        
        # Calculate outcome text based on value
        p_val = hand_value(st.session_state.player_hand)
        d_val = hand_value(st.session_state.dealer_hand)
        if p_val > 21:
            st.error(f"Bust! You lost 🪙 {st.session_state.bet}.")
        elif p_val == 21 and len(st.session_state.player_hand) == 2:
            st.success(f"Blackjack! You won 🪙 {int(st.session_state.bet * 1.5)}!")
        elif d_val > 21 or p_val > d_val:
            st.success(f"You Win! 🪙 {st.session_state.bet} added.")
        elif d_val > p_val:
            st.error(f"Dealer Wins. You lost 🪙 {st.session_state.bet}.")
        else:
            st.info("Push. It's a tie, no coins lost.")

        if st.button("Clear Table"):
            st.session_state.player_hand = []
            st.session_state.dealer_hand = []
            st.rerun()
            
        st.divider()
        
    st.write("### Start a New Game")
    bet = st.number_input("Enter your bet (Coins):", min_value=10, max_value=max(10, int(balance)), step=10)
    
    pin = ""
    if not is_pin_verified(selected_user):
        pin = st.text_input("Confirm with PIN to start:", type="password")
    else:
        st.success("🔓 PIN unlocked for 5 minutes.")
    
    if st.button("Deal"):
        if bet > balance:
            st.error("Insufficient funds!")
        elif not verify_pin(selected_user, pin):
            pass 
        else:
            st.session_state.bet = bet
            st.session_state.deck = create_deck()
            st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
            st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
            st.session_state.game_over = False
            
            if hand_value(st.session_state.player_hand) == 21:
                st.session_state.game_over = True
                winnings = int(bet * 1.5)
                insert_transaction(selected_user, winnings, "casino", {"game": "blackjack", "result": "blackjack"})
                st.success(f"BLACKJACK! You won 🪙 {winnings}!")
            st.rerun()

else:
    st.write(f"**Bet:** 🪙 {st.session_state.bet}")
    
    st.write("### Dealer's Hand")
    st.markdown(render_hand(st.session_state.dealer_hand, hide_second=True), unsafe_allow_html=True)
    st.write(f"Total: {card_value(st.session_state.dealer_hand[0])} + ?")
    
    st.write("### Your Hand")
    st.markdown(render_hand(st.session_state.player_hand), unsafe_allow_html=True)
    st.write(f"Total: {hand_value(st.session_state.player_hand)}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Hit"):
            st.session_state.player_hand.append(st.session_state.deck.pop())
            if hand_value(st.session_state.player_hand) > 21:
                st.session_state.game_over = True
                insert_transaction(selected_user, -st.session_state.bet, "casino", {"game": "blackjack", "result": "bust"})
            st.rerun()
            
    with col2:
        if st.button("Stand"):
            while hand_value(st.session_state.dealer_hand) < 17:
                st.session_state.dealer_hand.append(st.session_state.deck.pop())
                
            dealer_val = hand_value(st.session_state.dealer_hand)
            player_val = hand_value(st.session_state.player_hand)
            
            st.session_state.game_over = True
            
            if dealer_val > 21 or player_val > dealer_val:
                insert_transaction(selected_user, st.session_state.bet, "casino", {"game": "blackjack", "result": "win"})
            elif dealer_val > player_val:
                insert_transaction(selected_user, -st.session_state.bet, "casino", {"game": "blackjack", "result": "lose"})
            else:
                pass # tie, no transaction
            st.rerun()


