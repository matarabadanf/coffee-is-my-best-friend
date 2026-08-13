import streamlit as st
import pandas as pd
import yfinance as yf

from database import get_data, get_transactions, insert_transaction
from data_processing import process_raw_data, get_coin_balances, get_user_preferences, get_gamification_metrics, get_user_titles
from utils import verify_pin, is_pin_verified, enforce_user_identity
from components.ui import inject_custom_css, render_app_header

st.set_page_config(page_title="Not Stocks", page_icon="📈", layout="wide")

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

st.title("📈 Not Stocks (Beverage Exchange)")

# Calculate Portfolio
portfolio = {}
tx_df = pd.DataFrame(transactions)
if not tx_df.empty and "transaction_type" in tx_df.columns:
    stock_buys = tx_df[tx_df["transaction_type"] == "stock_buy"]
    stock_sells = tx_df[tx_df["transaction_type"] == "stock_sell"]
    
    for _, row in stock_buys.iterrows():
        if row["user_name"] == selected_user:
            meta = row.get("metadata", {})
            ticker = meta.get("ticker")
            shares = meta.get("shares", 0)
            if ticker:
                portfolio[ticker] = portfolio.get(ticker, 0) + shares
                
    for _, row in stock_sells.iterrows():
        if row["user_name"] == selected_user:
            meta = row.get("metadata", {})
            ticker = meta.get("ticker")
            shares = meta.get("shares", 0)
            if ticker:
                portfolio[ticker] = portfolio.get(ticker, 0) - shares

st.subheader(f"Your Balance: 🪙 {balance}")

stocks = {
    "SBUX": "Starbucks Corp",
    "NESN.SW": "Nestlé S.A.",
    "JDEP.AS": "JDE Peet's",
    "LKNCY": "Luckin Coffee"
}

@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    return hist

st.divider()
st.subheader("Market")

selected_ticker = st.selectbox("Select a company:", list(stocks.keys()), format_func=lambda x: f"{x} - {stocks[x]}")

hist = get_stock_data(selected_ticker)
if not hist.empty:
    current_price = hist["Close"].iloc[-1]
    st.metric("Current Price (USD)", f"${current_price:.2f}")
    st.line_chart(hist["Close"])
    
    # We map $1 USD = 1 Coin for simplicity
    st.write(f"**Price in Coins:** 🪙 {int(current_price)}")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.popover("Buy Shares"):
            shares_to_buy = st.number_input("Shares to buy", min_value=1, step=1, key="buy_shares")
            cost = int(shares_to_buy * current_price)
            st.write(f"Total cost: 🪙 {cost}")
            pin = ""
            if not is_pin_verified(selected_user):
                pin = st.text_input("PIN", type="password", key="buy_pin")
            else:
                st.success("🔓 PIN unlocked for 5 minutes.")
                
            if st.button("Confirm Buy"):
                if balance < cost:
                    st.error("Not enough coins!")
                elif verify_pin(selected_user, pin):
                    insert_transaction(selected_user, -cost, "stock_buy", {"ticker": selected_ticker, "shares": shares_to_buy, "price": current_price})
                    st.success(f"Bought {shares_to_buy} shares of {selected_ticker}!")
                    st.rerun()
                    
    with col2:
        owned_shares = portfolio.get(selected_ticker, 0)
        with st.popover(f"Sell Shares (Owned: {owned_shares})"):
            shares_to_sell = st.number_input("Shares to sell", min_value=1, max_value=max(1, owned_shares), step=1, key="sell_shares")
            revenue = int(shares_to_sell * current_price)
            st.write(f"Total revenue: 🪙 {revenue}")
            pin_sell = ""
            if not is_pin_verified(selected_user):
                pin_sell = st.text_input("PIN", type="password", key="sell_pin")
            else:
                st.success("🔓 PIN unlocked for 5 minutes.")
                
            if st.button("Confirm Sell"):
                if shares_to_sell > owned_shares:
                    st.error("You don't own that many shares!")
                elif verify_pin(selected_user, pin_sell):
                    insert_transaction(selected_user, revenue, "stock_sell", {"ticker": selected_ticker, "shares": shares_to_sell, "price": current_price})
                    st.success(f"Sold {shares_to_sell} shares of {selected_ticker}!")
                    st.rerun()
else:
    st.error("Failed to load stock data.")

st.divider()
st.subheader("Your Portfolio")
total_net_worth = balance
has_stocks = False
for ticker, shares in portfolio.items():
    if shares > 0:
        has_stocks = True
        h = get_stock_data(ticker)
        if not h.empty:
            cp = h["Close"].iloc[-1]
            val = int(shares * cp)
            total_net_worth += val
            st.write(f"- **{ticker}**: {shares} shares (Value: 🪙 {val})")

if not has_stocks:
    st.write("You don't own any stocks yet.")
    
st.write(f"### Total Net Worth: 🪙 {total_net_worth}")
