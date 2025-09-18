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

#--------------------------------Page 2 - Insights---------------------------

def page_insights(df):
    st.title("📈 Insights")

    # Choose data source
    mode = st.radio("Select Data Source", ["DataFrame (Python)", "Database (SQL)"], horizontal=True)

    # Filter by Department
    depts = sorted(df["Department"].dropna().unique().tolist())
    chosen = st.multiselect("Filter by Department", depts, default=depts)

    if mode == "DataFrame (Python)":
        # PANDAS MODE 
        df_f = df[df["Department"].isin(chosen)]

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Total Employees", f"{df_f['EmployeeCount'].sum():,}")
        with k2: st.metric("Attrition Rate", f"{df_f['Attrition'].eq('Yes').mean()*100:.1f}%")
        with k3: st.metric("Avg Perf. Rating", f"{df_f['PerformanceRating'].mean():.2f}")
        with k4: st.metric("Avg Monthly Income", f"${df_f['MonthlyIncome'].mean():,.0f}")

        st.markdown("---")

        # 1) Employees per Department
        st.subheader("Employees per Department")
        dept_cnt = df_f.groupby("Department")["EmployeeCount"].sum().reset_index()
        fig_dept = px.bar(dept_cnt.sort_values("EmployeeCount"),
                          x="EmployeeCount", y="Department", orientation="h",
                          text="EmployeeCount", color="EmployeeCount",
                          color_continuous_scale=["#4f008c", "#ff375e"],
                          template="plotly_white")
        st.plotly_chart(fig_dept, use_container_width=True)

        # 2) Average Monthly Income by Job Role
        st.subheader("Average Monthly Income by Job Role")
        inc_role = df_f.groupby("JobRole")["MonthlyIncome"].mean().reset_index().round(0)
        fig_inc = px.bar(inc_role.sort_values("MonthlyIncome"),
                         x="MonthlyIncome", y="JobRole", orientation="h",
                         text="MonthlyIncome", color="MonthlyIncome",
                         color_continuous_scale=["#4f008c", "#ff375e"],
                         template="plotly_white")
        st.plotly_chart(fig_inc, use_container_width=True)

        # 3) Average Performance by Department 
        st.subheader("Average Performance by Department")
        perf = df_f.groupby("Department")["PerformanceRating"].mean().reset_index(name="AvgRating")
        fig_perf = px.pie(perf, names="Department", values="AvgRating",
                          color_discrete_sequence=["#4f008c", "#ff375e", "#3f2156"],
                          hole=0.35)
        st.plotly_chart(fig_perf, use_container_width=True)

        # 4) Overtime vs Attrition by Department
        st.subheader("Attrition vs Overtime by Department")
        ot = (df_f.groupby(["Department", "OverTime"])
                  .agg(AttritionRate=("Attrition", lambda s: (s=="Yes").mean()))
                  .reset_index())
        fig_ot = px.bar(ot, x="OverTime", y="AttritionRate",
                        facet_col="Department", facet_col_wrap=3,
                        text=ot["AttritionRate"].mul(100).round(1).astype(str)+"%",
                        color="OverTime", color_discrete_sequence=["#4f008c", "#ff375e"],
                        template="plotly_white")
        fig_ot.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig_ot, use_container_width=True)
        


#---------------------------------- Main----------------------------------------
st.sidebar.image("top_banner.png", use_container_width=True)  
st.sidebar.title("IBM Hr Data Analysis")
page = st.sidebar.radio("Go to", ["EDA", "Insights", "Manage Employees"])
st.sidebar.image("bottom_banner.png", use_container_width =True) 


#Calling all the function 
df = load_data()

if page == "EDA":
    page_eda(df)
elif page == "Insights":
    page_insights(df)