# ============================================
# Restaurant Dashboard - Group02 Streamlit App (Dark Theme)
# ============================================

# Block 1: Import required libraries
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import folium
from streamlit_folium import st_folium

# ----------------------------------------------------------
# Custom CSS for fonts and minor tweaks
# ----------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

    body {
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, h3, h4 {
        color: #2196f3;
    }

    .stButton>button {
        background-color: #2196f3;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1976d2;
        color: white;
    }

    .stDataFrame tbody tr:hover {
        background-color: #1e88e5 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Block 2: Page configuration
st.set_page_config(
    page_title="Dallas Restaurants App",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------
# Database connection
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
# Sidebar Navigation
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
# PAGE 1 — HOMEPAGE
# ============================================
if page == "Homepage":
    st.markdown("""
        <h1 style="text-align:center; margin-bottom:0;">
            🍽️ Dallas Restaurants Dashboard
        </h1>
        <p style="text-align:center; font-size:18px; margin-top:0; color:#ffffff;">
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
        "<p style='text-align:center; color:#bbbbbb;'>Built by Group02 • Powered by Streamlit & MySQL</p>",
        unsafe_allow_html=True
    )


# ============================================
# PAGE 2 — RESTAURANT TABLE (price filter buttons)
# ============================================
elif page == "Restaurant Table":
    st.header("📋 Restaurant Table")
    st.markdown("---")

    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        try:
            # Fetch only necessary columns with price symbol
            query = """
                SELECT r.restaurant_id, r.name, r.description, r.website, pr.price_symbol
                FROM Restaurants r
                LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id;
            """
            df = pd.read_sql(query, connection)

            st.success(f"Loaded {len(df)} restaurants")

            # Style the price filter buttons for uniform width and visibility
            st.markdown("""
                <style>
                /* Main container for the radio group, use flexbox */
                div[role="radiogroup"] {
                    display: flex;
                    justify-content: space-between; /* Distribute items evenly */
                    width: 100%; /* Take full width of the parent container */
                }

                /* Individual button labels */
                div[data-baseweb="radio"] > div > label {
                    display: flex;
                    justify-content: center; /* Center text within the button */
                    width: 100%; /* Ensure the label fills the flex item's width */
                    cursor: pointer;
                }

                /* The inner div containing the text and the hidden radio circle */
                div[data-baseweb="radio"] > div > label > div {
                    background-color: #001f3f !important;  /* Navy background */
                    color: white !important; /* White text */
                    border-radius: 8px;
                    padding: 0.4rem 0.8rem;
                    font-weight: bold;
                    text-align: center;
                    width: 100%; /* Make the visible part take the full width */
                }

                /* Hide the actual radio input circle to make it look like buttons */
                div[data-baseweb="radio"] input[type="radio"] {
                    display: none;
                }

                div[data-baseweb="radio"] > div > label > div:hover {
                    background-color: #001a35 !important;  /* Slightly darker navy on hover */
                }

                /* Style for the selected button */
                input[type="radio"]:checked + div {
                    background-color: #007bff !important;  /* Use a contrasting color for "selected" state, e.g., a bright blue */
                    color: white !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # Price filter buttons
            filter_price = st.radio(
                "Filter by Price",
                options=["All", "$", "$$", "$$$", "$$$$"],
                horizontal=True
            )

            # Apply filter
            if filter_price != "All":
                df = df[df["price_symbol"] == filter_price]

            # Show only desired columns
            st.dataframe(df[["name", "description", "website"]], use_container_width=True)

            if filter_price != "All":
                st.info(f"Showing {len(df)} restaurants with price {filter_price}")

        except Exception as e:
            st.error(f"Query failed: {e}")


# ============================================
# PAGE 3 — RESTAURANT MAP
# ============================================
elif page == "Restaurant Map":
    st.header("🗺️ Restaurant Map")
    st.markdown("---")
    
    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        try:
            # Join Restaurants with PriceRanges to get price symbol
            query = """
                SELECT r.name, r.latitude, r.longitude, pr.price_symbol
                FROM Restaurants r
                LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                WHERE r.latitude IS NOT NULL AND r.longitude IS NOT NULL;
            """
            df = pd.read_sql(query, connection)

            if df.empty:
                st.warning("No restaurant coordinates found")
            else:
                # Use lighter map tiles for better visibility
                m = folium.Map(
                    location=[df.latitude.mean(), df.longitude.mean()],
                    zoom_start=12,
                    tiles="CartoDB Positron"  # light map tiles
                )

                # Marker colors by price range
                price_color_map = {
                    "$": "lightblue",
                    "$$": "blue",
                    "$$$": "darkblue",
                    "$$$$": "purple"
                }

                for _, row in df.iterrows():
                    color = price_color_map.get(row["price_symbol"], "blue")
                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=f"{row['name']} ({row['price_symbol']})",
                        tooltip=row["name"],
                        icon=folium.Icon(color=color, icon="cutlery", prefix="fa")
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
