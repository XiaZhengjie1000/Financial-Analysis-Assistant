import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config(
    page_title="Business Intelligence Analytics Tool",
    page_icon="📊",
    layout="wide"
)

plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# --------------------------
# Title
# --------------------------
st.title("📊 Business Intelligence Interactive Analytics Tool")
st.subheader("Data Acquisition | Cleaning | Transformation | Visualization | AI Business Insights")

# --------------------------
# File Upload
# --------------------------
uploaded_file = st.file_uploader("Upload CSV / Excel File", type=["csv", "xlsx"])

if uploaded_file is not None:

    # ======================
    # Data Format Transformation (Header Settings)
    # ======================
    st.subheader("🔁 Data Format Transformation (Header Settings)")
    header_mode = st.radio(
        "Select Header Type",
        ["Standard Row Header (First row as field names)",
         "Standard Column Header (First column as field names)",
         "Both Row & Column as Headers"]
    )

    # Read Data
    if uploaded_file.name.endswith('.xlsx'):
        df_raw = pd.read_excel(uploaded_file)
    else:
        encodings = ["utf-8-sig", "gb18030", "gbk", "utf-8"]
        df_raw = None
        for enc in encodings:
            try:
                uploaded_file.seek(0)
                df_raw = pd.read_csv(uploaded_file, sep=r'[,\t]', encoding=enc, on_bad_lines="skip")
                break
            except:
                continue
        if df_raw is None:
            uploaded_file.seek(0)
            df_raw = pd.read_csv(uploaded_file, sep=r'[,\t]', encoding="latin-1")

    # Process three header formats
    if header_mode == "Standard Row Header (First row as field names)":
        df = df_raw.copy()

    elif header_mode == "Standard Column Header (First column as field names)":
        df = df_raw.set_index(df_raw.columns[0]).T
        df = df.reset_index()

    elif header_mode == "Both Row & Column as Headers":
        row_headers = df_raw.iloc[:, 0].astype(str).fillna("")
        col_headers = df_raw.columns[1:].astype(str)
        new_cols = []
        for c in col_headers:
            for r in row_headers:
                new_cols.append(f"{c}_{r}")
        data = df_raw.iloc[:, 1:].values.flatten()
        df = pd.DataFrame([data], columns=new_cols)

    # ======================
    # Data Type Check
    # ======================
    st.subheader("🔍 Data Type Check")
    dtype_df = pd.DataFrame(df.dtypes, columns=["Data Type"])
    st.dataframe(dtype_df, use_container_width=True)

    # ======================
    # Date Auto-Processing
    # ======================
    st.subheader("📅 Automatic Date Format Processing")

    keywords = ["时间", "日期", "年份", "月份", "Date", "Time"]
    date_cols = [col for col in df.columns if any(k in str(col) for k in keywords)]

    for col in date_cols:
        temp_dt = pd.to_datetime(df[col], errors="coerce")
        valid_num = temp_dt.notna().sum()
        if valid_num > 1:
            df[col] = temp_dt
            df['year'] = df[col].dt.year
            df['month'] = df[col].dt.month
            df['day'] = df[col].dt.day

    st.dataframe(df.head(10), use_container_width=True)

    # ======================
    # Custom Column Renaming
    # ======================
    st.subheader("✏️ Custom Column Renaming")
    new_names = {}
    cols = df.columns.tolist()
    for c in cols:
        new_names[c] = st.text_input(f"Original Column: {c}", value=c)

    if st.button("Apply Column Name Changes"):
        df = df.rename(columns=new_names)
        st.success("Column names updated successfully")
        st.dataframe(df.head(5), use_container_width=True)

    # ======================
    # 6 Data Cleaning Options
    # ======================
    st.subheader("🧹 Data Cleaning Options (Choose 1)")
    clean_option = st.selectbox(
        "Select Cleaning Method",
        [
            "No Cleaning",
            "Drop Rows with Missing Values",
            "Linear Interpolation (Trend)",
            "Mean Imputation",
            "Median Imputation",
            "Mode Imputation"
        ]
    )

    df_clean = df.copy()
    numeric_cols = df_clean.select_dtypes(include=['number']).columns

    if clean_option == "Drop Rows with Missing Values":
        df_clean = df_clean.dropna()

    elif clean_option == "Linear Interpolation (Trend)":
        df_clean[numeric_cols] = df_clean[numeric_cols].interpolate(method="linear")

    elif clean_option == "Mean Imputation":
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())

    elif clean_option == "Median Imputation":
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())

    elif clean_option == "Mode Imputation":
        df_clean = df_clean.fillna(df_clean.mode().iloc[0])

    st.dataframe(df_clean.head(10), use_container_width=True)
    st.success(f"Applied: {clean_option}")

    # ======================
    # Cleaned Dataset & Descriptive Statistics
    # ======================
    st.subheader("1️⃣ Final Cleaned Dataset")
    st.dataframe(df_clean, use_container_width=True)

    st.subheader("2️⃣ Descriptive Statistics")
    st.dataframe(df_clean.describe(include='all').round(2), use_container_width=True)

    # ======================
    # Data Visualization
    # ======================
    st.subheader("3️⃣ Data Visualization")
    cols = df_clean.columns.tolist()
    x_col = st.selectbox("X-axis", cols)
    y_col = st.selectbox("Y-axis", cols)
    chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot"])

    plot_df = df_clean.copy()
    plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors='coerce')
    plot_df[y_col] = plot_df[y_col].interpolate(method="linear")

    fig, ax = plt.subplots(figsize=(8, 4))
    if chart_type == "Bar Chart":
        ax.bar(plot_df[x_col], plot_df[y_col])
    elif chart_type == "Line Chart":
        ax.plot(plot_df[x_col], plot_df[y_col], marker='o')
    elif chart_type == "Scatter Plot":
        ax.scatter(plot_df[x_col], plot_df[y_col])

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    st.pyplot(fig)

    # ======================
    # AI Business Insights
    # ======================
    st.subheader("4️⃣ AI Macro-to-Micro Structured Business Analysis")
    with st.spinner("AI Analyzing..."):
        try:
            data_info = f"""
Data Size: {df_clean.shape[0]} rows {df_clean.shape[1]} columns
Features: {list(df_clean.columns)}
Descriptive Stats: {df_clean.describe().round(2)}
Sample: {df_clean.head()}
            """
            prompt = f"""
You are a senior business analyst. Provide structured analysis strictly in this format:
1. Industry Overview (definition, development, market size, industry chain)
2. PEST + ESG Analysis
3. Porter's Five Forces Analysis
4. SWOT + 3 Actionable Recommendations
Add a short [Conclusion] after each section.
Data: {data_info}
            """
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Content-Type": "application/json","Authorization": "Bearer sk-6a11f0523d5f42819578280b84f16f12"},
                json={"model":"deepseek-chat","messages":[{"role":"user","content":prompt}],"temperature":0.1},
                timeout=30
            )
            if response.status_code == 200:
                st.success(response.json()["choices"][0]["message"]["content"])
        except:
            st.warning("AI service unavailable temporarily")

else:
    st.info("Please upload a file to start analysis")
