import streamlit as st
import pandas as pd
import datetime

# Import refactored modules
from database import get_data, get_transactions
from data_processing import (
    process_raw_data, 
    get_cumulative_data, 
    get_expense_and_caffeine, 
    get_user_preferences, 
    get_coin_balances, 
    get_gamification_metrics, 
    get_user_titles,
    resolve_user_title
)
from utils import enforce_user_identity
from world_data import TRAVEL_COUNTRIES, get_option_from_code
from components.ui import inject_custom_css, render_app_header
from components.charts import (
    render_pie_chart, 
    plot_metric, 
    plot_hourly_distribution, 
    plot_weekday_distribution, 
    plot_average_weekday_distribution, 
    plot_hot_vs_iced_distribution,
    plot_cumulative_projections
)

# Setup Page Configuration
st.set_page_config(page_title="Analytics & Trends", page_icon="📈", layout="wide")

users = ["Cris", "Bea", "Fer"]
selected_user = enforce_user_identity(users)

data = get_data()
transactions = get_transactions()
df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)

prefs = get_user_preferences(transactions, users)
user_theme = prefs.get(selected_user, {}).get("theme", "Latte (Light)")
user_style = prefs.get(selected_user, {}).get("ui_style", "Modern Flat")
inject_custom_css(user_theme, user_style, user=selected_user)

trophies = get_gamification_metrics(df_coffee, df_tea, users, transactions=transactions)
coin_balances = get_coin_balances(df, transactions, users)
user_coins = coin_balances.get(selected_user, 0)
user_streak = trophies.get("streaks", {}).get(selected_user, 0)
user_emoji = prefs.get(selected_user, {}).get("emoji", "☕")
user_title = resolve_user_title(selected_user, prefs, trophies)

# --- 1. Persistent App Header ---
render_app_header(
    selected_user=selected_user, 
    coin_balance=user_coins, 
    streak_days=user_streak, 
    custom_emoji=user_emoji, 
    custom_title=user_title
)

st.title("📈 Analytics & Consumption Trends")

if df.empty:
    st.info("No data yet! Go to the Home page to start logging drinks.")
    st.stop()

now = pd.Timestamp.now(tz="Europe/Madrid")

# --- 2. In-Page Segmented Filter Controls ---
with st.container(border=True):
    f_col1, f_col2 = st.columns([1, 1])
    with f_col1:
        drink_filter = st.segmented_control(
            "🥤 Select Beverage Focus", 
            ["All Drinks", "Coffee Only", "Tea Only"], 
            default="All Drinks"
        )
        if drink_filter is None:
            drink_filter = "All Drinks"
            
    with f_col2:
        date_filter = st.segmented_control(
            "📅 Timescale Window", 
            ["Last 7 Days", "Last 30 Days", "Year to Date", "All Time"], 
            default="Last 30 Days"
        )
        if date_filter is None:
            date_filter = "Last 30 Days"

# Apply Drink Filter
if drink_filter == "Coffee Only":
    df_filtered = df_coffee.copy()
elif drink_filter == "Tea Only":
    df_filtered = df_tea.copy()
else:
    df_filtered = df.copy()

# Add explicit drink labels for multi-line tracking
if not df_filtered.empty and "drink_id" in df_filtered.columns:
    mask_coffee = df_filtered["drink_id"].isin([1, 3])
    mask_tea = df_filtered["drink_id"].isin([2, 4])
    df_filtered.loc[mask_coffee, "user_name"] = df_filtered.loc[mask_coffee, "user_name"] + " (coffee)"
    df_filtered.loc[mask_tea, "user_name"] = df_filtered.loc[mask_tea, "user_name"] + " (tea)"

# Timezone localization
if df_filtered["created_at"].dt.tz is None:
    df_filtered["created_at"] = df_filtered["created_at"].dt.tz_localize("UTC")
df_filtered["created_at"] = df_filtered["created_at"].dt.tz_convert("Europe/Madrid")

df_all_dates = df_filtered.copy()

# Apply Date Filter
start_date = None
if date_filter == "Last 7 Days":
    start_date = now - pd.Timedelta(days=7)
elif date_filter == "Last 30 Days":
    start_date = now - pd.Timedelta(days=30)
elif date_filter == "Year to Date":
    start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)

if start_date:
    df_filtered = df_filtered[df_filtered["created_at"] >= start_date]

# --- 3. Hero KPI Deck (4 Elevated Cards) ---
if df_filtered.empty:
    st.warning("No data found for the selected filter combination.")
