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
    # 4. AI 定量+定性商业洞察（联网大模型｜宏观→微观结构化）
    # --------------------------
    st.subheader("4️⃣ AI 商业洞察（宏观→微观结构化分析）")

    try:
        data_info = f"""
【数据基本信息】
- 数据集形状：{df.shape[0]}行 × {df.shape[1]}列
- 字段名：{list(df.columns)}
- 数值字段描述性统计：
{df.describe().round(2)}
- 前5行样本：
{df.head()}
    """.strip()

        prompt = f"""
你是资深商业分析师，基于下面【数据】做**时间趋势类商业分析**，要求：
1. 结构必须严格按：
   一、行业概况（宏观：行业界定、发展历程、定量的国内外市场规模、产业链介绍）
   二、宏观行业PEST+ESG分析（政治/经济/社会/技术 + 环境/社会责任/治理）
   三、微观竞争：波特五力分析
   四、最微观落地：SWOT + 3条可执行商业建议
2. 每一小节结尾必须换行并追加一句【小结论】，简短易读。
3. 语言商业、简洁、量化、结构化，不要 Markdown 标题，用“一、二、三、四、”和“1.2.3.”分层。
4. 结合你的数据库、联网数据与提供数据的**时间趋势、规模、波动、相关性、异常值**做定量；结合业务做定性。

【数据】
{data_info}
    """.strip()

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
    except Exception as e:
        st.error(f"AI 分析出错：{e}")

else:
    st.info("👆 请先上传 CSV / Excel 文件，才能使用全部功能~")
    st.subheader("AI 商业洞察 示例")
    st.info("""
AI 商业洞察（结构化示例）：
一、行业概况
1. 行业界定：本数据所属行业为典型时间序列驱动的消费/零售类赛道。
2. 发展历程：整体呈稳步增长，近年受宏观环境影响增速放缓。
3. 市场规模：国内规模领先，国际市场具备扩张潜力。
4. 产业链：上游供给稳定、中游竞争集中、下游渠道多元。
【小结论】行业处于成熟期，规模大、链条完整、增长稳中承压。

二、PEST+ESG分析
1. 政治（P）：政策趋严，合规成本上升。
2. 经济（E）：通胀与利率波动影响消费力。
3. 社会（S）：健康化、智能化需求提升。
4. 技术（T）：数字化与AI应用加速渗透。
5. ESG：环保与数据合规成为核心门槛。
【小结论】宏观整体中性偏利好，合规与技术是关键变量。

三、波特五力
1. 新进入者：中等（有资金/技术壁垒）。
2. 替代品：中高（跨界替代活跃）。
3. 现有竞争：激烈（集中度一般、价格战常见）。
4. 供应商议价：中等（依赖核心资源）。
5. 购买者议价：高（价格敏感、信息透明）。
【小结论】行业竞争偏激烈，利润易被上下游挤压。

四、SWOT+落地建议
1. 优势（S）：数据完整、趋势清晰、用户基础稳定。
2. 劣势（W）：抗波动弱、产品同质化、数字化不足。
3. 机会（O）：细分增长、出海、AI提效、ESG溢价。
4. 威胁（T）：宏观下行、政策收紧、跨界竞争。
【小结论】整体机遇大于风险，需靠差异化与合规构建壁垒。

可执行建议：
1. 按时间节点做季度滚动预测，提前对冲波动。
2. 加大数字化与AI投入，提升运营效率与用户体验。
3. 完善ESG合规体系，规避政策风险并获取溢价。
        """)
