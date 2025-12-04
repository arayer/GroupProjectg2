# ============================================
# Restaurant Dashboard - Group02 Streamlit App (Styled)
# ============================================

# Block 1: Import required libraries
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import folium
from streamlit_folium import st_folium

# Block 2: Page configuration
st.set_page_config(
    page_title="Dallas Restaurants App",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------
# Custom CSS for colors and fonts
# ----------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Montserrat', sans-serif;
        background-color: #f0f8ff;  /* Light blue background */
        color: #333333;
    }

    /* Sidebar styling */
    .css-1d391kg {  /* sidebar container */
        background-color: #00796b;  /* Teal sidebar */
        color: white;
    }
    .css-1d391kg .stRadio label {
        color: white;
    }

    /* Main headers */
    h1, h2, h3, h4 {
        color: #ff7043;  /* Orange headers */
    }

    /* Buttons */
    .stButton>button {
        background-color: #ff7043;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff5722;
        color: white;
    }

    /* Tables */
    .dataframe tbody tr:hover {
        background-color: #b2dfdb;
    }

    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# Block 3: Database connection (UPDATED FOR group02)
# ----------------------------------------------------------
try:
    connection = mysql.connector.connect(
        host="db-mysql-itom-do-user-28250611-0.j.db.ondigitalocean.com",
        port=25060,
        user="group02",
        password="Pass2025_group02",
        database="group02"
    )
    db_connected = True
    st.sidebar.success("✅ Connected to group02 database")
except Error as e:
    st.sidebar.error(f"❌ DB Connection Failed: {e}")
    db_connected = False
    connection = None

# --------
