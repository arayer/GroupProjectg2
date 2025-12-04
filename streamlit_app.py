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
    ["Home", "Restaurant Search", "Find Food Near Me!"]
)
st.sidebar.markdown("---")
st.sidebar.info("Group02 • ITOM6265 • Dallas Restaurants Dashboard")

# ============================================
# PAGE 1 — HOMEPAGE
# ============================================
if page == "Home":
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
# PAGE 2 — RESTAURANT SEARCH (multi-cuisine filter)
# ============================================
elif page == "Restaurant Search":
    st.header("📋 Restaurant Search")
    st.markdown("---")

    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        try:
            # Fetch all restaurant data with price and cuisine info
            query = """
                SELECT r.restaurant_id, r.name, r.description, r.website, pr.price_symbol,
                       GROUP_CONCAT(ct.cuisine_name) AS cuisines
                FROM Restaurants r
                LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                GROUP BY r.restaurant_id, r.name, r.description, r.website, pr.price_symbol
            """
            df = pd.read_sql(query, connection)
            st.success(f"Loaded {len(df)} restaurants")

            # Initialize session state for filters
            if "filter_price" not in st.session_state:
                st.session_state.filter_price = "All"
            if "filter_name" not in st.session_state:
                st.session_state.filter_name = ""
            if "filter_cuisines" not in st.session_state:
                st.session_state.filter_cuisines = []

            # --- Filters layout ---
            st.markdown("### Filter Options")
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                # Text input for restaurant name
                name_input = st.text_input(
                    "Restaurant Name:",
                    value=st.session_state.filter_name,
                    placeholder="Enter part of a name"
                )

            with col2:
                # Price filter buttons
                if st.button("All"):
                    st.session_state.filter_price = "All"
                if st.button("$"):
                    st.session_state.filter_price = "$"
                if st.button("$$"):
                    st.session_state.filter_price = "$$"
                if st.button("$$$"):
                    st.session_state.filter_price = "$$$"

            with col3:
                # Multi-select for cuisines
                all_cuisines = sorted(df["cuisines"].dropna().str.split(",").explode().unique())
                selected_cuisines = st.multiselect(
                    "Cuisine Type(s):",
                    options=all_cuisines,
                    default=st.session_state.filter_cuisines
                )

            # Store filters in session state
            st.session_state.filter_name = name_input
            st.session_state.filter_cuisines = selected_cuisines
            filter_price = st.session_state.filter_price

            # --- Search button ---
            search_button = st.button("🔍 Get Results")

            # --- Apply filters when search button is pressed ---
            if search_button:
                filtered_df = df.copy()

                # Filter by name
                if name_input:
                    filtered_df = filtered_df[filtered_df["name"].str.contains(name_input, case=False, na=False)]

                # Filter by price
                if filter_price != "All":
                    filtered_df = filtered_df[filtered_df["price_symbol"] == filter_price]

                # Filter by cuisines (match any selected)
                if selected_cuisines:
                    filtered_df = filtered_df[
                        filtered_df["cuisines"].apply(lambda x: any(c in x.split(",") for c in selected_cuisines) if pd.notna(x) else False)
                    ]

                # Show results
                if not filtered_df.empty:
                    st.success(f"✅ Found {len(filtered_df)} restaurant(s) matching your criteria")
                    st.dataframe(
                        filtered_df[["name", "description", "website"]],
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ No restaurants found. Try adjusting your filters.")

        except Exception as e:
            st.error(f"❌ Query failed: {e}")


# ============================================
# PAGE 3 — RESTAURANT MAP
# ============================================
elif page == "Find Food Near Me!":
    st.header("🗺️ Find Food Near Me!")
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
