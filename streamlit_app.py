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
    
    .delete-button>button {
        background-color: #f44336;
        color: white;
    }
    .delete-button>button:hover {
        background-color: #d32f2f;
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
    ["Home", "Restaurant Search", "Find Food Near Me!", "Manage Restaurants"]
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
            - 🗑️ Manage and delete restaurant records

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
    feat1, feat2, feat3, feat4 = st.columns(4)
    with feat1: st.markdown("### 🗺️ Interactive Map")
    with feat2: st.markdown("### 📋 Restaurant Table")
    with feat3: st.markdown("### ➕ Add New Data")
    with feat4: st.markdown("### 🗑️ Manage Records")
    st.write("---")
    st.markdown(
        "<p style='text-align:center; color:#bbbbbb;'>Built by Group02 • Powered by Streamlit & MySQL</p>",
        unsafe_allow_html=True
    )


# ============================================
# PAGE 2 — RESTAURANT SEARCH (dropdown for price)
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
            col1, col2 = st.columns([2, 2])

            with col1:
                # Text input for restaurant name
                name_input = st.text_input(
                    "Restaurant Name:",
                    value=st.session_state.filter_name,
                    placeholder="Enter part of a name"
                )

            with col2:
                # Dropdown for price
                price_options = ["All", "$", "$$", "$$$"]
                selected_price = st.selectbox(
                    "Price Range:",
                    options=price_options,
                    index=price_options.index(st.session_state.filter_price)
                )

                # Multi-select for cuisines
                all_cuisines = sorted(df["cuisines"].dropna().str.split(",").explode().unique())
                selected_cuisines = st.multiselect(
                    "Cuisine Type(s):",
                    options=all_cuisines,
                    default=st.session_state.filter_cuisines
                )

            # Store filters in session state
            st.session_state.filter_name = name_input
            st.session_state.filter_price = selected_price
            st.session_state.filter_cuisines = selected_cuisines

            # --- Search button ---
            search_button = st.button("🔍 Get Results")

            # --- Apply filters when search button is pressed ---
            if search_button:
                filtered_df = df.copy()

                # Filter by name
                if name_input:
                    filtered_df = filtered_df[filtered_df["name"].str.contains(name_input, case=False, na=False)]

                # Filter by price
                if selected_price != "All":
                    filtered_df = filtered_df[filtered_df["price_symbol"] == selected_price]

                # Filter by cuisines (match any selected)
                if selected_cuisines:
                    filtered_df = filtered_df[
                        filtered_df["cuisines"].apply(
                            lambda x: any(c in x.split(",") for c in selected_cuisines) if pd.notna(x) else False
                        )
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
#  PAGE 3 — RESTAURANT MAP
# ============================================
elif page == "Find Food Near Me!":
    
    st.header("🗺️ Find Food Near Me")
    st.markdown("---")

    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        try:
            # Fetch restaurant names, coordinates, and price symbol
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
                import folium
                from streamlit_folium import st_folium

                # Create a Folium map centered on average coordinates
                m = folium.Map(
                    location=[df.latitude.mean(), df.longitude.mean()],
                    zoom_start=12,
                    tiles="CartoDB Positron"  # light map for visibility
                )

                # Define marker colors by price range
                price_color_map = {
                    "$": "lightblue",
                    "$$": "blue",
                    "$$$": "darkblue",
                    "$$$$": "purple"
                }

                # Add markers
                for _, row in df.iterrows():
                    color = price_color_map.get(row["price_symbol"], "blue")
                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=f"{row['name']} ({row['price_symbol']})",
                        tooltip=row["name"],
                        icon=folium.Icon(color=color, icon="info-sign")
                    ).add_to(m)

                # Display map in Streamlit
                st_folium(m, height=600, width=None)
                st.success(f"Mapped {len(df)} restaurants successfully!")

                # Add text explanation for marker colors
                st.markdown("""
                    **Marker Color Key (Price Ranges):**  
                    - Light Blue: $ (Budget-friendly)  
                    - Blue: $$ (Moderate)  
                    - Dark Blue: $$$ (Upscale)   
                """)
                
        except Exception as e:
            st.error(f"Map query failed: {e}")


# ============================================
# PAGE 4 — MANAGE RESTAURANTS (DELETE BY CUISINE)
# ============================================
elif page == "Manage Restaurants":
    st.header("🗑️ Manage Restaurants")
    st.markdown("---")

    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        # Create tabs for different management functions
        tab1, tab2 = st.tabs(["Delete by Cuisine Type", "View All Restaurants"])
        
        with tab1:
            st.subheader("Delete Restaurants by Cuisine")
            st.info("ℹ️ Select a cuisine type to see which restaurants would be affected. Changes are NOT permanent until you click 'Confirm Delete'.")
            
            try:
                # Fetch all restaurants with cuisine info
                query = """
                    SELECT r.restaurant_id, r.name, r.description, pr.price_symbol,
                           GROUP_CONCAT(ct.cuisine_name) AS cuisines
                    FROM Restaurants r
                    LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                    LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                    LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                    LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                    GROUP BY r.restaurant_id, r.name, r.description, pr.price_symbol
                    ORDER BY r.name
                """
                df = pd.read_sql(query, connection)
                
                if df.empty:
                    st.info("No restaurants found in the database.")
                else:
                    # Get unique cuisines
                    all_cuisines = sorted(df["cuisines"].dropna().str.split(",").explode().str.strip().unique())
                    
                    # Cuisine selector
                    selected_cuisine = st.selectbox(
                        "Select Cuisine Type to Delete:",
                        options=["-- Select a Cuisine --"] + all_cuisines,
                        key="cuisine_selector"
                    )
                    
                    if selected_cuisine != "-- Select a Cuisine --":
                        # Filter restaurants with selected cuisine
                        matching_restaurants = df[
                            df["cuisines"].apply(
                                lambda x: selected_cuisine in [c.strip() for c in x.split(",")] if pd.notna(x) else False
                            )
                        ]
                        
                        if matching_restaurants.empty:
                            st.warning(f"No restaurants found with cuisine type: {selected_cuisine}")
                        else:
                            st.markdown("---")
                            st.markdown(f"### Preview: Restaurants with '{selected_cuisine}' Cuisine")
                            st.warning(f"⚠️ {len(matching_restaurants)} restaurant(s) will be deleted if you confirm:")
                            
                            # Display matching restaurants
                            st.dataframe(
                                matching_restaurants[["restaurant_id", "name", "price_symbol", "cuisines", "description"]],
                                use_container_width=True
                            )
                            
                            st.markdown("---")
                            
                            # Two-step confirmation process
                            col1, col2, col3 = st.columns([2, 2, 2])
                            
                            with col1:
                                # First confirmation checkbox
                                confirm_preview = st.checkbox(
                                    f"I want to delete all {len(matching_restaurants)} {selected_cuisine} restaurants",
                                    key="confirm_checkbox"
                                )
                            
                            with col2:
                                # Second confirmation with text input
                                if confirm_preview:
                                    confirm_text = st.text_input(
                                        "Type 'CONFIRM' to proceed:",
                                        key="confirm_text_input"
                                    )
                                else:
                                    confirm_text = ""
                            
                            # Delete button row
                            st.markdown("---")
                            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])
                            
                            with btn_col1:
                                delete_enabled = confirm_preview and (confirm_text.upper() == "CONFIRM")
                                
                                if st.button(
                                    "🗑️ Confirm Delete", 
                                    disabled=not delete_enabled,
                                    type="primary",
                                    key="delete_confirm_btn"
                                ):
                                    try:
                                        cursor = connection.cursor()
                                        deleted_count = 0
                                        deleted_names = []
                                        
                                        # Delete each matching restaurant
                                        for _, row in matching_restaurants.iterrows():
                                            restaurant_id = row['restaurant_id']
                                            restaurant_name = row['name']
                                            
                                            # Delete related records first (foreign key constraints)
                                            cursor.execute("DELETE FROM RestaurantCuisines WHERE restaurant_id = %s", (restaurant_id,))
                                            cursor.execute("DELETE FROM RestaurantPricing WHERE restaurant_id = %s", (restaurant_id,))
                                            
                                            # Delete the restaurant
                                            cursor.execute("DELETE FROM Restaurants WHERE restaurant_id = %s", (restaurant_id,))
                                            
                                            deleted_count += 1
                                            deleted_names.append(restaurant_name)
                                        
                                        connection.commit()
                                        cursor.close()
                                        
                                        st.success(f"✅ Successfully deleted {deleted_count} {selected_cuisine} restaurant(s)!")
                                        
                                        with st.expander("View deleted restaurants"):
                                            for name in deleted_names:
                                                st.write(f"• {name}")
                                        
                                        st.balloons()
                                        
                                        # Refresh button
                                        if st.button("🔄 Refresh Page", key="refresh_after_delete"):
                                            st.rerun()
                                            
                                    except Error as e:
                                        connection.rollback()
                                        st.error(f"❌ Failed to delete restaurants: {e}")
                            
                            with btn_col2:
                                if st.button("↩️ Cancel", key="cancel_btn"):
                                    st.info("Delete operation cancelled. No changes were made.")
                                    st.rerun()
                        
            except Exception as e:
                st.error(f"❌ Error loading restaurants: {e}")
        
        with tab2:
            st.subheader("All Restaurants in Database")
            try:
                query = """
                    SELECT r.restaurant_id, r.name, r.description, r.website, pr.price_symbol,
                           GROUP_CONCAT(ct.cuisine_name) AS cuisines
                    FROM Restaurants r
                    LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                    LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                    LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                    LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                    GROUP BY r.restaurant_id, r.name, r.description, r.website, pr.price_symbol
                    ORDER BY r.name
                """
                df = pd.read_sql(query, connection)
                
                if df.empty:
                    st.info("No restaurants found in the database.")
                else:
                    st.success(f"📊 Total Restaurants: {len(df)}")
                    
                    # Show cuisine breakdown
                    cuisine_counts = df["cuisines"].dropna().str.split(",").explode().str.strip().value_counts()
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.dataframe(
                            df[["restaurant_id", "name", "price_symbol", "cuisines", "description"]],
                            use_container_width=True,
                            height=400
                        )
                    
                    with col2:
                        st.markdown("### Cuisine Breakdown")
                        for cuisine, count in cuisine_counts.items():
                            st.write(f"**{cuisine}:** {count} restaurant(s)")
                    
            except Exception as e:
                st.error(f"❌ Error loading restaurants: {e}")


# ============================================
# CLOSE CONNECTION
# ============================================
if connection and connection.is_connected():
    connection.close()
