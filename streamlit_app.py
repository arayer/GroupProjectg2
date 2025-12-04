import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

import streamlit as st

# ----------------------------------------------------------
# Homepage Layout
# ----------------------------------------------------------

st.set_page_config(
    page_title="Dallas Restaurants App",
    page_icon="🍽️",
    layout="wide"
)

# ===== Header =====
st.markdown("""
    <h1 style="text-align:center; margin-bottom:0;">
        🍽️ Dallas Restaurants Dashboard
    </h1>
    <p style="text-align:center; font-size:18px; margin-top:0;">
        Explore, analyze, and visualize restaurant data across Dallas.
    </p>
""", unsafe_allow_html=True)

st.write("---")

# ===== Intro Section with Columns =====
col1, col2 = st.columns([1.3, 1])

with col1:
    st.subheader("Welcome!")
    st.write("""
        This application allows you to explore restaurant locations,  
        view insights, and interact with geographic and tabular data  
        stored in your **group02 MySQL database**.

        **What you can do here:**
        - 📍 View restaurants on an interactive map  
        - 🗂️ Browse and filter restaurant data  
        - ➕ Add or edit restaurant entries  
        - 📊 Create visual insights (charts & summaries)  
        
        Use the sidebar to navigate through the app’s pages.
    """)

with col2:
    st.image(
        "https://images.unsplash.com/photo-1555992336-cbfdbc69af72",
        caption="Dallas Restaurant Explorer",
        use_column_width=True
    )

st.write("---")

# ===== Feature Cards Section =====
st.subheader("Features")

feat1, feat2, feat3 = st.columns(3)

with feat1:
    st.markdown("""
    ### 🗺️ Interactive Map  
    View all restaurants across Dallas using a dynamic, zoomable Folium map.
    """)

with feat2:
    st.markdown("""
    ### 📋 Restaurant Table  
    Load, filter, and sort restaurant details from your MySQL database.
    """)

with feat3:
    st.markdown("""
    ### ➕ Add New Data  
    Easily add new restaurant entries with a clean, user-friendly form.
    """)

st.write("---")

# ===== Footer =====
st.markdown("""
    <p style="text-align:center; color:gray; margin-top:30px;">
        Built by Group 02 • Powered by Streamlit & MySQL
    </p>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# Connect to MySQL (group02 database)
# ----------------------------------------------------------

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="db-mysql-itom-do-user-28250611-0.j.db.ondigitalocean.com",        # e.g. "localhost" or server IP
            user="group02",
            password="Pass2025_group02",
            database="group02"
        )
        if connection.is_connected():
            st.success("Connected to group02 database!")
            return connection

    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None


# ----------------------------------------------------------
# Example query function
# ----------------------------------------------------------

def load_restaurants():
    connection = create_connection()
    if connection:
        query = "SELECT * FROM Restaurants;"
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    return None


# ----------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------

st.title("Group02 Database Connection Test")

if st.button("Load Restaurant Data"):
    df = load_restaurants()
    if df is not None:
        st.dataframe(df)
    else:
        st.error("No data found or failed to load data.")
