import streamlit as st
import pandas as pd
import datetime

# Import refactored modules
from database import get_data
from data_processing import process_raw_data, get_cumulative_data, get_expense_and_caffeine
from components.ui import inject_custom_css
from components.charts import render_pie_chart, plot_metric, plot_hourly_distribution, plot_weekday_distribution, plot_average_weekday_distribution, plot_cumulative_projections

# Setup Page Configuration
st.set_page_config(page_title="Coffee is my best friend", page_icon="📈", layout="wide")
inject_custom_css()

users = ["Cris", "Bea", "Fer"]

data = get_data()
df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)

st.title("Graphs! Graphs! Graphs! 📈")

if df.empty:
    st.info("No data yet! Go to the Home page to start logging drinks.")
    st.stop()

# --- Filters ---
st.sidebar.header("Filter Data")

drink_filter = st.sidebar.radio("Drink Type", ["All", "Coffee", "Tea"])

date_filter = st.sidebar.selectbox("Date Range", [
    "Last 7 Days",
    "Last 30 Days",
    "Year to Date",
    "All Time"
])

# Apply Drink Filter
if drink_filter == "Coffee":
    df_filtered = df_coffee.copy()
elif drink_filter == "Tea":
    df_filtered = df_tea.copy()
else:
    df_filtered = df.copy()

# Add explicit drink labels to all users
if not df_filtered.empty and "drink_id" in df_filtered.columns:
    mask_coffee = df_filtered["drink_id"] == 1
    mask_tea = df_filtered["drink_id"] == 2
    df_filtered.loc[mask_coffee, "user_name"] = df_filtered.loc[mask_coffee, "user_name"] + " (coffee)"
    df_filtered.loc[mask_tea, "user_name"] = df_filtered.loc[mask_tea, "user_name"] + " (tea)"

# Localize to Madrid for filtering
if df_filtered["created_at"].dt.tz is None:
    df_filtered["created_at"] = df_filtered["created_at"].dt.tz_localize("UTC")
df_filtered["created_at"] = df_filtered["created_at"].dt.tz_convert("Europe/Madrid")

now = pd.Timestamp.now(tz="Europe/Madrid")

# Save a copy before date filtering for projections
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

# --- Top-Level KPI Cards ---
st.subheader("Key Performance Indicators")

if df_filtered.empty:
    st.warning("No data found for the selected filters.")
else:
    total_drinks = df_filtered["value"].sum()
    
    # Calculate costs and caffeine for the filtered selection
    c_count = df_filtered[df_filtered["drink_id"] == 1]["value"].sum() if "drink_id" in df_filtered.columns else 0
    t_count = df_filtered[df_filtered["drink_id"] == 2]["value"].sum() if "drink_id" in df_filtered.columns else 0
    
    total_cost = (c_count * 2.50) + (t_count * 1.50)
    total_caffeine = (c_count * 95) + (t_count * 30)
    
    # Busiest day
    busiest_day = df_filtered["created_at"].dt.day_name().value_counts().idxmax()
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Drinks", int(total_drinks))
    kpi2.metric("Estimated Cost*", f"€{total_cost:.2f}")
    kpi3.metric("Estimated Caffeine*", f"{int(total_caffeine)} mg")
    kpi4.metric("Busiest Day", busiest_day)

st.divider()

if not df_filtered.empty:
    # --- Advanced Visualizations ---
    chart_users = ["Cris (coffee)", "Cris (tea)", "Bea (coffee)", "Bea (tea)", "Fer (coffee)", "Fer (tea)"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Drink Share 🍰")
        # Prepare data for pie chart based on filtered set
        pie_scores = df_filtered.groupby("user_name")["value"].sum().to_dict()
        render_pie_chart(pie_scores, "User", "Total Drinks", is_coffee=(drink_filter == "Coffee"))
        
    with col2:
        st.subheader("Cumulative Trend 📈")
        # Use get_cumulative_data on the filtered range
        if date_filter == "Last 7 Days":
            # Show ONLY this calendar week instead of rolling 7 days
            c_start = now - pd.to_timedelta(now.dayofweek, unit='d')
            c_start = c_start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif start_date is None:
            c_start = df_filtered["created_at"].min().floor("D")
        else:
            c_start = start_date.floor("D")
            
        c_end = now.ceil("D")
        
        trend_df = get_cumulative_data(df_filtered, c_start, c_end, chart_users, "D")
        trend_title = "This Week" if date_filter == "Last 7 Days" else date_filter
        plot_metric(trend_df, f"Trend ({trend_title})")
        
    st.divider()
    
    col3, col4 = st.columns(2)
    with col3:
        plot_hourly_distribution(df_filtered)
        
    with col4:
        plot_weekday_distribution(df_filtered)
        
    st.divider()
    
    # --- Averages Section ---
    st.subheader("Averages 📊")
    plot_average_weekday_distribution(df_filtered)
        
    st.divider()
    
    # --- Projections Section ---
    st.subheader("Projections 🚀")
    proj_filter = st.selectbox("Projection Timescale", ["This Week", "This Month", "This Year"])
    
    p_start = None
    p_end = None
    if proj_filter == "This Week":
        p_start = now - pd.to_timedelta(now.dayofweek, unit='d')
        p_start = p_start.replace(hour=0, minute=0, second=0, microsecond=0)
        p_end = p_start + pd.Timedelta(days=6, hours=23, minutes=59, seconds=59)
    elif proj_filter == "This Month":
        p_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (p_start + pd.DateOffset(months=1))
        p_end = next_month - pd.Timedelta(seconds=1)
    elif proj_filter == "This Year":
        p_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        p_end = now.replace(month=12, day=31, hour=23, minute=59, second=59)
        
    df_proj = df_all_dates[df_all_dates["created_at"] >= p_start].copy()
    
    if df_proj.empty:
        st.info("No data in this period to project from.")
    else:
        projected_values = plot_cumulative_projections(df_proj, p_start, p_end, chart_users, title=f"Projection to end of {proj_filter}")
        
        if projected_values:
            st.markdown(f"**Projected Total Drinks by end of {proj_filter}:**")
            cols = st.columns(len(projected_values))
            for i, (usr, val) in enumerate(projected_values.items()):
                cols[i].metric(usr, f"{int(round(val))}")

    st.divider()
    
    st.caption("*Estimated cost and caffeine are calculated based on the following assumptions: Coffee (€2.50, 95mg), Tea (€1.50, 30mg).*")
    
    with st.expander("Show Raw Data"):
        st.dataframe(df_filtered, use_container_width=True)
