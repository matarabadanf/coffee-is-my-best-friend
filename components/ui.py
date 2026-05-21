import streamlit as st
import random

def inject_custom_css():
    st.markdown(
        """
        <style>
        /* Tea Button Style */
        .stButton > button:first-child {
             border-radius: 20px;
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

        /* Fix Fullscreen Chart Contrast */
        [data-testid="stFullScreenFrame"],
        div[data-testid="stFullScreenFrame"] > div {
            background-color: #F9F3E3 !important;
        }
        
        /* Force Selectbox Labels and Text to be Black */
        .stSelectbox label p,
        .stSelectbox div[data-baseweb="select"] span {
            color: #000000 !important;
        }
        
        /* Make Sidebar Selectbox Labels White */
        [data-testid="stSidebar"] .stSelectbox label p {
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

import randfacts

def render_header_and_quotes():
    st.title("Coffee is my best friend :coffee:")
    fact = randfacts.get_fact()
    st.caption(f"🧠 *Did you know? {fact}*")
    st.divider()
