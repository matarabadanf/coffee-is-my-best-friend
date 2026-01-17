import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# 1. Setup Page Configuration
st.set_page_config(page_title="Coffee is my best friend", page_icon=":coffee:")

# Custom CSS for Soft Beige Background
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F9F3E3; /* Soft Beige / Cream */
        color: #4A3B32; /* Coffee-ish text color for contrast */
    }
    
    /* Tea Button Style */
    .stButton > button:first-child {
         border-radius: 20px;
    }
    
    /* Optional: Style metrics to look good on beige */
    /* Force all text inside metrics to be black */
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #000000 !important;
    }
    
    /* Style buttons to look like coffee beans */
    .stButton > button {
        background-color: #4A3B32; /* Coffee bean color */
        color: white; /* White text as requested */
        border: none;
    }
    .stButton > button:hover {
        background-color: #6F4E37; /* Lighter roast on hover */
        color: white;
    }
    
    /* Warning message contrast fix */
    div[data-testid="stAlert"] > div {
        color: #2C1A11 !important; /* Force dark coffee color */
    }
    div[data-testid="stAlert"] p {
        color: #2C1A11 !important; /* Force paragraph text dark */
    }
    
    /* Fix Tab Text Contrast */
    .stTabs [data-baseweb="tab"] {
        color: #4A3B32; /* Coffee color */
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #2C1A11; /* Darker when selected */
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. Connection Setup
# Explanation: We use st.secrets to securely access API keys without hardcoding them.
# The .streamlit/secrets.toml file is local-only and ignored by git.
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
except FileNotFoundError:
    st.error("Secrets not found! Please create .streamlit/secrets.toml")
    st.stop()

# Initialize Supabase Client
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(url, key)

supabase = get_supabase_client()

# 3. Application Logic
st.title("Coffee is my best friend :coffee:")
st.write("Yes. This is actually happening.")
st.write("Once Cris said:")
st.markdown('### "Dios no creo que oiga una frikada mayor de lo que acabo de oir."')
st.markdown('However, **this is the newest "frikada"**.')

import random
st.divider()
st.header("Coffee Quote:")
coffee_sentences = [
    # Translated Classics
    # "Coffee helps those who sleep little and dream distinctively.",
    # "Life begins after coffee.",
    # "Everything is possible with enough coffee.",
    # "Better latte than never.",
    # "I try to drink coffee with friends; everything tastes better with them.",
    # "A day without coffee is like... just kidding, I have no idea.",
    # "Coffee is a hug in a mug.",
    
    # The "Bad Jokes" Collection (Cats, Lasers, Proteins, Electrons)
    "Caffeine excites my electrons to a higher energy state.",
    "Coffee: The essential cofactor for my productivity enzymes.",
    "I need coffee right meow.",
    "Warning: Coffee may cause laser-like focus on absolutely nothing.",
    "My energy level is in the ground state. Insert coffee to excite electrons.",
    "Coffee and cats: profound vibration experts.",
    "Resistance is futile. You will be caffeinated."
]
st.info(f"✨ {random.choice(coffee_sentences)} ✨")
st.divider()

# User Configuration
users = ["Cris", "Bea", "Fer"]

# 4. Data Fetching
def get_data():
    try:
        response = supabase.table("clicks").select("*").execute()
        return response.data
    except Exception:
        return []

data = get_data()

# 5. Calculate Scores (Independent)
if data:
    df = pd.DataFrame(data)
    
    # Ensure drink_id exists (fill with 1 for Coffee if missing)
    if "drink_id" not in df.columns:
        df["drink_id"] = 1
    else:
        df["drink_id"] = df["drink_id"].fillna(1)
    
    
    # 2. Convert timestamps immediately (before splitting)
    # This prevents the "AttributeError: Can only use .dt accessor" later
    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    
    # Separate Dataframes
    df_coffee = df[df["drink_id"] == 1]
    df_tea = df[df["drink_id"] == 2]
    
    # Calculate Scores
    coffee_scores = df_coffee.groupby("user_name")["value"].sum().to_dict()
    tea_scores = df_tea.groupby("user_name")["value"].sum().to_dict()
else:
    coffee_scores = {}
    tea_scores = {}
    df = pd.DataFrame() 
    df_coffee = pd.DataFrame()
    df_tea = pd.DataFrame()

# 6. Display Scores & Actions
st.header("Coffee Counter in 2026:")
cols = st.columns(len(users))

# Pre-process timestamps if data exists
# (Moved up to Step 5)

for idx, user in enumerate(users):
    c_score = coffee_scores.get(user, 0)
    t_score = tea_scores.get(user, 0)
    
    with cols[idx]:
        # --- Coffee Section ---
        st.metric(label=f"{user} (Coffee) :coffee:", value=c_score)
        
        # Check cooldown state (Global cooldown)
        last_click_time = None
        if not df.empty:
            user_clicks = df[df["user_name"] == user]
            if not user_clicks.empty:
                last_click_time = user_clicks["created_at"].max()

        # Coffee Button
        if st.button(f"{user} took a coffee :coffee:", key=f"btn_coffee_{user}", use_container_width=True):
            # Cooldown Logic
            if last_click_time:
                now = pd.Timestamp.now(tz=last_click_time.tz)
                time_diff = (now - last_click_time).total_seconds()
                if time_diff < 60:
                    st.warning(f"Wait {int(60 - time_diff)}s before adding another!")
                    st.stop()

            # Coffee = 1
            event_data = {
                "user_name": user,
                "value": 1,
                "drink_id": 1 # 1 for Coffee
            }
            try:
                supabase.table("clicks").insert(event_data).execute()
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

        # Tea Button
        if st.button(f"{user} took a tea 🍵", key=f"btn_tea_{user}", use_container_width=True):
             # Cooldown Logic
            if last_click_time:
                now = pd.Timestamp.now(tz=last_click_time.tz)
                time_diff = (now - last_click_time).total_seconds()
                if time_diff < 60:
                    st.warning(f"Wait {int(60 - time_diff)}s before adding another!")
                    st.stop()
            
            # Tea = 1
            event_data = {
                "user_name": user,
                "value": 1,
                "drink_id": 2 # 2 for Tea
            }
            try:
                supabase.table("clicks").insert(event_data).execute()
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

# Analytics Section
st.header("Coffee Analytics 📈")

if not df_coffee.empty:
    # --- Pie Chart Section ---
    st.subheader("Coffee Share 🍰")
    
    # Prepare data for Pie Chart
    # Add Bea(tea) as requested
    pie_data = coffee_scores.copy()
    if "Bea" in tea_scores:
        pie_data["Bea(tea)"] = tea_scores["Bea"]

    pie_df = pd.DataFrame(list(pie_data.items()), columns=['Coffee friend', 'Coffees'])
    pie_df['Percentage'] = pie_df['Coffees'] / pie_df['Coffees'].sum()
    
    # --- Color Configuration ---
    # Define custom colors
    domain = ["Cris", "Bea", "Fer", "Bea(tea)"]
    range_ = ["#1f77b4", "#ff7f0e", "rebeccapurple", "#2ca02c"] # Blue, Orange, RebeccaPurple, Green

    import altair as alt
    
    # Base chart
    base = alt.Chart(pie_df).encode(
        theta=alt.Theta("Coffees", stack=True)
    )
    
    # Pie slices
    pie = base.mark_arc(outerRadius=100).encode(
        color=alt.Color("Coffee friend", scale=alt.Scale(domain=domain, range=range_)),
        order=alt.Order("Coffees", sort="descending"),
        tooltip=["Coffee friend", "Coffees", alt.Tooltip("Percentage", format=".1%")]
    )
    
    # Text labels (Percentages)
    text = base.mark_text(radius=120).encode(
        text=alt.Text("Percentage", format=".1%"),
        order=alt.Order("Coffees", sort="descending"),
        color=alt.value("#4A3B32")  # Dark coffee color
    )
    
    
    # Combine and Style
    chart_pie = (pie + text).properties(
        title="",
        height=350
    ).configure(
        background='#DDC7A0' # Same dark cream background
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        fontSize=16,
        color='#4A3B32'
    ).configure_legend(
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    )
    
    st.altair_chart(chart_pie, use_container_width=True)
    st.divider()

    # Helper to build cumulative dataframe for a specific range and frequency
    def get_cumulative_data(data, start_date, end_date, freq="D"):
        # 1. Expand range (reindex needs strict boundaries)
        # Create full frequency index first
        full_index = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        # 2. Pivot
        # Group by Time(freq) and User
        # We need to ensure we capture all data in the range, effectively resampling
        
        # Filter first to minimize processing
        mask = (data["created_at"] >= start_date) & (data["created_at"] <= end_date)
        filtered_df = data.loc[mask]
        
        if filtered_df.empty:
            # Return empty df with correct index and columns
            empty_df = pd.DataFrame(0, index=full_index, columns=users)
            return empty_df.cumsum() # still all zeros

        # Pivot to [Time, User] = Count
        # We resample the Filtered DF to the target frequency
        # But pivot_table is easier to handle multi-users
        pivot = filtered_df.pivot_table(index="created_at", columns="user_name", values="value", aggfunc="sum", fill_value=0)
        
        # 3. Ensure all users exist
        for u in users:
            if u not in pivot.columns:
                pivot[u] = 0
                
        # 4. Resample & Reindex
        resampled = pivot.resample(freq).sum()
        resampled = resampled.reindex(full_index, fill_value=0)
        
        # 5. Cumulative Sum
        cumulative = resampled.cumsum()
        
        # 6. Mask future dates to stop the line at "today"
        # Since 'cumulative' usually holds ints, we astype(float) to allow NaNs
        cumulative = cumulative.astype(float)
        
        # Get cutoff (Now)
        # We need to match the timezone of the index
        current_time = pd.Timestamp.now(tz=cumulative.index.tz).normalize()
        
        # Mask future dates
        cumulative.loc[cumulative.index > current_time] = None
        
        return cumulative

    # Current Setup (Use server time or UTC to be safe, but local is fine for now)
    now = pd.Timestamp.now(tz=df_coffee["created_at"].dt.tz)
    
    # --- Weekly Configuration (Mon-Sun) ---
    today = now.floor("D") # Midnight
    start_week = (today - pd.to_timedelta(today.dayofweek, unit='D')).replace(hour=0, minute=0, second=0, microsecond=0)
    end_week = (start_week + pd.Timedelta(days=6)).replace(hour=23, minute=59, second=59)
    
    # --- Monthly Configuration (1-End) ---
    start_month = today.replace(day=1)
    next_month = (start_month + pd.DateOffset(months=1))
    end_month = (next_month - pd.Timedelta(seconds=1))
    
    # --- Yearly Configuration (Jan 1 - Dec 31) ---
    start_year = today.replace(month=1, day=1)
    end_year = today.replace(month=12, day=31).replace(hour=23, minute=59, second=59)

    # Calculate Dataframes (Coffee + Bea(tea))
    # Create a display dataframe that includes Bea's tea counts as "Bea(tea)"
    df_coffee_charts = df_coffee.copy()
    
    if not df_tea.empty:
        bea_tea = df_tea[df_tea["user_name"] == "Bea"].copy()
        if not bea_tea.empty:
            bea_tea["user_name"] = "Bea(tea)"
            df_coffee_charts = pd.concat([df_coffee_charts, bea_tea])

    df_week = get_cumulative_data(df_coffee_charts, start_week, end_week, "D")
    df_month = get_cumulative_data(df_coffee_charts, start_month, end_month, "D")
    df_year = get_cumulative_data(df_coffee_charts, start_year, end_year, "D")

    import altair as alt

    # Helper to plot with Altair (Custom Y-axis & Background)
    def plot_metric(data, title):
        # 1. Melt to long format for Altair
        # Reset index to make 'created_at' a column
        source = data.reset_index().melt('index', var_name='Coffee friend', value_name='Coffees')
        
        # 2. Calculate dynamic Y max for spacing
        y_max = source['Coffees'].max()
        # Add 10% padding or at least 1 unit
        y_domain_max = y_max * 1.1 if y_max > 0 else 5
        
        # 3. Create Chart
        chart = alt.Chart(source).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X('index', title='Date', axis=alt.Axis(format='%b %d')),
            y=alt.Y('Coffees', scale=alt.Scale(domain=[0, y_domain_max])),
            color=alt.Color('Coffee friend', scale=alt.Scale(domain=domain, range=range_)),
            tooltip=['index', 'Coffee friend', 'Coffees']
        ).properties(
            title=title,
            height=300
        ).configure(
            background='#DDC7A0' # Darker beige/coffee cream as requested
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14,
            gridColor='#000000',   # Black grid lines as requested
            domainColor='#4A3B32', # Dark axis line
            tickColor='#4A3B32',   # Dark ticks
            labelColor='#4A3B32',  # Dark labels
            titleColor='#4A3B32'   # Dark axis title
        ).configure_legend(
            labelColor='#4A3B32',
            titleColor='#4A3B32'
        ).configure_title(
            fontSize=16,
            color='#4A3B32'
        )
        
        st.altair_chart(chart, use_container_width=True)

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

    # Use the separated df_tea
    if not df_tea.empty:
        # Tea Pie Chart
        st.subheader("Tea Share 🍵")
        tea_pie_df = pd.DataFrame(list(tea_scores.items()), columns=['Tea friend', 'Teas'])
        tea_pie_df['Percentage'] = tea_pie_df['Teas'] / tea_pie_df['Teas'].sum()

        base_tea = alt.Chart(tea_pie_df).encode(
            theta=alt.Theta("Teas", stack=True)
        )
        pie_tea = base_tea.mark_arc(outerRadius=100).encode(
            color=alt.Color("Tea friend", scale=alt.Scale(domain=domain, range=range_)),
            order=alt.Order("Teas", sort="descending"),
            tooltip=["Tea friend", "Teas", alt.Tooltip("Percentage", format=".1%")]
        )
        text_tea = base_tea.mark_text(radius=120).encode(
            text=alt.Text("Percentage", format=".1%"),
            order=alt.Order("Teas", sort="descending"),
            color=alt.value("#4A3B32")
        )
        chart_pie_tea = (pie_tea + text_tea).properties(title="", height=350)
        # Note: Configure is global for the chart object, we can reuse the specific style if we want, 
        # but Altair configs are chart-specific.
        
        # Apply same style manually or via same config chain since we're displaying separately
        chart_pie_tea = chart_pie_tea.configure(
            background='#DDC7A0'
        ).configure_view(
            strokeWidth=0
        ).configure_title(
            fontSize=16, color='#4A3B32'
        ).configure_legend(
            labelColor='#4A3B32', titleColor='#4A3B32'
        )
        
        st.altair_chart(chart_pie_tea, use_container_width=True)
        st.divider()

        # Calculate Dataframes for Tea
        tea_week = get_cumulative_data(df_tea, start_week, end_week, "D")
        tea_month = get_cumulative_data(df_tea, start_month, end_month, "D")
        tea_year = get_cumulative_data(df_tea, start_year, end_year, "D")

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