else:
    total_drinks = int(df_filtered["value"].sum())
    c_count = int(df_filtered[df_filtered["drink_id"].isin([1, 3])]["value"].sum()) if "drink_id" in df_filtered.columns else 0
    t_count = int(df_filtered[df_filtered["drink_id"].isin([2, 4])]["value"].sum()) if "drink_id" in df_filtered.columns else 0
    
    total_cost = (c_count * 2.50) + (t_count * 1.50)
    total_caffeine = (c_count * 95) + (t_count * 35)
    
    busiest_day = df_filtered["created_at"].dt.day_name().value_counts().idxmax()
    peak_hour = int(df_filtered["created_at"].dt.hour.value_counts().idxmax())
    peak_hour_str = f"{peak_hour:02d}:00"

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Drinks", f"{total_drinks:,}", delta=f"☕ {c_count} | 🍵 {t_count}")
    with kpi2:
        st.metric("Estimated Spend*", f"€{total_cost:.2f}", delta=f"€{(total_cost/max(total_drinks, 1)):.2f} / drink")
    with kpi3:
        st.metric("Total Caffeine*", f"{total_caffeine:,} mg", delta=f"{int(total_caffeine/max(total_drinks, 1))} mg / cup")
    with kpi4:
        st.metric("Peak Rhythm", f"{busiest_day}", delta=f"Peak Hour: {peak_hour_str}")

st.divider()

