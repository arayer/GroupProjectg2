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
# PAGE 4 — MANAGE RESTAURANTS (DELETE)
# ============================================
elif page == "Manage Restaurants":
    st.header("🗑️ Manage Restaurants")
    st.markdown("---")

    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        # Create tabs for different management functions
        tab1, tab2, tab3 = st.tabs(["Delete Restaurant", "Delete by Criteria", "View All Restaurants"])
        
        with tab1:
            st.subheader("Delete a Restaurant")
            st.warning("⚠️ **Warning:** Deleting a restaurant is permanent and cannot be undone!")
            
            try:
                # Fetch all restaurants
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
                    # Create a dropdown with restaurant names
                    restaurant_options = {f"{row['name']} (ID: {row['restaurant_id']})": row['restaurant_id'] 
                                        for _, row in df.iterrows()}
                    
                    selected_restaurant = st.selectbox(
                        "Select a restaurant to delete:",
                        options=list(restaurant_options.keys())
                    )
                    
                    if selected_restaurant:
                        restaurant_id = restaurant_options[selected_restaurant]
                        
                        # Display restaurant details
                        restaurant_info = df[df['restaurant_id'] == restaurant_id].iloc[0]
                        
                        st.markdown("### Restaurant Details")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {restaurant_info['name']}")
                            st.write(f"**Price Range:** {restaurant_info['price_symbol']}")
                        with col2:
                            st.write(f"**Cuisines:** {restaurant_info['cuisines']}")
                            st.write(f"**Description:** {restaurant_info['description']}")
                        
                        st.markdown("---")
                        
                        # Confirmation checkbox
                        confirm = st.checkbox("I understand this action cannot be undone")
                        
                        # Delete button
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("🗑️ Delete Restaurant", disabled=not confirm, key="delete_btn"):
                                try:
                                    cursor = connection.cursor()
                                    
                                    # Delete related records first (due to foreign key constraints)
                                    cursor.execute("DELETE FROM RestaurantCuisines WHERE restaurant_id = %s", (restaurant_id,))
                                    cursor.execute("DELETE FROM RestaurantPricing WHERE restaurant_id = %s", (restaurant_id,))
                                    
                                    # Delete the restaurant
                                    cursor.execute("DELETE FROM Restaurants WHERE restaurant_id = %s", (restaurant_id,))
                                    
                                    connection.commit()
                                    cursor.close()
                                    
                                    st.success(f"✅ Restaurant '{restaurant_info['name']}' has been deleted successfully!")
                                    st.balloons()
                                    
                                    # Add a button to refresh the page
                                    if st.button("🔄 Refresh Page"):
                                        st.rerun()
                                        
                                except Error as e:
                                    connection.rollback()
                                    st.error(f"❌ Failed to delete restaurant: {e}")
                        
                        with col2:
                            if st.button("Cancel"):
                                st.info("Delete operation cancelled")
                                
            except Exception as e:
                st.error(f"❌ Error loading restaurants: {e}")
        
        with tab2:
            st.subheader("Delete Restaurants by Criteria")
            st.warning("⚠️ **Warning:** This will delete ALL restaurants matching your criteria!")
            
            try:
                # Fetch all restaurants for filtering
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
                    st.markdown("### Select Deletion Criteria")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Price range filter
                        price_options = ["None"] + sorted(df["price_symbol"].dropna().unique().tolist())
                        selected_price = st.selectbox(
                            "Delete by Price Range:",
                            options=price_options
                        )
                    
                    with col2:
                        # Cuisine filter
                        all_cuisines = sorted(df["cuisines"].dropna().str.split(",").explode().unique())
                        selected_cuisine = st.selectbox(
                            "Delete by Cuisine Type:",
                            options=["None"] + all_cuisines
                        )
                    
                    # Filter preview
                    preview_df = df.copy()
                    
                    if selected_price != "None":
                        preview_df = preview_df[preview_df["price_symbol"] == selected_price]
                    
                    if selected_cuisine != "None":
                        preview_df = preview_df[
                            preview_df["cuisines"].apply(
                                lambda x: selected_cuisine in x.split(",") if pd.notna(x) else False
                            )
                        ]
                    
                    # Show matching restaurants
                    if selected_price != "None" or selected_cuisine != "None":
                        st.markdown("---")
                        st.markdown("### Restaurants That Will Be Deleted")
                        
                        if preview_df.empty:
                            st.info("No restaurants match the selected criteria.")
                        else:
                            st.error(f"⚠️ {len(preview_df)} restaurant(s) will be permanently deleted:")
                            st.dataframe(
                                preview_df[["restaurant_id", "name", "price_symbol", "cuisines"]],
                                use_container_width=True
                            )
                            
                            st.markdown("---")
                            
                            # Confirmation
                            confirm_text = st.text_input(
                                f"Type 'DELETE {len(preview_df)}' to confirm:",
                                key="bulk_delete_confirm"
                            )
                            
                            expected_text = f"DELETE {len(preview_df)}"
                            
                            col1, col2, col3 = st.columns([1, 1, 2])
                            with col1:
                                if st.button("🗑️ Delete All Matching", disabled=(confirm_text != expected_text), key="bulk_delete_btn"):
                                    try:
                                        cursor = connection.cursor()
                                        deleted_count = 0
                                        
                                        for _, row in preview_df.iterrows():
                                            restaurant_id = row['restaurant_id']
                                            
                                            # Delete related records first
                                            cursor.execute("DELETE FROM RestaurantCuisines WHERE restaurant_id = %s", (restaurant_id,))
                                            cursor.execute("DELETE FROM RestaurantPricing WHERE restaurant_id = %s", (restaurant_id,))
                                            
                                            # Delete the restaurant
                                            cursor.execute("DELETE FROM Restaurants WHERE restaurant_id = %s", (restaurant_id,))
                                            deleted_count += 1
                                        
                                        connection.commit()
                                        cursor.close()
                                        
                                        st.success(f"✅ Successfully deleted {deleted_count} restaurant(s)!")
                                        st.balloons()
                                        
                                        if st.button("🔄 Refresh Page", key="bulk_refresh"):
                                            st.rerun()
                                            
                                    except Error as e:
                                        connection.rollback()
                                        st.error(f"❌ Failed to delete restaurants: {e}")
                            
                            with col2:
                                if st.button("Cancel", key="bulk_cancel"):
                                    st.info("Bulk delete operation cancelled")
                    else:
                        st.info("👆 Select at least one criterion above to preview which restaurants will be deleted.")
                        
            except Exception as e:
                st.error(f"❌ Error loading restaurants: {e}")
        
        with tab3:
            st.subheader("All Restaurants")
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
                    st.success(f"Total Restaurants: {len(df)}")
                    st.dataframe(
                        df[["restaurant_id", "name", "price_symbol", "cuisines", "description"]],
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ Error loading restaurants: {e}")


# ============================================
# CLOSE CONNECTION
# ============================================
if connection and connection.is_connected():
    connection.close()
