import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# 1. Setup Page Configuration
st.set_page_config(page_title="Friend Counters", page_icon="🔢")

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
st.title("🔢 The Count")
st.write("A shared ledger of clicks.")

# User Selection (for flexibility, could also be hardcoded buttons)
# We use a selectbox so you can easily add more friends without changing code much
users = ["Friend A", "Friend B", "Me"] 
selected_user = st.selectbox("Who are you?", users)

# 4. Data Fetching
# We fetch ALL events to calculate the score locally. 
# For massive scale, you'd use a database view or RPC, but for this scale, this is perfect.
def get_data():
    response = supabase.table("clicks").select("*").execute()
    return response.data

data = get_data()

# 5. Calculate Scores
if data:
    df = pd.DataFrame(data)
    # Group by 'user_name' and count (or sum 'value' if you stored simple events)
    # Using sum of 'value' column as per requirement
    scores = df.groupby("user_name")["value"].sum().to_dict()
else:
    scores = {}

# 6. Display Scores & Actions
# Show metrics for all users
st.subheader("Current Scores")
cols = st.columns(len(users))

for idx, user in enumerate(users):
    score = scores.get(user, 0)
    with cols[idx]:
        st.metric(label=user, value=score)
        
        # The 'Count' Button
        # Only enable the button for the selected user to prevent accidents? 
        # Or just let anyone click. User asked for "their own buttons".
        # We'll make a big button for the CURRENTLY selected user below.

st.divider()

# Action Section
st.subheader(f"Update Score for {selected_user}")

col1, col2 = st.columns([1, 2])
with col1:
    if st.button(f"+1 for {selected_user}", type="primary", use_container_width=True):
        # Insert Event
        event_data = {
            "user_name": selected_user,
            "value": 1
            # created_at is auto-handled by Supabase default
        }
        
        try:
            supabase.table("clicks").insert(event_data).execute()
            st.success("Counted!")
            # Rerun to update the score immediately
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    # Optional: Recent History
    if data:
        st.caption("Recent Log")
        # Show last 5 events
        df_sorted = df.sort_values("created_at", ascending=False).head(5)
        st.dataframe(df_sorted[["created_at", "user_name", "value"]], hide_index=True)

