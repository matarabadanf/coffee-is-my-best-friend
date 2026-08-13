import hashlib
import streamlit as st
import time

def enforce_user_identity(users: list) -> str:
    """
    Checks if a user is defined in the URL or session state.
    If not, renders a landing page to choose the identity and stops execution.
    Returns the identified user.
    """
    query_user = st.query_params.get("user")
    if query_user in users:
        st.session_state.global_user = query_user
        return query_user
        
    if "global_user" in st.session_state and st.session_state.global_user in users:
        st.query_params["user"] = st.session_state.global_user
        st.rerun()
        
    # Render Landing Page with Clean Typography
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    div[data-testid="stButton"] > button {
        background-color: #4A3B32 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #33251D !important;
        transform: translateY(-2px);
    }
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>☕ Welcome!</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: var(--text-muted, #666);'>Please select who you are to continue:</h3>", unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    cols = st.columns(len(users))
    for i, u in enumerate(users):
        with cols[i]:
            if st.button(f"👤 I am {u}", width="stretch", key=f"login_{u}"):
                st.session_state.global_user = u
                st.query_params["user"] = u
                st.rerun()
                
    st.stop()

import time

def is_pin_verified(user_name: str) -> bool:
    """Check if the user has recently verified their PIN (e.g., within the last 5 minutes)."""
    cache_key = f"pin_verified_time_{user_name}"
    if cache_key in st.session_state:
        last_verified = st.session_state[cache_key]
        if time.time() - last_verified < 300: # 5 minutes
            return True
    return False

def verify_pin(user_name: str, pin_input: str) -> bool:
    """
    Hashes the provided pin_input and checks if it matches the stored hash
    for user_name in st.secrets["pins"].
    """
    if is_pin_verified(user_name):
        # Refresh the timer so it stays unlocked while they keep playing
        st.session_state[f"pin_verified_time_{user_name}"] = time.time()
        return True

    if not pin_input:
        st.error("Please enter a PIN.")
        return False
        
    try:
        stored_hash = st.secrets["pins"].get(user_name)
    except Exception:
        st.error("PIN secrets not configured properly. Check .streamlit/secrets.toml")
        return False

    if not stored_hash:
        st.error(f"No PIN configured for user {user_name}")
        return False

    input_hash = hashlib.sha256(pin_input.encode()).hexdigest()
    
    if input_hash == stored_hash:
        st.session_state[f"pin_verified_time_{user_name}"] = time.time()
        return True
    else:
        st.error("Incorrect PIN! Please try again.")
        return False

