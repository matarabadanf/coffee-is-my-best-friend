import streamlit as st
import random

def inject_custom_css():
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

def render_header_and_quotes():
    st.title("Coffee is my best friend :coffee:")
    st.write("Yes. This is actually happening.")
    st.write("Once Cris said:")
    st.markdown('### "Dios no creo que oiga una frikada mayor de lo que acabo de oir."')
    st.markdown('However, **this is the newest "frikada"**.')
    
    st.divider()
    st.header("Coffee Quote:")
    coffee_sentences = [
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
