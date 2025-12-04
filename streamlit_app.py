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
    
    .restore-button>button {
        background-color: #4caf50;
        color: white;
    }
    .restore-button>button:hover {
        background-color: #388e3c;
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
# Helper function to check if is_active column exists
# ----------------------------------------------------------
def ensure_is_active_column():
    """Add is_active column if it doesn't exist"""
    try:
        cursor = connection.cursor()
        # Check if column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'group02' 
            AND TABLE_NAME = 'Restaurants' 
            AND COLUMN_NAME = 'is_active'
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            # Add the column with default value TRUE
            cursor.execute("""
                ALTER TABLE Restaurants 
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """)
            connection.commit()
            st.sidebar.info("✅ Added is_active column to database")
        
        cursor.close()
        return True
    except Error as e:
        st.sidebar.warning(f"Note: is_active column setup - {e}")
        return False

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
            - 🗃️ Archive/restore restaurant records (soft delete)

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
    with feat4: st.markdown("### 🗃️ Archive Manager")
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
            # Ensure is_active column exists
            ensure_is_active_column()
            
            # Fetch all ACTIVE restaurant data with price and cuisine info
            query = """
                SELECT r.restaurant_id, r.name, r.description, r.website, pr.price_symbol,
                       GROUP_CONCAT(ct.cuisine_name) AS cuisines
                FROM Restaurants r
                LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                WHERE r.is_active = TRUE
                GROUP BY r.restaurant_id, r.name, r.description, r.website, pr.price_symbol
            """
            df = pd.read_sql(query, connection)
            st.success(f"Loaded {len(df)} active restaurants")

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
            # Ensure is_active column exists
            ensure_is_active_column()
            
            # Fetch ACTIVE restaurant names, coordinates, and price symbol
            query = """
                SELECT r.name, r.latitude, r.longitude, pr.price_symbol
                FROM Restaurants r
                LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                WHERE r.latitude IS NOT NULL AND r.longitude IS NOT NULL AND r.is_active = TRUE;
            """
            df = pd.read_sql(query, connection)

            if df.empty:
                st.warning("No active restaurant coordinates found")
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
                st.success(f"Mapped {len(df)} active restaurants successfully!")

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
# PAGE 4 — MANAGE RESTAURANTS (SOFT DELETE)
# ============================================
elif page == "Manage Restaurants":
    st.header("🗃️ Manage Restaurants")
    st.markdown("---")

    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        # Ensure is_active column exists
        ensure_is_active_column()
        
        # Create tabs for different management functions
        tab1, tab2, tab3 = st.tabs(["Archive Restaurants", "Restore Archived", "View All Status"])
        
        # ============================================
        # TAB 1: ARCHIVE (SOFT DELETE)
        # ============================================
        with tab1:
            st.subheader("📦 Archive Restaurants")
            st.info("ℹ️ Archiving removes restaurants from active listings but preserves all data. You can restore them anytime!")
            
            try:
                # Fetch all ACTIVE restaurants
                query = """
                    SELECT r.restaurant_id, r.name, r.description, pr.price_symbol,
                           GROUP_CONCAT(ct.cuisine_name) AS cuisines
                    FROM Restaurants r
                    LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                    LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                    LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                    LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                    WHERE r.is_active = TRUE
                    GROUP BY r.restaurant_id, r.name, r.description, pr.price_symbol
                    ORDER BY r.name
                """
                df = pd.read_sql(query, connection)
                
                if df.empty:
                    st.info("No active restaurants to archive.")
                else:
                    st.success(f"📊 {len(df)} active restaurants available")
                    
                    # Add filter options
                    st.markdown("### Filter Options (optional)")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        filter_cuisine = st.selectbox(
                            "Filter by Cuisine:",
                            ["All Cuisines"] + sorted(df["cuisines"].dropna().str.split(",").explode().str.strip().unique())
                        )
                    
                    with col2:
                        filter_price = st.selectbox(
                            "Filter by Price:",
                            ["All Prices"] + sorted(df["price_symbol"].dropna().unique().tolist())
                        )
                    
                    # Apply filters
                    filtered_df = df.copy()
                    if filter_cuisine != "All Cuisines":
                        filtered_df = filtered_df[
                            filtered_df["cuisines"].apply(
                                lambda x: filter_cuisine in [c.strip() for c in x.split(",")] if pd.notna(x) else False
                            )
                        ]
                    if filter_price != "All Prices":
                        filtered_df = filtered_df[filtered_df["price_symbol"] == filter_price]
                    
                    st.markdown("---")
                    st.markdown(f"### Select Restaurants to Archive ({len(filtered_df)} shown)")
                    
                    # Initialize session state for selections
                    if "selected_to_archive" not in st.session_state:
                        st.session_state.selected_to_archive = []
                    
                    # Select All / Deselect All buttons
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("✅ Select All Visible"):
                            st.session_state.selected_to_archive = filtered_df["restaurant_id"].tolist()
                            st.rerun()
                    with col2:
                        if st.button("❌ Deselect All"):
                            st.session_state.selected_to_archive = []
                            st.rerun()
                    
                    # Display restaurants with checkboxes
                    st.markdown("---")
                    for idx, row in filtered_df.iterrows():
                        col1, col2, col3, col4 = st.columns([0.5, 2, 1.5, 2])
                        
                        with col1:
                            is_selected = st.checkbox(
                                "",
                                value=row["restaurant_id"] in st.session_state.selected_to_archive,
                                key=f"archive_cb_{row['restaurant_id']}"
                            )
                            if is_selected and row["restaurant_id"] not in st.session_state.selected_to_archive:
                                st.session_state.selected_to_archive.append(row["restaurant_id"])
                            elif not is_selected and row["restaurant_id"] in st.session_state.selected_to_archive:
                                st.session_state.selected_to_archive.remove(row["restaurant_id"])
                        
                        with col2:
                            st.write(f"**{row['name']}**")
                        with col3:
                            st.write(f"{row['price_symbol']} • {row['cuisines']}")
                        with col4:
                            st.write(f"_{row['description'][:50]}..._" if len(str(row['description'])) > 50 else f"_{row['description']}_")
                    
                    # Archive button
                    st.markdown("---")
                    if len(st.session_state.selected_to_archive) > 0:
                        st.warning(f"⚠️ {len(st.session_state.selected_to_archive)} restaurant(s) selected for archiving")
                        
                        col1, col2, col3 = st.columns([1, 1, 3])
                        with col1:
                            if st.button("📦 Archive Selected", type="primary", key="archive_btn"):
                                try:
                                    cursor = connection.cursor()
                                    archived_count = 0
                                    
                                    for restaurant_id in st.session_state.selected_to_archive:
                                        cursor.execute(
                                            "UPDATE Restaurants SET is_active = FALSE WHERE restaurant_id = %s",
                                            (restaurant_id,)
                                        )
                                        archived_count += 1
                                    
                                    connection.commit()
                                    cursor.close()
                                    
                                    st.success(f"✅ Successfully archived {archived_count} restaurant(s)!")
                                    st.session_state.selected_to_archive = []
                                    st.balloons()
                                    
                                    if st.button("🔄 Refresh", key="refresh_archive"):
                                        st.rerun()
                                        
                                except Error as e:
                                    connection.rollback()
                                    st.error(f"❌ Failed to archive: {e}")
                        
                        with col2:
                            if st.button("Cancel"):
                                st.session_state.selected_to_archive = []
                                st.rerun()
                    else:
                        st.info("👆 Select restaurants above to archive them")
                        
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # ============================================
        # TAB 2: RESTORE
        # ============================================
        with tab2:
            st.subheader("♻️ Restore Archived Restaurants")
            st.info("ℹ️ Restore archived restaurants to make them active again in searches and on the map.")
            
            try:
                # Fetch all INACTIVE restaurants
                query = """
                    SELECT r.restaurant_id, r.name, r.description, pr.price_symbol,
                           GROUP_CONCAT(ct.cuisine_name) AS cuisines
                    FROM Restaurants r
                    LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                    LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                    LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                    LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                    WHERE r.is_active = FALSE
                    GROUP BY r.restaurant_id, r.name, r.description, pr.price_symbol
                    ORDER BY r.name
                """
                df = pd.read_sql(query, connection)
                
                if df.empty:
                    st.info("No archived restaurants to restore.")
                else:
                    st.success(f"📊 {len(df)} archived restaurants available")
                    
                    # Initialize session state for restore selections
                    if "selected_to_restore" not in st.session_state:
                        st.session_state.selected_to_restore = []
                    
                    # Select All / Deselect All buttons
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("✅ Select All", key="restore_select_all"):
                            st.session_state.selected_to_restore = df["restaurant_id"].tolist()
                            st.rerun()
                    with col2:
                        if st.button("❌ Deselect All", key="restore_deselect_all"):
                            st.session_state.selected_to_restore = []
                            st.rerun()
                    
                    # Display archived restaurants with checkboxes
                    st.markdown("---")
                    for idx, row in df.iterrows():
                        col1, col2, col3, col4 = st.columns([0.5, 2, 1.5, 2])
                        
                        with col1:
                            is_selected = st.checkbox(
                                "",
                                value=row["restaurant_id"] in st.session_state.selected_to_restore,
                                key=f"restore_cb_{row['restaurant_id']}"
                            )
                            if is_selected and row["restaurant_id"] not in st.session_state.selected_to_restore:
                                st.session_state.selected_to_restore.append(row["restaurant_id"])
                            elif not is_selected and row["restaurant_id"] in st.session_state.selected_to_restore:
                                st.session_state.selected_to_restore.remove(row["restaurant_id"])
                        
                        with col2:
                            st.write(f"**{row['name']}**")
                        with col3:
                            st.write(f"{row['price_symbol']} • {row['cuisines']}")
                        with col4:
                            st.write(f"_{row['description'][:50]}..._" if len(str(row['description'])) > 50 else f"_{row['description']}_")
                    
                    # Restore button
                    st.markdown("---")
                    if len(st.session_state.selected_to_restore) > 0:
                        st.success(f"✅ {len(st.session_state.selected_to_restore)} restaurant(s) selected for restoration")
                        
                        col1, col2, col3 = st.columns([1, 1, 3])
                        with col1:
                            if st.button("♻️ Restore Selected", type="primary", key="restore_btn"):
                                try:
                                    cursor = connection.cursor()
                                    restored_count = 0
                                    
                                    for restaurant_id in st.session_state.selected_to_restore:
                                        cursor.execute(
                                            "UPDATE Restaurants SET is_active = TRUE WHERE restaurant_id = %s",
                                            (restaurant_id,)
                                        )
                                        restored_count += 1
                                    
                                    connection.commit()
                                    cursor.close()
                                    
                                    st.success(f"✅ Successfully restored {restored_count} restaurant(s)!")
                                    st.session_state.selected_to_restore = []
                                    st.balloons()
                                    
                                    if st.button("🔄 Refresh", key="refresh_restore"):
                                        st.rerun()
                                        
                                except Error as e:
                                    connection.rollback()
                                    st.error(f"❌ Failed to restore: {e}")
                        
                        with col2:
                            if st.button("Cancel", key="restore_cancel"):
                                st.session_state.selected_to_restore = []
                                st.rerun()
                    else:
                        st.info("👆 Select restaurants above to restore them")
                        
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # ============================================
        # TAB 3: VIEW ALL
        # ============================================
        with tab3:
            st.subheader("📊 All Restaurants - Status Overview")
            
            try:
                # Fetch ALL restaurants (active and inactive)
                query = """
                    SELECT r.restaurant_id, r.name, r.description, r.is_active, pr.price_symbol,
                           GROUP_CONCAT(ct.cuisine_name) AS cuisines
                    FROM Restaurants r
                    LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                    LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                    LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                    LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                    GROUP BY r.restaurant_id, r.name, r.description, r.is_active, pr.price_symbol
                    ORDER BY r.is_active DESC, r.name
                """
                df = pd.read_sql(query, connection)
                
                if df.empty:
                    st.info("No restaurants found in database.")
                else:
                    active_count = len(df[df["is_active"] == True])
                    archived_count = len(df[df["is_active"] == False])
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Restaurants", len(df))
                    with col2:
                        st.metric("Active", active_count, delta=None)
                    with col3:
                        st.metric("Archived", archived_count, delta=None)
                    
                    st.markdown("---")
                    
                    # Add status indicator to dataframe for display
                    df["status"] = df["is_active"].apply(lambda x: "✅ Active" if x else "📦 Archived")
                    
                    # Display full table
                    st.dataframe(
                        df[["restaurant_id", "name", "status", "price_symbol", "cuisines", "description"]],
                        use_container_width=True,
                        height=500
                    )
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")


# ============================================
# CLOSE CONNECTION
# ============================================
if connection and connection.is_connected():
    connection.close()
