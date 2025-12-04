import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

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
