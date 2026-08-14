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
    
    # 1. Preferred modern format: single JSON column "location" (e.g. {"country": "ES", "city": "Alcobendas"})
    if country or city:
        loc_json = {}
        if country: loc_json["country"] = country
        if city: loc_json["city"] = city
        
        # Try inserting with single JSON column 'location'
        try:
            event_data_json = {
                "user_name": user,
                "value": value,
                "drink_id": drink_id,
                "location": loc_json
            }
            return supabase.table("clicks").insert(event_data_json).execute()
        except Exception:
            pass
            
        # Try inserting with separate columns 'country' and 'city'
        try:
            event_data_cols = {
                "user_name": user,
                "value": value,
                "drink_id": drink_id,
                "country": country,
                "city": city
            }
            return supabase.table("clicks").insert(event_data_cols).execute()
        except Exception:
            pass

    # 3. Base fallback without location columns
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

def get_preferences():
    """Fetches all rows from the dedicated user_preferences table."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("user_preferences").select("*").execute()
        return response.data or []
    except Exception:
        return []

def save_user_preference(user_name: str, updates: dict):
    """Saves or updates user settings in user_preferences table with seamless fallback."""
    supabase = get_supabase_client()
    try:
        existing = supabase.table("user_preferences").select("*").eq("user_name", user_name).execute()
        if existing.data and len(existing.data) > 0:
            return supabase.table("user_preferences").update(updates).eq("user_name", user_name).execute()
        else:
            record = {"user_name": user_name, **updates}
            return supabase.table("user_preferences").insert(record).execute()
    except Exception:
        # Fallback to coin_transactions if user_preferences table is not created yet
        return insert_transaction(user_name, 0, "preference", updates)

