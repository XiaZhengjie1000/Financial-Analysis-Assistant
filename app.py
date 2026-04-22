import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 页面标题
st.title("交互式数据分析可视化工具")
st.subheader("上传CSV文件即可自动分析数据")

# 1. 文件上传功能
uploaded_file = st.file_uploader("请上传CSV格式数据文件", type="csv")

if uploaded_file is not None:
    # 读取数据
    df = pd.read_csv(uploaded_file, sep=r'[,	]', encoding='utf-8')
    
    # 展示原始数据
    st.subheader("1. 原始数据集")
    st.dataframe(df)

    # 2. 数据基础统计信息
    st.subheader("2. 数据描述性统计")
    st.write(df.describe())

    # 3. 选择列进行可视化
    st.subheader("3. 自定义数据图表")
    columns = df.columns.tolist()
    
    x_col = st.selectbox("选择X轴字段", columns)
    y_col = st.selectbox("选择Y轴字段", columns)
    chart_type = st.selectbox("选择图表类型", ["柱状图", "折线图", "散点图"])

    # 画图
    fig, ax = plt.subplots()
    if chart_type == "柱状图":
        ax.bar(df[x_col], df[y_col])
    elif chart_type == "折线图":
        ax.plot(df[x_col], df[y_col])
    else:
        ax.scatter(df[x_col], df[y_col])

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    st.pyplot(fig)

else:
    st.info("请先上传CSV文件开始分析")
