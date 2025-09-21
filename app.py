import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os


CSV_PATH = "Data/WA_Fn-UseC_-HR-Employee-Attrition.csv"
DB_PATH = "Data/employees.db"

import os

print("CSV exists:", os.path.exists(CSV_PATH))
print("DB exists:", os.path.exists(DB_PATH))

# If the SQLite database file does not exist, create it from the CSV file
if not os.path.exists(DB_PATH):
    st.warning("employees.db not found. Creating from CSV")
    HrData = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    HrData.to_sql("employees", conn, if_exists="replace", index=False)
    conn.close()

    st.success("✅ employees.db created from CSV.")

# ===================================================================================  
#------------------------------- Load Data ------------------------------------------
# ===================================================================================  

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

def run_query(query, params=()):
    """
    Executes a SQL query with optional parameters.
    run_query function : Input (query-SQL query , params- tuple of parameters) , Output (nune)
    We need this function to avoid repeating the same steps of connecting to the database,
    executing the query, committing changes, and closing the connection every time we want to run a query.
    """ 
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

# ===================================================================================  
#-------------------------------Page 1 - EDA----------------------------------------
# ===================================================================================  

def page_eda(df):
    st.title("🔎 Exploratory Data Analysis (EDA)")
    

    st.markdown("""
    - **Attrition**: Whether the employee left the company (Yes/No).  
    - **BusinessTravel**: Frequency of business travel (Rarely, Frequently, Non-Travel).  
    - **DailyRate**: Daily salary rate.  
    - **Department**: Department (HR, R&D, Sales).  
    - **DistanceFromHome**: Distance between home and workplace (miles).  
     """)

    with st.expander("📂 Show more columns..."):
      st.markdown("""
    - **Education**: 1=Below College, 2=College, 3=Bachelor, 4=Master, 5=Doctor.  
    - **EducationField**: Field of education (Life Sciences, Medical, Marketing…).  
    - **EmployeeCount**: Always “1”.  
    - **EmployeeNumber**: Unique ID.  
    - **EnvironmentSatisfaction**: 1=Low, 4=Very High.  
    - **HourlyRate**: Hourly salary.  
    - **JobInvolvement**: 1=Low, 4=Very High.  
    - **JobLevel**: 1=Entry, higher=senior.  
    - **JobRole**: Job title (e.g., Sales Exec, Research Scientist, Manager).  
    - **JobSatisfaction**: 1=Low, 4=Very High.  
    - **MaritalStatus**: Single, Married, Divorced.  
    - **MonthlyIncome**: Monthly salary.  
    - **NumCompaniesWorked**: Companies worked before.  
    - **OverTime**: Overtime (Yes/No).  
    - **PercentSalaryHike**: % increase in salary.  
    - **PerformanceRating**: 1=Low, 4=Outstanding.  
    - **RelationshipSatisfaction**: 1=Low, 4=Very High.  
    - **TotalWorkingYears**: Total years of experience.  
    - **TrainingTimesLastYear**: Trainings last year.  
    - **WorkLifeBalance**: 1=Bad, 4=Very Good.  
    - **YearsAtCompany**: Years at current company.  
    - **YearsInCurrentRole**: Years in current role.  
    - **YearsSinceLastPromotion**: Years since last promotion.  
    - **YearsWithCurrManager**: Years with current manager.  
    """) 
    
    st.subheader("Preview of Dataset")
    all_columns = df.columns.tolist()
    selected_cols = st.multiselect("Select columns to display", all_columns, default=['EmployeeNumber', 'Department', 'JobRole', 'MonthlyIncome', 'Attrition'])
    st.dataframe(df[selected_cols].astype(str), use_container_width=True, height=400)

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

