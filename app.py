import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os


CSV_PATH = r"C:\Users\halkhthran.t\Downloads\WA_Fn-UseC_-HR-Employee-Attrition.csv"
DB_PATH = "employees.db"

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


#-------------------------------Page 1 - EDA-----------------------------

def page_eda(df):
    st.title("🔎 Exploratory Data Analysis (EDA)")

   
    st.markdown("""
    ### 📊 Dataset Columns & Explanations

    - **Attrition** Whether the employee left the company (Yes/No).  
    - **BusinessTravel**  Frequency of business travel (Rarely, Frequently, Non-Travel).  
    - **DailyRate**  Daily salary rate.  
    - **Department**  Department (HR, R&D, Sales).  
    - **DistanceFromHome**  Distance between home and workplace (miles).  
    - **Education**  1=Below College, 2=College, 3=Bachelor, 4=Master, 5=Doctor.  
    - **EducationField**  Field of education (Life Sciences, Medical, Marketing…).  
    - **EmployeeCount**  Always “1”.  
    - **EmployeeNumber**  Unique ID.  
    - **EnvironmentSatisfaction**  1=Low, 4=Very High.  
    - **HourlyRate**  Hourly salary.  
    - **JobInvolvement**  1=Low, 4=Very High.  
    - **JobLevel**  1=Entry, higher=senior.  
    - **JobRole**  Job title (e.g., Sales Exec, Research Scientist, Manager).  
    - **JobSatisfaction**  1=Low, 4=Very High.  
    - **MaritalStatus**  Single, Married, Divorced.  
    - **MonthlyIncome**  Monthly salary.  
    - **NumCompaniesWorked**  Companies worked before.  
    - **OverTime**  Overtime (Yes/No).  
    - **PercentSalaryHike** % increase in salary.  
    - **PerformanceRating**  1=Low, 4=Outstanding.  
    - **RelationshipSatisfaction**  1=Low, 4=Very High.  
    - **TotalWorkingYears**  Total years of experience.  
    - **TrainingTimesLastYear**  Trainings last year.  
    - **WorkLifeBalance**  1=Bad, 4=Very Good.  
    - **YearsAtCompany**  Years at current company.  
    - **YearsInCurrentRole**  Years in current role.  
    - **YearsSinceLastPromotion**  Years since last promotion.  
    - **YearsWithCurrManager**  Years with current manager.  
    """)

    st.subheader("Preview of Dataset")
    st.dataframe(df.astype(str), use_container_width=True, height=400)

    st.subheader("Missing Values")
    missing = df.isnull().sum().reset_index()
    missing.columns = ["Column", "Missing"]
    st.dataframe(missing, use_container_width=True)

    st.subheader("Distribution of Numeric Features")
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns
    col = st.selectbox("Choose a column", num_cols)
    fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}",
                       color_discrete_sequence=["#4f008c"])
    st.plotly_chart(fig, use_container_width=True)

#---------------------------------- Main----------------------------------------
st.sidebar.image("top_banner.png", use_container_width=True)  
st.sidebar.title("IBM Hr Data Analysis")
page = st.sidebar.radio("Go to", ["EDA", "Insights", "Manage Employees"])
st.sidebar.image("bottom_banner.png", use_container_width =True) 


#Calling all the function 
df = load_data()

if page == "EDA":
    page_eda(df)