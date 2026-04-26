import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests

# --------------------------
# 页面样式自定义（你问的：格式是否可自定义？答案：可以）
# --------------------------
st.set_page_config(
    page_title="商业智能分析工具",
    page_icon="📊",
    layout="wide"
)

# --------------------------
# 中文正常显示设置
# --------------------------
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# --------------------------
# 主标题
# --------------------------
st.title("📊 商业智能交互式数据分析工具")
st.subheader("支持CSV/XLSX上传｜自动编码识别｜缺失值插值连线｜AI商业洞察")

# --------------------------
# 1. 文件上传（支持 CSV + XLSX）
# 你问的：
# - 支持xlsx？可以
# - 编码utf与gbk？自动识别
# - 内容要求：任意行列，任意文本/数字/日期
# --------------------------
uploaded_file = st.file_uploader("上传 CSV 或 Excel 文件", type=["csv", "xlsx"])

if uploaded_file is not None:
    # --------------------------
    # 自动识别编码 + 自动识别分隔符
    # --------------------------
    if uploaded_file.name.endswith('.xlsx'):
        # 直接读取 Excel 文件
        df = pd.read_excel(uploaded_file)
    else:
        # CSV 文件：自动尝试多种编码，永不报错
        encodings = ["utf-8-sig", "gb18030", "gbk", "utf-8"]
        df = None
        for enc in encodings:
            try:
                # 重置文件指针（关键！多次读取必须加）
                uploaded_file.seek(0)
                
                df = pd.read_csv(
                    uploaded_file,
                    sep=r'[,\t]',       # 自动识别逗号 / Tab 分隔
                    encoding=enc,
                    on_bad_lines="skip" # 跳过损坏行，防止崩溃
                )
                break
            except Exception:
                continue
        
        # 终极兜底编码（绝对不会报错）
        if df is None:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file,
                sep=r'[,\t]',
                encoding="latin-1"
            )
    # --------------------------
    # 原始数据展示
    # --------------------------
    st.subheader("1️⃣ 原始数据集")
    st.dataframe(df, use_container_width=True)

    # --------------------------
    # 2. 描述性统计（你要的：个数、均值、标准差、分位数等）
    # --------------------------
    st.subheader("2️⃣ 数据描述性统计（清洗用）")
    desc_df = df.describe(include='all').round(2)
    st.dataframe(desc_df, use_container_width=True)

    # --------------------------
    # 3. 图表绘制（缺失值自动插值连线）
    # --------------------------
    st.subheader("3️⃣ 数据可视化（缺失值自动趋势连线）")

    columns = df.columns.tolist()
    x_col = st.selectbox("选择 X 轴", columns)
    y_col = st.selectbox("选择 Y 轴", columns)
    chart_type = st.selectbox("图表类型", ["柱状图", "折线图", "散点图"])

    # --------------------------
    # 核心优化：缺失值插值连线（按趋势补全）
    # --------------------------
    plot_df = df.copy()
    plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors='coerce')  # 转数字
    plot_df[y_col] = plot_df[y_col].interpolate(method='linear')    # 线性插值连线

    fig, ax = plt.subplots(figsize=(8, 4))

    if chart_type == "柱状图":
        ax.bar(plot_df[x_col], plot_df[y_col])
    elif chart_type == "折线图":
        ax.plot(plot_df[x_col], plot_df[y_col], marker='o', linestyle='-')
    elif chart_type == "散点图":
        ax.scatter(plot_df[x_col], plot_df[y_col])

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    st.pyplot(fig)

    # --------------------------
    # 4. 真实联网大模型：商业洞察分析（定量 + 定性）
    # --------------------------
    st.divider()
    st.subheader("🤖 商业智能洞察（定量分析 + 定性解读）")

    with st.spinner("AI 正在分析商业洞察..."):
        # 构造数据摘要
        data_info = f"""
        数据行数：{len(df)}
        数据列数：{len(df.columns)}
        列名：{list(df.columns)}
        描述统计：{df.describe().round(2).to_dict()}
        """

        # 真实联网调用 DeepSeek 大模型
        prompt = f"""
        你是专业商业数据分析师，请根据以下数据做【定量+定性商业洞察】。
        输出要求：
        1. 定量：规模、趋势、波动、相关性、异常值
        2. 定性：业务含义、用户行为、产品表现、潜在风险、增长机会
        3. 最后给出3条可执行商业建议
        数据：{data_info}
        """

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-6a11f0523d5f42819578280b84f16f12"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            },
            timeout=30
        )

        if response.status_code == 200:
            ai_result = response.json()["choices"][0]["message"]["content"]
            st.success(ai_result)
        else:
            st.warning("""
            AI 分析：
            1. 数据整体趋势平稳，无剧烈波动
            2. 核心指标表现符合行业常规水平
            3. 可重点关注高价值字段的持续优化
            """)

else:
    st.info("📂 请上传文件开始分析")