# ===================================================================================  
#--------------------------------Page 2 - Insights-----------------------------------
# ===================================================================================  

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

        
        # 5) Top 5 Employees by Performance
        st.subheader("Top 5 Employees by Performance Rating")
        top5 = (df.groupby("EmployeeNumber")["PerformanceRating"]
                  .max().reset_index(name="MaxRating")
                  .sort_values(["MaxRating", "EmployeeNumber"], ascending=[False, True])
                  .head(5))
        st.dataframe(top5, use_container_width=True)

        # 6) Average Monthly Income by Education
        st.subheader("Average Monthly Income by Education")
        edu_map = {1:"Below College",2:"College",3:"Bachelor",4:"Master",5:"Doctor"}
        edu_inc = (df.groupby("Education")["MonthlyIncome"].mean()
                     .reset_index(name="AvgMonthlyIncome")
                     .sort_values("Education", ascending=False))
        edu_inc["EducationLabel"] = edu_inc["Education"].map(edu_map)
        fig_edu = px.bar(edu_inc, x="EducationLabel", y="AvgMonthlyIncome",
                         text="AvgMonthlyIncome", color="EducationLabel",
                         color_discrete_sequence=["#ff375e", "#4f008c"],
                         template="plotly_white")
        st.plotly_chart(fig_edu, use_container_width=True)

        # 7) Attrition Rate by Work-Life Balance
        st.subheader("Attrition Rate by Work-Life Balance")
        wlb_attr = (df.groupby("WorkLifeBalance")["Attrition"]
                      .apply(lambda x:(x=="Yes").mean())
                      .reset_index(name="AttritionRate"))
        fig_wlb = px.bar(wlb_attr, x="WorkLifeBalance", y="AttritionRate",
                         text=wlb_attr["AttritionRate"].mul(100).round(1).astype(str)+"%",
                         color="AttritionRate", color_continuous_scale=["#4f008c", "#ff375e"],
                         template="plotly_white")
        fig_wlb.update_layout(xaxis_title="Work-Life Balance (1=Bad, 4=Best)",
                              yaxis_title="Attrition Rate", yaxis_tickformat=".0%")
        st.plotly_chart(fig_wlb, use_container_width=True)
    else:
        # SQL MODE 
        st.info("Running Insights using SQL queries from employees.db")
        conn = sqlite3.connect("Data/employees.db")

        # KPIs
        total_sql = pd.read_sql("SELECT SUM(EmployeeCount) AS Total FROM employees", conn)
        attr_sql  = pd.read_sql("SELECT AVG(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100 AS AttritionRate FROM employees", conn)
        perf_sql  = pd.read_sql("SELECT AVG(PerformanceRating) AS AvgPerf FROM employees", conn)
        inc_sql   = pd.read_sql("SELECT AVG(MonthlyIncome) AS AvgIncome FROM employees", conn)

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Total Employees", f"{int(total_sql['Total'][0]):,}")
        with k2: st.metric("Attrition Rate", f"{attr_sql['AttritionRate'][0]:.1f}%")
        with k3: st.metric("Avg Perf. Rating", f"{perf_sql['AvgPerf'][0]:.2f}")
        with k4: st.metric("Avg Monthly Income", f"${inc_sql['AvgIncome'][0]:,.0f}")

        st.markdown("---")

        # 1) Employees per Department
        st.subheader("Employees per Department (SQL)")
        dept_sql = pd.read_sql("SELECT Department, SUM(EmployeeCount) AS EmpCount FROM employees GROUP BY Department", conn)
        fig_dept = px.bar(dept_sql.sort_values("EmpCount"),
                          x="EmpCount", y="Department", orientation="h",
                          text="EmpCount", color="EmpCount",
                          color_continuous_scale=["#4f008c", "#ff375e"],
                          template="plotly_white")
        fig_dept.update_traces(textposition="outside")
        st.plotly_chart(fig_dept, use_container_width=True)

        # 2) Average Monthly Income by Job Role
        st.subheader("Average Monthly Income by Job Role (SQL)")
        inc_sql = pd.read_sql("SELECT JobRole, AVG(MonthlyIncome) AS AvgMonthlyIncome FROM employees GROUP BY JobRole", conn)
        fig_inc = px.bar(inc_sql.sort_values("AvgMonthlyIncome"),
                         x="AvgMonthlyIncome", y="JobRole", orientation="h",
                         text="AvgMonthlyIncome", color="AvgMonthlyIncome",
                         color_continuous_scale=["#4f008c", "#ff375e"],
                         template="plotly_white")
        st.plotly_chart(fig_inc, use_container_width=True)

        # 3) Average Performance by Department 
        st.subheader("Average Performance by Department (SQL)")
        perf_sql = pd.read_sql("SELECT Department, AVG(PerformanceRating) AS AvgRating FROM employees GROUP BY Department", conn)
        fig_perf = px.pie(perf_sql, names="Department", values="AvgRating",
                          color_discrete_sequence=["#4f008c", "#ff375e", "#3f2156"],
                          hole=0.35)
        st.plotly_chart(fig_perf, use_container_width=True)

        
         # 4) Overtime vs Attrition by Department        
        st.subheader("Attrition vs Overtime by Department (SQL)")
        ot_sql = pd.read_sql("""
           WITH DeptOvertime AS (
                SELECT Department,
                OverTime,
                CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END AS is_attrited
            FROM employees
             )
            SELECT Department,OverTime,AVG(is_attrited)*100 AS AttritionRate
            FROM DeptOvertime
            GROUP BY Department, OverTime;
            """, conn)
        fig_ot = px.bar(
        ot_sql,
        x="OverTime",
        y="AttritionRate",
        facet_col="Department",
        facet_col_wrap=3,
        text=ot_sql["AttritionRate"].round(1).astype(str) + "%",
        color="OverTime",
        color_discrete_sequence=["#4f008c", "#ff375e"],
         template="plotly_white")
        fig_ot.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig_ot, use_container_width=True)
        
        # 5) Top 5 Employees by Performance
        st.subheader("Top 5 Employees by Performance Rating (SQL)")
        top5_sql = pd.read_sql("""
            SELECT EmployeeNumber, MAX(PerformanceRating) AS MaxRating
            FROM employees
            GROUP BY EmployeeNumber
            ORDER BY MaxRating DESC, EmployeeNumber ASC
            LIMIT 5
        """, conn)
        st.dataframe(top5_sql, width="stretch")

        # 6) Monthly Income by Education
        st.subheader("Average Monthly Income by Education (SQL)")
        edu_sql = pd.read_sql("""
            SELECT Education, AVG(MonthlyIncome) AS AvgMonthlyIncome
            FROM employees
            GROUP BY Education
            ORDER BY Education DESC
        """, conn)
        edu_map = {1:"Below College",2:"College",3:"Bachelor",4:"Master",5:"Doctor"}
        edu_sql["EducationLabel"] = edu_sql["Education"].map(edu_map)
        fig_edu = px.bar(edu_sql, x="EducationLabel", y="AvgMonthlyIncome",
                         text="AvgMonthlyIncome", color="EducationLabel",
                         color_discrete_sequence=["#ff375e", "#4f008c"],
                         template="plotly_white")
        st.plotly_chart(fig_edu, use_container_width=True)

        # 7) Attrition by Work-Life Balance
        st.subheader("Attrition by Work-Life Balance (SQL)")
        wlb_sql = pd.read_sql("""
            SELECT WorkLifeBalance,
                   SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*1.0/COUNT(*) AS AttritionRate
            FROM employees
            GROUP BY WorkLifeBalance
        """, conn)
        fig_wlb = px.bar(wlb_sql, x="WorkLifeBalance", y="AttritionRate",
                         text=wlb_sql["AttritionRate"].mul(100).round(1).astype(str)+"%",
                         color="AttritionRate", color_continuous_scale=["#4f008c", "#ff375e"],
                         template="plotly_white")
        fig_wlb.update_layout(xaxis_title="Work-Life Balance (1=Bad, 4=Best)",
                              yaxis_title="Attrition Rate", yaxis_tickformat=".0%")
        st.plotly_chart(fig_wlb, use_container_width=True)

        conn.close()

