# 📊 IBM HR Employee  Dashboard

An interactive **Streamlit web app** for analyzing IBM HR Employee data.  
It allows you to explore the dataset, generate insights with **Pandas or SQL**, and manage employee records directly.

---

## 🚀 Features

- **Database Setup**  
  - If `employees.db` is missing, it is created automatically from the CSV file.  

- **EDA (Exploratory Data Analysis)**  
  - Dataset preview with column explanations  
  - Missing values overview  
  - Column distribution plots  

- **Insights**  
  - Switch between **DataFrame (Python)** and **Database (SQL)** modes  
  - KPIs (Total Employees, Attrition Rate, Performance Rating, Income)  
  - Charts:  
    - Employees per Department  
    - Avg Monthly Income by Job Role  
    - Avg Performance by Department  
    - Overtime vs Attrition by Department  
    - Top 5 Employees by Performance  
    - Income by Education  
    - Attrition vs Work-Life Balance  

- **Manage Employees**  
  - Add new employees  
  - Update employee details  
  - Delete employees  

---


## 📂 Project Structure

HR Project/  
│── employees.db                     # SQLite database (auto-created if missing)  
│── WA_Fn-UseC_-HR-Employee-Attrition.csv   # Original dataset  
│── app.py                           # Main Streamlit app  
│── IBM_HrData_Notebook.ipynb        # Jupyter Notebook with extended EDA & insights  
│── requirements.txt                 # Project dependencies  
│── top_banner.png                   # Sidebar top banner image  
│── bottom_banner.png                # Sidebar bottom banner image  
│── README.md                        # Project documentation  


---
## 🛠 Tools & Apps Needed

To run this project you will need:  
- **Python 3.9+**  
- **Conda** (Anaconda or Miniconda)   
- **Streamlit** 
- **Jupyter Notebook** 
- **SQLite**   
- **VS Code** 


---

## ⚡ Setup & Run (with Conda)

1. **Clone or Download** this project folder.  

2. **Install Anaconda / Miniconda**  

3. **Create a new environment and run the app**  
   ``` conda prompt or command prompt 
   -conda create -n IBMHRDataAnalysis python=3.10 -y

   -conda activate IBMHRDataAnalysis

   -pip install -r requirements.txt

   -streamlit run app.py