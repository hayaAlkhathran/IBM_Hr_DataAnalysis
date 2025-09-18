import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os


CSV_PATH = r"C:\Users\halkhthran.t\Downloads\WA_Fn-UseC_-HR-Employee-Attrition.csv"
DB_PATH = r"c:\Users\halkhthran.t\Downloads\HrAnalysisProject\employees.db"

# If the SQLite database file does not exist, create it from the CSV file
if not os.path.exists(DB_PATH):
    st.warning("employees.db not found. Creating from CSV")
    HrData = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    HrData.to_sql("employees", conn, if_exists="replace", index=False)
    conn.close()

    st.success("✅ employees.db created from CSV.")

#------------------------------- Load Data -----------------------------

@st.cache_data
def load_data():
    """
    Loads the employee data from the SQLite database into a DataFrame.
    load_data function : Input (nune) , Output (df-DataFrame)
    Why do we need this function when we can read_csv direct ?
       Because if we update or add new employees, we can see the changes in 
       the SQLite database and DataFrame . There is another solution when adding new employees;
       add to SQLite databases and DataFrame , but I prefer this way it less code.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df


#Calling all the function 
df = load_data()