# --- 4. Interactive 5-Tab Analytical Suite ---
if not df_filtered.empty:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview & Cumulative Race",
        "⏰ Rhythm & Peak Hours",
        "🌡️ Temperature & Preference Duel",
        "🚀 Projections & Milestones",
        "🌍 Travel & Geography"
    ])
    
    chart_users = ["Cris (coffee)", "Cris (tea)", "Bea (coffee)", "Bea (tea)", "Fer (coffee)", "Fer (tea)"]

    # --- TAB 1: Overview & Cumulative Race ---
    with tab1:
        c_col1, c_col2 = st.columns([1, 1])
        with c_col1:
            with st.container(border=True):
                st.markdown("#### 🍩 Beverage Volume Share")
                pie_scores = df_filtered.groupby("user_name")["value"].sum().to_dict()
                render_pie_chart(pie_scores, "User", "Total Drinks", is_coffee=(drink_filter == "Coffee Only"))
        with c_col2:
            with st.container(border=True):
                st.markdown("#### 🏃 Cumulative Leaderboard Pace")
                if date_filter == "Last 7 Days":
                    c_start = now - pd.to_timedelta(now.dayofweek, unit='D')
                    c_start = c_start.replace(hour=0, minute=0, second=0, microsecond=0)
                elif start_date is None:
                    c_start = df_filtered["created_at"].min().floor("D")
                else:
                    c_start = start_date.floor("D")
                c_end = now.ceil("D")
                
                trend_df = get_cumulative_data(df_filtered, c_start, c_end, chart_users, "D")
                trend_title = f"Pace Trajectory ({date_filter})"
                plot_metric(trend_df, trend_title)

    # --- TAB 2: Rhythm & Peak Hours ---
    with tab2:
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            with st.container(border=True):
                st.markdown("#### ⏰ 24-Hour Circadian Brewing Cycle")
                plot_hourly_distribution(df_filtered)
        with r_col2:
            with st.container(border=True):
                st.markdown("#### 📅 Total Volume by Day of Week")
                plot_weekday_distribution(df_filtered)
                
        with st.container(border=True):
            avg_mode_col1, avg_mode_col2 = st.columns([2, 3])
            with avg_mode_col1:
                st.markdown("#### 📊 Daily Consumption Average")
            with avg_mode_col2:
                avg_mode = st.segmented_control(
                    "Average Method", 
                    ["📅 Calendar Normalized (Includes Zero Days)", "⚡ Raw (Active Days Only)"], 
                    default="📅 Calendar Normalized (Includes Zero Days)",
                    key="avg_mode_selector"
                )
                if avg_mode is None:
                    avg_mode = "📅 Calendar Normalized (Includes Zero Days)"
            
            calc_mode = "raw" if "Raw" in avg_mode else "normalized"
            if calc_mode == "raw":
                st.caption("⚡ **Raw Active Average**: Divides total drinks by the number of days you actually logged a beverage.")
            else:
                st.caption("📅 **Calendar-Normalized Average**: Divides total drinks by the total calendar days in the selected timeframe (including zero-logging days).")
                
            plot_average_weekday_distribution(df_filtered, title="Average Drinks per Weekday", mode=calc_mode)

    # --- TAB 3: Temperature Duel & Caffeine ---
    with tab3:
        t_col1, t_col2 = st.columns([3, 2])
        with t_col1:
            with st.container(border=True):
                st.markdown("#### 🧊 Hot vs. Iced Temperature Breakdown")
                st.caption("Compares preferences for Hot Coffee ☕, Iced Coffee 🧊☕, Hot Tea 🍵, and Iced Tea 🧊🍵.")
                plot_hot_vs_iced_distribution(df_filtered)
        with t_col2:
            with st.container(border=True):
                st.markdown("#### ⚡ Temperature Stats Breakdown")
                hot_c = int(df_filtered[df_filtered["drink_id"] == 1]["value"].sum())
                iced_c = int(df_filtered[df_filtered["drink_id"] == 3]["value"].sum())
                hot_t = int(df_filtered[df_filtered["drink_id"] == 2]["value"].sum())
                iced_t = int(df_filtered[df_filtered["drink_id"] == 4]["value"].sum())
                
                total_iced = iced_c + iced_t
                total_hot = hot_c + hot_t
                grand_total = total_iced + total_hot
                iced_pct = int((total_iced / grand_total * 100)) if grand_total > 0 else 0
                
                st.metric("Total Iced Drinks", f"{total_iced} 🧊", delta=f"{iced_pct}% of total drinks")
                st.metric("Total Hot Drinks", f"{total_hot} ☕", delta=f"{100-iced_pct}% of total drinks")
                st.caption("💡 *Temperature breakdown and drinking habits are continuously tracked.*")

    # --- TAB 4: Projections & Milestones ---
    with tab4:
        with st.container(border=True):
            st.markdown("#### 🚀 Predictive Trend Extrapolation")
            p_time = st.segmented_control("Forecast Horizon", ["This Week", "This Month", "This Year"], default="This Month")
            if p_time is None:
                p_time = "This Month"
                
            p_start = None
            p_end = None
            if p_time == "This Week":
                p_start = now - pd.to_timedelta(now.dayofweek, unit='D')
                p_start = p_start.replace(hour=0, minute=0, second=0, microsecond=0)
                p_end = p_start + pd.Timedelta(days=6, hours=23, minutes=59, seconds=59)
            elif p_time == "This Month":
                p_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = (p_start + pd.DateOffset(months=1))
                p_end = next_month - pd.Timedelta(seconds=1)
            elif p_time == "This Year":
                p_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                p_end = now.replace(month=12, day=31, hour=23, minute=59, second=59)
                
            df_proj = df_all_dates[df_all_dates["created_at"] >= p_start].copy()
            
            if df_proj.empty:
                st.info("Not enough data in this period to calculate a forecast.")
            else:
                projected_values = plot_cumulative_projections(df_proj, p_start, p_end, chart_users, title=f"Forecast to end of {p_time}")
                
                if projected_values:
                    st.markdown(f"**Predicted Total Drinks by end of {p_time}:**")
                    cols = st.columns(len(projected_values))
                    for i, (usr, val) in enumerate(projected_values.items()):
                        cols[i].metric(usr, f"{int(round(val))} drinks")

    # --- TAB 5: Travel & Geography ---
    with tab5:
        st.markdown("#### 🌍 Beverage Consumption by Country & Continent")
        st.caption("Geographic distribution of coffee and tea logs across the globe.")
        
        travel_logs = []
        if transactions:
            for tx in transactions:
                if tx.get("transaction_type") == "drink_log":
                    meta = tx.get("metadata", {})
                    c_code = meta.get("country") if isinstance(meta, dict) else None
                    if c_code and c_code in TRAVEL_COUNTRIES:
                        u = tx.get("user_name")
                        info = TRAVEL_COUNTRIES[c_code]
                        travel_logs.append({
                            "User": u,
                            "Country": f"{info['flag']} {info['name']}",
                            "Continent": info["continent"],
                            "Drinks": 1
                        })
        
        if not travel_logs:
            st.info("No travel location logs recorded yet. Once drinks are logged with country stamps, geographic breakdown analytics will appear here!")
        else:
            t_df = pd.DataFrame(travel_logs)
            tg_col1, tg_col2 = st.columns(2)
            with tg_col1:
                with st.container(border=True):
                    st.markdown("##### 🗺️ Drinks by Country")
                    country_counts = t_df.groupby("Country")["Drinks"].sum().reset_index().sort_values("Drinks", ascending=False)
                    st.dataframe(country_counts, use_container_width=True, hide_index=True)
            with tg_col2:
                with st.container(border=True):
                    st.markdown("##### 🌎 Drinks by Continent")
                    continent_counts = t_df.groupby("Continent")["Drinks"].sum().reset_index().sort_values("Drinks", ascending=False)
                    st.dataframe(continent_counts, use_container_width=True, hide_index=True)

    st.divider()
    st.caption("*Estimated cost and caffeine assumptions: Coffee (€2.50, 95mg), Tea (€1.50, 35mg).*")
    
    with st.expander("🔍 View Raw Log Data"):
        st.dataframe(df_filtered, use_container_width=True)
