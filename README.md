# Big Mart Sales Prediction using Machine Learning & Multi-Platform Dashboards
# 🎯 Project Objective
To bridge data science modeling with practical deployment by delivering multi-platform analytical dashboards that forecast retail sales performance and streamline automated reporting.

## 📌 Project Overview
This project predicts sales for Big Mart products using advanced Machine Learning techniques (Linear Regression and XGBoost). It evaluates critical features such as Item MRP, Outlet Identifier, Outlet Size, Outlet Type, and Outlet Establishment Year to forecast current sales and project a 5-year sales trajectory with confidence intervals. The project is deployed across dual interfaces—a cloud-ready **Streamlit Web Application (`app.py`)** and a **Tkinter Desktop Application (`frontend.py`)**—powered by a modular `backend.py` architecture. It also includes batch CSV processing and automated exportable CSV and PDF reporting with embedded textual summaries.

## 🚀 Key Features
- **5-Year Sales Forecasting:** Generates multi-year sales trends and confidence bounds using trained ML models.
- **What-If Price/Discount Slider:** Dynamically adjusts item MRP to analyze real-time sales impact.
- **Batch CSV Prediction:** Supports multi-row bulk predictions with smart, flexible column-mapping logic.
- **Automated Report Generation:** Exports detailed projection reports in CSV and PDF formats complete with embedded summary overview paragraphs.
- **Dual Platforms:** Includes both a modern Streamlit web dashboard and an interactive Tkinter desktop interface.
- **Feature Importance Analysis:** Visualizes what drives model predictions using feature ranking charts.

## 🛠 Technologies Used
- **Python**
- **Machine Learning & Data Processing:** scikit-learn, XGBoost, pandas, NumPy, joblib
- **Web & Desktop Frameworks:** Streamlit, Tkinter, Matplotlib
- **Reporting & Document Generation:** ReportLab (PDF), Python standard CSV library

## 📂 Dataset & Input Features
The project analyzes the following core features:
- `Item_MRP`: Maximum Retail Price of the product
- `Outlet_Identifier`: Unique store ID (e.g., OUT010, OUT013, OUT027)
- `Outlet_Size`: Scale of the store (High, Medium, Small)
- `Outlet_Type`: Category of the store (Grocery Store, Supermarket Types 1–3)
- `Outlet_Establishment_Year`: Year the store was established

## ⚙️ Modular Architecture & Working Process
1. **`backend.py`**: Houses the core ML prediction logic, model loading via `joblib`, 5-year trajectory simulation, confidence intervals, and feature importance analysis.
2. **`app.py` (Streamlit)**: Cloud-ready web dashboard providing single-item dynamic forecasting, batch CSV uploads with auto-column matching, and side-by-side report downloads.
3. **`frontend.py` (Tkinter)**: Desktop GUI application mirroring the web dashboard capabilities for local execution.
4. **Execution Flow**: Users supply item/outlet metrics $\rightarrow$ data passes through preprocessing and regression models $\rightarrow$ outputs generate visual charts, breakdown tables, and downloadable summary reports.

## ▶️ How to Run the Project

1. **Clone the repository**
     ```bash
   git clone [https://github.com/boomirosh/bigmart_sales_prediction_usingML.git](https://github.com/boomirosh/bigmart_sales_prediction_usingML.git)
   cd bigmart_sales_prediction_usingML

**Install required dependencies**
**Bash**
pip install streamlit pandas numpy matplotlib scikit-learn xgboost joblib reportlab

**Run the Streamlit Web Application**
**Bash**
streamlit run app.py
**(Open http://localhost:8501 in your browser)**

**Alternatively, run the Tkinter Desktop Application**

**Bash**
python frontend.py

**🖥️ Usage Guide**
$ Single Item & What-If Tab: Enter the item MRP, select outlet characteristics, adjust the price slider, and click PREDICT SALES to view trends and export reports.

$ Batch CSV Prediction Tab: Upload a custom CSV file containing product records to instantly run bulk predictions.

👩‍💻 Author
S.K. BOOMIKA