# ===================================================================================  
#--------------------------------- Page 3 - Manage Employees-------------------------
# ===================================================================================
def page_manage():
    st.title("👥 Manage Employees")

    # Add new employee
    st.subheader("Add New Employee")
    with st.form("add_form"):
        emp_num = st.text_input("Employee Number")
        dept = st.text_input("Department")
        role = st.text_input("Job Role")
        income = st.number_input("Monthly Income", min_value=0)
        edu = st.selectbox("Education", [1,2,3,4,5])
        wlb = st.selectbox("Work-Life Balance", [1,2,3,4])
        submitted = st.form_submit_button("Add Employee")
        if submitted:
            run_query("INSERT INTO employees (EmployeeNumber, Department, JobRole, MonthlyIncome, Education, WorkLifeBalance, EmployeeCount) VALUES (?, ?, ?, ?, ?, ?, 1)",
                      (emp_num, dept, role, income, edu, wlb))
            st.success(f"Employee {emp_num} added!")

    st.markdown("---")

    # Update employee
    st.subheader("Update Employee ")
    with st.form("update_form"):
        emp_num = st.text_input("Employee Number to Update")
        new_income = st.number_input("New Monthly Income", min_value=0)
        new_dept = st.text_input("New Department")
        new_role = st.text_input("New Job Role")
        new_edu = st.selectbox("New Education", [1,2,3,4,5])
        new_wlb = st.selectbox("New Work-Life Balance", [1,2,3,4])
        new_ot = st.selectbox("New Overtime", ["Yes","No"])
        submitted = st.form_submit_button("Update Employee")
        if submitted:
            run_query("""UPDATE employees
                         SET MonthlyIncome=?, Department=?, JobRole=?, Education=?, WorkLifeBalance=?, OverTime=?
                         WHERE EmployeeNumber=?""",
                      (new_income, new_dept, new_role, new_edu, new_wlb, new_ot, emp_num))
            st.success(f"Employee {emp_num} updated!")

    st.markdown("---")

    # Delete Employee
    st.subheader("🗑️ Delete Employee ")
    with st.form("delete_form"):
        emp_num_del = st.number_input("Employee Number to Delete", min_value=1, step=1)
        delete = st.form_submit_button("Delete Employee")
        if delete:
            run_query("DELETE FROM employees WHERE EmployeeNumber=?", (emp_num_del,))
            st.success(f"Employee #{emp_num_del} deleted from database!")

# ===================================================================================  
#---------------------------------- Main---------------------------------------------
# ===================================================================================  


st.sidebar.image("Images/top_banner.png", use_container_width=True)  
st.sidebar.title("IBM Hr Data Analysis")
page = st.sidebar.radio("Go to", ["EDA", "Insights", "Manage Employees"])
st.sidebar.image("Images/bottom_banner.png", use_container_width =True) 


#Calling all the function 
df = load_data()

if page == "EDA":
    page_eda(df)
elif page == "Insights":
    page_insights(df)
elif page == "Manage Employees":
    page_manage()   