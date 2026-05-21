import streamlit as st
import pandas as pd
from datetime import datetime

# Import refactored modules
from database import get_data, insert_click
from data_processing import process_raw_data, get_cumulative_data
from components.ui import inject_custom_css, render_header_and_quotes
from components.charts import render_pie_chart, plot_metric

# 1. Setup Page Configuration
st.set_page_config(page_title="Coffee is my best friend", page_icon=":coffee:")

# Inject CSS and Render Header
inject_custom_css()
render_header_and_quotes()

# User Configuration
users = ["Cris", "Bea", "Fer"]

# 2. Data Fetching & Processing
data = get_data()
df, df_coffee, df_tea, coffee_scores, tea_scores = process_raw_data(data, users)

# 3. Display Scores & Actions
st.header("Coffee Counter in 2026:")
cols = st.columns(len(users))

for idx, user in enumerate(users):
    c_score = coffee_scores.get(user, 0)
    t_score = tea_scores.get(user, 0)
    
    with cols[idx]:
        # --- Coffee Section ---
        st.metric(label=f"{user} (Coffee) :coffee:", value=c_score)
        
        # Check cooldown state
        last_click_time = None
        if not df.empty:
            user_clicks = df[df["user_name"] == user]
            if not user_clicks.empty:
                last_click_time = user_clicks["created_at"].max()

        if st.button(f"{user} took a coffee :coffee:", key=f"btn_coffee_{user}", use_container_width=True):
            if last_click_time:
                now = pd.Timestamp.now(tz=last_click_time.tz)
                time_diff = (now - last_click_time).total_seconds()
                if time_diff < 60:
                    st.warning(f"Wait {int(60 - time_diff)}s before adding another!")
                    st.stop()

            try:
                insert_click(user, 1, 1) # 1 for Coffee
                st.success("Coffee Counted!")
                st.rerun()
            except Exception as e:
                err_msg = str(e)
                if "Could not find the 'drink_id' column" in err_msg:
                    st.error("🚨 **Database Update Required** 🚨")
                    st.warning("To support tracking, you need to add a column to your Supabase table.")
                    st.info("Go to Supabase -> Table Editor -> `clicks` -> Add Column:\n- **Name**: `drink_id`\n- **Type**: `int` (or number)\n- **Default Value**: `1`")
                else:
                    st.error(f"Error: {e}")

        # --- Tea Section ---
        st.metric(label=f"{user} (Tea) 🍵", value=t_score)

        if st.button(f"{user} took a tea 🍵", key=f"btn_tea_{user}", use_container_width=True):
            if last_click_time:
                now = pd.Timestamp.now(tz=last_click_time.tz)
                time_diff = (now - last_click_time).total_seconds()
                if time_diff < 60:
                    st.warning(f"Wait {int(60 - time_diff)}s before adding another!")
                    st.stop()
            
            try:
                insert_click(user, 1, 2) # 2 for Tea
                st.success("Tea Counted!")
                st.rerun()
            except Exception as e:
                err_msg = str(e)
                if "Could not find the 'drink_id' column" in err_msg or "PGRST204" in err_msg:
                    st.error("🚨 **Database Update Required** 🚨")
                    st.warning("To support Tea tracking, you need to add a column to your Supabase table.")
                    st.info("Go to Supabase -> Table Editor -> `clicks` -> Add Column:\n- **Name**: `drink_id`\n- **Type**: `int` (or number)\n- **Default Value**: `1`")
                else:
                    st.error(f"Error: {e}")

# Total Count Display
total_coffees = sum(coffee_scores.values())
total_teas = sum(tea_scores.values())
st.markdown(f"<h3 style='text-align: center; color: #4A3B32;'>Totals: {total_coffees} Coffees :coffee: | {total_teas} Teas 🍵</h3>", unsafe_allow_html=True)
st.divider()

# 4. Analytics Section
st.header("Coffee Analytics 📈")

if not df_coffee.empty:
    st.subheader("Coffee Share 🍰")
    
    # Add Bea(tea) as requested
    pie_data = coffee_scores.copy()
    if "Bea" in tea_scores:
        pie_data["Bea(tea)"] = tea_scores["Bea"]

    render_pie_chart(pie_data, "Coffee friend", "Coffees", is_coffee=True)
    st.divider()

    now = pd.Timestamp.now(tz=df_coffee["created_at"].dt.tz)
    
    # --- Time Configurations ---
    today = now.floor("D")
    start_week = (today - pd.to_timedelta(today.dayofweek, unit='D')).replace(hour=0, minute=0, second=0, microsecond=0)
    end_week = (start_week + pd.Timedelta(days=6)).replace(hour=23, minute=59, second=59)
    
    start_month = today.replace(day=1)
    next_month = (start_month + pd.DateOffset(months=1))
    end_month = (next_month - pd.Timedelta(seconds=1))
    
    start_year = today.replace(month=1, day=1)
    end_year = today.replace(month=12, day=31).replace(hour=23, minute=59, second=59)

    # Calculate Dataframes (Coffee + Bea(tea))
    df_coffee_charts = df_coffee.copy()
    
    if not df_tea.empty:
        bea_tea = df_tea[df_tea["user_name"] == "Bea"].copy()
        if not bea_tea.empty:
            bea_tea["user_name"] = "Bea(tea)"
            df_coffee_charts = pd.concat([df_coffee_charts, bea_tea])

    chart_users = users + ["Bea(tea)"]
    df_week = get_cumulative_data(df_coffee_charts, start_week, end_week, chart_users, "D")
    df_month = get_cumulative_data(df_coffee_charts, start_month, end_month, chart_users, "D")
    df_year = get_cumulative_data(df_coffee_charts, start_year, end_year, chart_users, "D")

    # Display Charts Stacked
    st.subheader("This Week (Mon-Sun)")
    plot_metric(df_week, "")
    st.subheader("This Month")
    plot_metric(df_month, "")
    st.subheader("This Year")
    plot_metric(df_year, "")

    # --- Tea Analytics ---
    st.divider()
    st.header("Tea Analytics 🍵")

    if not df_tea.empty:
        st.subheader("Tea Share 🍵")
        render_pie_chart(tea_scores, "Tea friend", "Teas", is_coffee=False)
        st.divider()

        tea_week = get_cumulative_data(df_tea, start_week, end_week, users, "D")
        tea_month = get_cumulative_data(df_tea, start_month, end_month, users, "D")
        tea_year = get_cumulative_data(df_tea, start_year, end_year, users, "D")

        st.subheader("Tea - This Week")
        plot_metric(tea_week, "Cups of Tea")
        st.subheader("Tea - This Month")
        plot_metric(tea_month, "Cups of Tea")
        st.subheader("Tea - This Year")
        plot_metric(tea_year, "Cups of Tea")
    else:
        st.info("No tea data found yet. Drink some tea!")
    
    with st.expander("Show Raw Data"):
         st.dataframe(df, use_container_width=True)

else:
    st.info("No coffee data yet! Click a button to start the history.")
