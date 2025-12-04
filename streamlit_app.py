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

# ----------------------------------------------------------
# Block 4: Sidebar Navigation
# ----------------------------------------------------------
st.sidebar.title("🍽️ Dallas Restaurants")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Homepage", "Restaurant Table", "Restaurant Map"]
)

st.sidebar.markdown("---")
st.sidebar.info("Group02 • ITOM6265 • Dallas Restaurants Dashboard")

# ============================================
#  PAGE 1 — HOMEPAGE
# ============================================
if page == "Homepage":
    st.markdown("""
        <h1 style="text-align:center; margin-bottom:0;">
            🍽️ Dallas Restaurants Dashboard
        </h1>
        <p style="text-align:center; font-size:18px; margin-top:0;">
            Explore, analyze, and visualize restaurant data across Dallas.
        </p>
    """, unsafe_allow_html=True)

    st.write("---")

    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.subheader("Welcome!")
        st.write("""
            This application connects to the **group02 MySQL restaurant database**  
            and allows you to:

            - 📍 View restaurants on an interactive map  
            - 🗂️ Browse and filter restaurant data  
            - ➕ Add new restaurant entries  
            - 📊 Create insights and summaries  

            Use the sidebar to navigate.
        """)

    with col2:
        st.image(
            "https://images.unsplash.com/photo-1555992336-cbfdbc69af72",
            caption="Dallas Restaurant Explorer",
            use_column_width=True
        )

    st.write("---")
    st.subheader("Features")
    feat1, feat2, feat3 = st.columns(3)
    with feat1: st.markdown("### 🗺️ Interactive Map")
    with feat2: st.markdown("### 📋 Restaurant Table")
    with feat3: st.markdown("### ➕ Add New Data")

    st.write("---")
    st.markdown(
        "<p style='text-align:center; color:#555555;'>Built by Group02 • Powered by Streamlit & MySQL</p>",
        unsafe_allow_html=True
    )

# ============================================
#  PAGE 2 — RESTAURANT TABLE
# ============================================
elif page == "Restaurant Table":
    st.header("📋 Restaurant Table")
    st.markdown("---")

    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        try:
            query = "SELECT * FROM Restaurants;"
            df = pd.read_sql(query, connection)
            st.success(f"Loaded {len(df)} restaurants")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

# ============================================
#  PAGE 3 — RESTAURANT MAP
# ============================================
elif page == "Restaurant Map":
    st.header("🗺️ Restaurant Map")
    st.markdown("---")

    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        try:
            query = """
                SELECT name, latitude, longitude
                FROM Restaurants
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
            """
            df = pd.read_sql(query, connection)
            if df.empty:
                st.warning("No restaurant coordinates found.")
            else:
                m = folium.Map(
                    location=[df.latitude.mean(), df.longitude.mean()],
                    zoom_start=11,
                    tiles="CartoDB Positron"
                )
                for _, row in df.iterrows():
                    folium.Marker(
                        [row["latitude"], row["longitude"]],
                        popup=row["name"],
                        tooltip=row["name"],
                        icon=folium.Icon(color="orange", icon="info-sign")
                    ).add_to(m)
                st_folium(m, height=600, width=None)
                st.success(f"Mapped {len(df)} restaurants successfully!")
        except Exception as e:
            st.error(f"Map query failed: {e}")

# ============================================
# CLOSE CONNECTION
# ============================================
if connection and connection.is_connected():
    connection.close()
