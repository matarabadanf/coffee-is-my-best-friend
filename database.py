import streamlit as st
from supabase import create_client, Client

# Initialize Supabase Client
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except FileNotFoundError:
        st.error("Secrets not found! Please create .streamlit/secrets.toml")
        st.stop()
    return create_client(url, key)

def get_data():
    supabase = get_supabase_client()
    try:
        response = supabase.table("clicks").select("*").execute()
        return response.data
    except Exception:
        return []

def insert_click(user: str, value: int, drink_id: int):
    supabase = get_supabase_client()
    event_data = {
        "user_name": user,
        "value": value,
        "drink_id": drink_id
    }
    return supabase.table("clicks").insert(event_data).execute()
