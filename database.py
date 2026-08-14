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
        all_data = []
        limit = 1000
        offset = 0
        while True:
            response = supabase.table("clicks").select("*").range(offset, offset + limit - 1).execute()
            data = response.data
            if not data:
                break
            all_data.extend(data)
            if len(data) < limit:
                break
            offset += limit
        return all_data
    except Exception:
        return []

def insert_click(user: str, value: int, drink_id: int, country: str = None, city: str = None):
    supabase = get_supabase_client()
    event_data = {
        "user_name": user,
        "value": value,
        "drink_id": drink_id
    }
    if country:
        event_data["country"] = country
    if city:
        event_data["city"] = city
        
    try:
        return supabase.table("clicks").insert(event_data).execute()
    except Exception:
        # Graceful fallback if country/city columns have not yet been added to Supabase clicks table
        fallback_data = {
            "user_name": user,
            "value": value,
            "drink_id": drink_id
        }
        return supabase.table("clicks").insert(fallback_data).execute()

def get_transactions():
    supabase = get_supabase_client()
    try:
        all_data = []
        limit = 1000
        offset = 0
        while True:
            response = supabase.table("coin_transactions").select("*").range(offset, offset + limit - 1).execute()
            data = response.data
            if not data:
                break
            all_data.extend(data)
            if len(data) < limit:
                break
            offset += limit
        return all_data
    except Exception:
        return []

def insert_transaction(user: str, amount: int, transaction_type: str, metadata: dict = None):
    if metadata is None:
        metadata = {}
    supabase = get_supabase_client()
    event_data = {
        "user_name": user,
        "amount": amount,
        "transaction_type": transaction_type,
        "metadata": metadata
    }
    return supabase.table("coin_transactions").insert(event_data).execute()

