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

def clear_all_db_caches():
    """Explicitly clears all in-memory database query caches."""
    try:
        get_data.clear()
    except Exception:
        pass
    try:
        get_transactions.clear()
    except Exception:
        pass
    try:
        get_preferences.clear()
    except Exception:
        pass

@st.cache_data(ttl=60, show_spinner=False)
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
    result = None
    
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
            result = supabase.table("clicks").insert(event_data_json).execute()
        except Exception:
            pass
            
        # Try inserting with separate columns 'country' and 'city'
        if result is None:
            try:
                event_data_cols = {
                    "user_name": user,
                    "value": value,
                    "drink_id": drink_id,
                    "country": country,
                    "city": city
                }
                result = supabase.table("clicks").insert(event_data_cols).execute()
            except Exception:
                pass

    # 3. Base fallback without location columns
    if result is None:
        fallback_data = {
            "user_name": user,
            "value": value,
            "drink_id": drink_id
        }
        result = supabase.table("clicks").insert(fallback_data).execute()

    # Clear cached query data so fresh clicks appear immediately
    try:
        get_data.clear()
    except Exception:
        pass

    return result

@st.cache_data(ttl=60, show_spinner=False)
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
    result = supabase.table("coin_transactions").insert(event_data).execute()
    try:
        get_transactions.clear()
    except Exception:
        pass
    return result

@st.cache_data(ttl=60, show_spinner=False)
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
        known_columns = {"theme", "emoji", "title", "ui_style", "default_country", "default_city", "share_live_location"}
        col_updates = {}
        meta_updates = {}
        for k, v in updates.items():
            if k in known_columns:
                col_updates[k] = v
            else:
                meta_updates[k] = v

        if existing.data and len(existing.data) > 0:
            row = existing.data[0]
            cur_meta = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
            if meta_updates:
                cur_meta.update(meta_updates)
                col_updates["metadata"] = cur_meta
            res = supabase.table("user_preferences").update(col_updates).eq("user_name", user_name).execute()
        else:
            record = {"user_name": user_name, **col_updates}
            if meta_updates:
                record["metadata"] = meta_updates
            res = supabase.table("user_preferences").insert(record).execute()

        try:
            get_preferences.clear()
            get_transactions.clear()
        except Exception:
            pass
        return res
    except Exception:
        # Fallback to coin_transactions if user_preferences table is not created yet
        res = insert_transaction(user_name, 0, "preference", updates)
        try:
            get_preferences.clear()
            get_transactions.clear()
        except Exception:
            pass
        return res

