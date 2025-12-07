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

# Block 2: Page configuration (MUST BE FIRST)
st.set_page_config(
    page_title="Dallas Restaurants App",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for fonts and minor tweaks
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    body { font-family: 'Montserrat', sans-serif; }
    h1, h2, h3, h4 { color: #2196f3; }
    .stButton>button {
        background-color: #2196f3; color: white; border-radius: 10px;
        border: none; padding: 0.5rem 1rem; font-weight: bold;
    }
    .stButton>button:hover { background-color: #1976d2; color: white; }
    .stDataFrame tbody tr:hover { background-color: #1e88e5 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# Database connection
try:
    connection = mysql.connector.connect(
        host="db-mysql-itom-do-user-28250611-0.j.db.ondigitalocean.com",
        port=25060, user="group02", password="Pass2025_group02", database="group02"
    )
    db_connected = True
    st.sidebar.success("✅ Connected to group02 database")
except Error as e:
    st.sidebar.error(f"❌ DB Connection Failed: {e}")
    db_connected = False
    connection = None

# Helper function to check if is_active column exists
def ensure_is_active_column():
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'group02' AND TABLE_NAME = 'Restaurants' AND COLUMN_NAME = 'is_active'
        """)
        exists = cursor.fetchone()[0]
        if not exists:
            cursor.execute("ALTER TABLE Restaurants ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            connection.commit()
            st.sidebar.info("✅ Added is_active column to database")
        cursor.close()
        return True
    except Error as e:
        st.sidebar.warning(f"Note: is_active column setup - {e}")
        return False

# Sidebar Navigation
st.sidebar.title("🍽️ Dallas Restaurants")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Home", "Restaurant Search", "Find Food Near Me!", "Manage Restaurants", "Manage Reviews"])
st.sidebar.markdown("---")
st.sidebar.info("Group02 • ITOM6265 • Dallas Restaurants Dashboard")

# ============================================
# PAGE 1 — HOMEPAGE
# ============================================
if page == "Home":
    st.markdown("""
        <h1 style="text-align:center; margin-bottom:0;">🍽️ Dallas Restaurants Dashboard</h1>
        <p style="text-align:center; font-size:18px; margin-top:0; color:#ffffff;">
            Explore, analyze, and visualize restaurant data across Dallas.
        </p>
    """, unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.subheader("Welcome!")
        st.write("""
            This application connects to the **group02 MySQL restaurant database** and allows you to:
            - 📍 View restaurants on an interactive map  
            - 🗂️ Browse and filter restaurant data  
            - ➕ Add new restaurant entries  
            - 🗃️ Archive/restore restaurant records (soft delete)
            - ⭐ Manage restaurant reviews
            
            Use the sidebar to navigate.
        """)
    with col2:
        st.image("drelogo.png", caption="Dallas Restaurant Explorer", use_container_width=True)
    st.write("---")
    st.subheader("Features")
    feat1, feat2, feat3, feat4, feat5 = st.columns(5)
    with feat1: st.markdown("### 🗺️ Map")
    with feat2: st.markdown("### 📋 Search")
    with feat3: st.markdown("### ➕ Add")
    with feat4: st.markdown("### 🗃️ Archive")
    with feat5: st.markdown("### ⭐ Reviews")
    st.write("---")
    st.markdown("<p style='text-align:center; color:#bbbbbb;'>Built by Group02 • Powered by Streamlit & MySQL</p>", unsafe_allow_html=True)

# ============================================
# PAGE 2 — RESTAURANT SEARCH
# ============================================
elif page == "Restaurant Search":
    st.header("📋 Restaurant Search")
    st.markdown("---")
    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        try:
            ensure_is_active_column()
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

            if "filter_price" not in st.session_state: st.session_state.filter_price = "All"
            if "filter_name" not in st.session_state: st.session_state.filter_name = ""
            if "filter_cuisines" not in st.session_state: st.session_state.filter_cuisines = []

            st.markdown("### Filter Options")
            col1, col2 = st.columns([2, 2])
            with col1:
                name_input = st.text_input("Restaurant Name:", value=st.session_state.filter_name, placeholder="Enter part of a name")
            with col2:
                price_options = ["All", "$", "$$", "$$$"]
                selected_price = st.selectbox("Price Range:", options=price_options, index=price_options.index(st.session_state.filter_price))
                all_cuisines = sorted(df["cuisines"].dropna().str.split(",").explode().unique())
                selected_cuisines = st.multiselect("Cuisine Type(s):", options=all_cuisines, default=st.session_state.filter_cuisines)

            st.session_state.filter_name = name_input
            st.session_state.filter_price = selected_price
            st.session_state.filter_cuisines = selected_cuisines

            if st.button("🔍 Get Results"):
                filtered_df = df.copy()
                if name_input:
                    filtered_df = filtered_df[filtered_df["name"].str.contains(name_input, case=False, na=False)]
                if selected_price != "All":
                    filtered_df = filtered_df[filtered_df["price_symbol"] == selected_price]
                if selected_cuisines:
                    filtered_df = filtered_df[filtered_df["cuisines"].apply(
                        lambda x: any(c in x.split(",") for c in selected_cuisines) if pd.notna(x) else False)]
                if not filtered_df.empty:
                    st.success(f"✅ Found {len(filtered_df)} restaurant(s) matching your criteria")
                    st.dataframe(filtered_df[["name", "description", "website"]], use_container_width=True)
                else:
                    st.warning("⚠️ No restaurants found. Try adjusting your filters.")
        except Exception as e:
            st.error(f"❌ Query failed: {e}")

# ============================================
# PAGE 3 — RESTAURANT MAP
# ============================================
elif page == "Find Food Near Me!":
    st.header("🗺️ Find Food Near Me")
    st.markdown("---")
    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        try:
            ensure_is_active_column()
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
                m = folium.Map(location=[df.latitude.mean(), df.longitude.mean()], zoom_start=12, tiles="CartoDB Positron")
                price_color_map = {"$": "lightblue", "$$": "blue", "$$$": "darkblue", "$$$$": "purple"}
                for _, row in df.iterrows():
                    color = price_color_map.get(row["price_symbol"], "blue")
                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=f"{row['name']} ({row['price_symbol']})",
                        tooltip=row["name"],
                        icon=folium.Icon(color=color, icon="info-sign")
                    ).add_to(m)
                st_folium(m, height=600, width=None)
                st.success(f"Mapped {len(df)} active restaurants successfully!")
                st.markdown("""**Marker Color Key (Price Ranges):**  
                    - Light Blue: $ (Budget-friendly)  
                    - Blue: $$ (Moderate)  
                    - Dark Blue: $$$ (Upscale)""")
        except Exception as e:
            st.error(f"Map query failed: {e}")

# ============================================
# PAGE 4 — MANAGE RESTAURANTS
# ============================================
elif page == "Manage Restaurants":
    st.header("🗃️ Manage Restaurants")
    st.markdown("---")
    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        ensure_is_active_column()
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Archive Restaurants", "Restore Archived", "View All Status", 
            "➕ Add New Restaurant", "🔄 Update Existing Restaurant"
        ])
        
        # TAB 1: Archive Restaurants
        with tab1:
            st.subheader("📦 Archive Restaurants")
            st.info("ℹ️ Archiving removes restaurants from active listings but preserves all data.")
            try:
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
                    if "selected_to_archive" not in st.session_state:
                        st.session_state.selected_to_archive = []
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("✅ Select All Visible"):
                            st.session_state.selected_to_archive = df["restaurant_id"].tolist()
                            st.rerun()
                    with col2:
                        if st.button("❌ Deselect All"):
                            st.session_state.selected_to_archive = []
                            st.rerun()
                    for idx, row in df.iterrows():
                        col1, col2, col3, col4 = st.columns([0.5, 2, 1.5, 2])
                        with col1:
                            is_selected = st.checkbox("", value=row["restaurant_id"] in st.session_state.selected_to_archive,
                                                     key=f"archive_cb_{row['restaurant_id']}")
                            if is_selected and row["restaurant_id"] not in st.session_state.selected_to_archive:
                                st.session_state.selected_to_archive.append(row["restaurant_id"])
                            elif not is_selected and row["restaurant_id"] in st.session_state.selected_to_archive:
                                st.session_state.selected_to_archive.remove(row["restaurant_id"])
                        with col2: st.write(f"**{row['name']}**")
                        with col3: st.write(f"{row['price_symbol']} • {row['cuisines']}")
                        with col4:
                            desc = row['description'][:50] + "..." if len(str(row['description'])) > 50 else row['description']
                            st.write(f"_{desc}_")
                    if len(st.session_state.selected_to_archive) > 0:
                        st.warning(f"⚠️ {len(st.session_state.selected_to_archive)} restaurant(s) selected for archiving")
                        col1, col2, _ = st.columns([1, 1, 3])
                        with col1:
                            if st.button("📦 Archive Selected", type="primary"):
                                try:
                                    cursor = connection.cursor()
                                    for rid in st.session_state.selected_to_archive:
                                        cursor.execute("UPDATE Restaurants SET is_active = FALSE WHERE restaurant_id = %s", (rid,))
                                    connection.commit()
                                    cursor.close()
                                    st.success(f"✅ Successfully archived {len(st.session_state.selected_to_archive)} restaurant(s)!")
                                    st.session_state.selected_to_archive = []
                                    st.balloons()
                                except Error as e:
                                    connection.rollback()
                                    st.error(f"❌ Failed to archive: {e}")
                        with col2:
                            if st.button("Cancel"):
                                st.session_state.selected_to_archive = []
                                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # TAB 2: Restore
        with tab2:
            st.subheader("♻️ Restore Archived Restaurants")
            try:
                query = """
                    SELECT r.restaurant_id, r.name, r.description, pr.price_symbol,
                           GROUP_CONCAT(ct.cuisine_name) AS cuisines
                    FROM Restaurants r
                    LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                    LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                    LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                    LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                    WHERE r.is_active = FALSE
                    GROUP BY r.restaurant_id
                    ORDER BY r.name
                """
                df = pd.read_sql(query, connection)
                if df.empty:
                    st.info("No archived restaurants to restore.")
                else:
                    st.success(f"📊 {len(df)} archived restaurants")
                    if "selected_to_restore" not in st.session_state:
                        st.session_state.selected_to_restore = []
                    for idx, row in df.iterrows():
                        col1, col2 = st.columns([0.5, 4])
                        with col1:
                            sel = st.checkbox("", value=row["restaurant_id"] in st.session_state.selected_to_restore,
                                            key=f"restore_cb_{row['restaurant_id']}")
                            if sel and row["restaurant_id"] not in st.session_state.selected_to_restore:
                                st.session_state.selected_to_restore.append(row["restaurant_id"])
                            elif not sel and row["restaurant_id"] in st.session_state.selected_to_restore:
                                st.session_state.selected_to_restore.remove(row["restaurant_id"])
                        with col2: st.write(f"**{row['name']}** - {row['price_symbol']}")
                    if len(st.session_state.selected_to_restore) > 0:
                        if st.button("♻️ Restore Selected", type="primary"):
                            try:
                                cursor = connection.cursor()
                                for rid in st.session_state.selected_to_restore:
                                    cursor.execute("UPDATE Restaurants SET is_active = TRUE WHERE restaurant_id = %s", (rid,))
                                connection.commit()
                                cursor.close()
                                st.success(f"✅ Restored {len(st.session_state.selected_to_restore)} restaurant(s)!")
                                st.session_state.selected_to_restore = []
                                st.balloons()
                            except Error as e:
                                connection.rollback()
                                st.error(f"❌ Failed: {e}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # TAB 3: View All Status
        with tab3:
            st.subheader("📊 All Restaurants - Status Overview")
            try:
                query = """
                    SELECT r.restaurant_id, r.name, r.is_active, pr.price_symbol,
                           GROUP_CONCAT(ct.cuisine_name) AS cuisines
                    FROM Restaurants r
                    LEFT JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
                    LEFT JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
                    LEFT JOIN RestaurantCuisines rc ON r.restaurant_id = rc.restaurant_id
                    LEFT JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
                    GROUP BY r.restaurant_id
                    ORDER BY r.is_active DESC, r.name
                """
                df = pd.read_sql(query, connection)
                if not df.empty:
                    df["status"] = df["is_active"].apply(lambda x: "✅ Active" if x else "📦 Archived")
                    col1, col2, col3 = st.columns(3)
                    with col1: st.metric("Total", len(df))
                    with col2: st.metric("Active", len(df[df["is_active"] == True]))
                    with col3: st.metric("Archived", len(df[df["is_active"] == False]))
                    st.dataframe(df[["restaurant_id", "name", "status", "price_symbol", "cuisines"]], 
                               use_container_width=True, height=500)
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # TAB 4: Add Restaurant
        with tab4:
            st.subheader("➕ Add New Restaurant")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Restaurant Name *", placeholder="e.g., Joe's Pizza")
                street = st.text_input("Street Address *")
                zip_code = st.text_input("ZIP Code *")
            with col2:
                city = st.text_input("City", value="Dallas")
                state = st.text_input("State", value="TX", max_chars=2)
                phone = st.text_input("Phone")
            description = st.text_area("Description")
            website = st.text_input("Website")
            lat = st.number_input("Latitude", value=32.7767, format="%.6f")
            lng = st.number_input("Longitude", value=-96.7970, format="%.6f")
            price = st.selectbox("Price Range", ["$", "$$", "$$$", "$$$$"])
            
            if st.button("💾 Save Restaurant", type="primary"):
                if not name or not street or not zip_code:
                    st.error("❌ Required fields missing!")
                else:
                    try:
                        cursor = connection.cursor()
                        cursor.execute("""
                            INSERT INTO Restaurants (name, street_address, city, state, zip_code, phone, 
                                                   website, description, latitude, longitude, is_active)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                        """, (name, street, city, state, zip_code, phone, website, description, lat, lng))
                        connection.commit()
                        cursor.close()
                        st.success(f"✅ Added {name}!")
                        st.balloons()
                    except Error as e:
                        connection.rollback()
                        st.error(f"❌ Error: {e}")
        
        # TAB 5: Update Restaurant
        with tab5:
            st.subheader("🔄 Update Existing Restaurant")
            st.info("Select a restaurant to edit its details")

# ============================================
# PAGE 5 — MANAGE REVIEWS (NEW SEPARATE PAGE)
# ============================================
elif page == "Manage Reviews":
    st.header("⭐ Manage Reviews")
    st.markdown("---")
    
    if not db_connected:
        st.error("Database connection unavailable.")
    else:
        review_tab1, review_tab2, review_tab3 = st.tabs(["📋 View Reviews", "➕ Add Review", "🗑️ Delete Review"])
        
        # TAB 1: View Reviews
        with review_tab1:
            st.subheader("📋 All Reviews")
            try:
                # First, let's check what columns exist in the Reviews table
                cursor = connection.cursor()
                cursor.execute("DESCRIBE Reviews")
                columns_info = cursor.fetchall()
                cursor.close()
                
                # Display column names for debugging
                with st.expander("🔍 Debug: Reviews Table Structure"):
                    st.write("Available columns in Reviews table:")
                    for col in columns_info:
                        st.write(f"- {col[0]} ({col[1]})")
                
                query = """
                    SELECT rv.review_id, r.name AS restaurant_name, rv.rating, 
                           rv.review_text, rv.review_date
                    FROM Reviews rv
                    INNER JOIN Restaurants r ON rv.restaurant_id = r.restaurant_id
                    ORDER BY rv.review_date DESC
                """
                reviews_df = pd.read_sql(query, connection)
                if reviews_df.empty:
                    st.info("No reviews found in the database.")
                else:
                    st.success(f"📊 {len(reviews_df)} total reviews")
                    
                    # Add filter by restaurant
                    restaurant_filter = st.selectbox(
                        "Filter by Restaurant:",
                        ["All Restaurants"] + sorted(reviews_df["restaurant_name"].unique().tolist())
                    )
                    
                    # Apply filter
                    if restaurant_filter != "All Restaurants":
                        filtered_reviews = reviews_df[reviews_df["restaurant_name"] == restaurant_filter]
                    else:
                        filtered_reviews = reviews_df
                    
                    st.markdown("---")
                    
                    # Display reviews
                    for _, review in filtered_reviews.iterrows():
                        with st.container():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.markdown(f"**{review['restaurant_name']}**")
                            with col2:
                                stars = "⭐" * int(review['rating'])
                                st.markdown(f"{stars} ({review['rating']}/5)")
                            with col3:
                                st.markdown(f"📅 {review['review_date']}")
                            if pd.notna(review['review_text']):
                                st.markdown(f"> {review['review_text']}")
                            st.markdown("---")
                    
                    if restaurant_filter != "All Restaurants":
                        st.info(f"Showing {len(filtered_reviews)} reviews for {restaurant_filter}")
            except Exception as e:
                st.error(f"❌ Error loading reviews: {e}")
        
        # TAB 2: Add Review
        with review_tab2:
            st.subheader("➕ Add New Review")
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT restaurant_id, name FROM Restaurants WHERE is_active = TRUE ORDER BY name")
                restaurants = cursor.fetchall()
                cursor.close()
                
                if not restaurants:
                    st.warning("No active restaurants available to review.")
                else:
                    restaurant_options = {name: rid for rid, name in restaurants}
                    selected_restaurant = st.selectbox("Select Restaurant *", list(restaurant_options.keys()))
                    selected_restaurant_id = restaurant_options[selected_restaurant]
                    
                    rating = st.slider("Rating *", 1, 5, 5, help="Rate from 1 to 5 stars")
                    review_text = st.text_area("Review Text", placeholder="Share your experience...", height=150)
                    
                    st.markdown("---")
                    col1, col2, _ = st.columns([1, 1, 3])
                    with col1:
                        if st.button("💾 Submit Review", type="primary"):
                            try:
                                cursor = connection.cursor()
                                cursor.execute("""
                                    INSERT INTO Reviews (restaurant_id, rating, review_text, review_date)
                                    VALUES (%s, %s, %s, CURDATE())
                                """, (selected_restaurant_id, rating, review_text or None))
                                connection.commit()
                                cursor.close()
                                st.success(f"✅ Review submitted successfully for **{selected_restaurant}**!")
                                st.balloons()
                            except Error as e:
                                connection.rollback()
                                st.error(f"❌ Database error: {e}")
                    with col2:
                        if st.button("Clear Form"):
                            st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading form: {e}")
        
        # TAB 3: Delete Review
        with review_tab3:
            st.subheader("🗑️ Delete Reviews")
            st.warning("⚠️ This action cannot be undone!")
            try:
                query = """
                    SELECT rv.review_id, r.name AS restaurant_name, rv.rating, 
                           rv.review_text, rv.review_date
                    FROM Reviews rv
                    INNER JOIN Restaurants r ON rv.restaurant_id = r.restaurant_id
                    ORDER BY rv.review_date DESC
                """
                reviews_df = pd.read_sql(query, connection)
                
                if reviews_df.empty:
                    st.info("No reviews to delete.")
                else:
                    st.info(f"📊 {len(reviews_df)} reviews available")
                    
                    if "selected_reviews_to_delete" not in st.session_state:
                        st.session_state.selected_reviews_to_delete = []
                    
                    # Select All / Deselect All
                    col1, col2, _ = st.columns([1, 1, 3])
                    with col1:
                        if st.button("✅ Select All"):
                            st.session_state.selected_reviews_to_delete = reviews_df["review_id"].tolist()
                            st.rerun()
                    with col2:
                        if st.button("❌ Deselect All"):
                            st.session_state.selected_reviews_to_delete = []
                            st.rerun()
                    
                    st.markdown("---")
                    
                    # Display reviews with checkboxes
                    for _, review in reviews_df.iterrows():
                        col1, col2, col3, col4 = st.columns([0.5, 2, 1, 2])
                        with col1:
                            sel = st.checkbox("", value=review["review_id"] in st.session_state.selected_reviews_to_delete,
                                            key=f"delete_review_cb_{review['review_id']}")
                            if sel and review["review_id"] not in st.session_state.selected_reviews_to_delete:
                                st.session_state.selected_reviews_to_delete.append(review["review_id"])
                            elif not sel and review["review_id"] in st.session_state.selected_reviews_to_delete:
                                st.session_state.selected_reviews_to_delete.remove(review["review_id"])
                        with col2:
                            st.write(f"**{review['restaurant_name']}**")
                        with col3:
                            stars = "⭐" * int(review['rating'])
                            st.write(f"{stars}")
                            st.write(f"📅 {review['review_date']}")
                        with col4:
                            preview = review['review_text'][:50] + "..." if pd.notna(review['review_text']) and len(str(review['review_text'])) > 50 else review['review_text']
                            st.write(f"_{preview if pd.notna(preview) else 'No text'}_")
                    
                    # Delete button
                    st.markdown("---")
                    if len(st.session_state.selected_reviews_to_delete) > 0:
                        st.error(f"⚠️ {len(st.session_state.selected_reviews_to_delete)} review(s) selected for deletion")
                        col1, col2, _ = st.columns([1, 1, 3])
                        with col1:
                            if st.button("🗑️ Delete Selected", type="primary"):
                                try:
                                    cursor = connection.cursor()
                                    for rid in st.session_state.selected_reviews_to_delete:
                                        cursor.execute("DELETE FROM Reviews WHERE review_id = %s", (rid,))
                                    connection.commit()
                                    cursor.close()
                                    st.success(f"✅ Successfully deleted {len(st.session_state.selected_reviews_to_delete)} review(s)!")
                                    st.session_state.selected_reviews_to_delete = []
                                except Error as e:
                                    connection.rollback()
                                    st.error(f"❌ Failed to delete: {e}")
                        with col2:
                            if st.button("Cancel"):
                                st.session_state.selected_reviews_to_delete = []
                                st.rerun()
                    else:
                        st.info("👆 Select reviews above to delete them")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# Close connection
if connection and connection.is_connected():
    connection.close()
