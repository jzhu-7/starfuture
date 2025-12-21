
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="🏠 销售数据大屏",
    layout="wide",
    page_icon="🏠",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 全局样式 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 标题样式 */
    .title {
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #e8f4f8;
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    /* 卡片样式 */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-top: 0.5rem;
    }
    
    /* 图表容器 */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
    }
    
    /* 数据表格样式 */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* 展开器样式 */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("## 🏠 控制面板")
    st.markdown("---")
    
    # 数据更新按钮
    if st.button("🔄 更新数据", key="update"):
        st.info("请在终端运行数据更新脚本")
    
    # 日期选择
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and f.startswith('20')]
    folders = sorted(folders, reverse=True)
    if folders:
        selected_date = st.selectbox("📅 选择数据日期", folders, index=0)
    else:
        st.error("未找到数据文件夹")
        selected_date = None
    
    st.markdown("---")
    st.markdown("### 📊 数据概览")
    st.markdown("实时销售数据分析平台")

# 主页面标题
st.markdown('<div class="title">🏠 销售数据大屏</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">现代化数据可视化 | 实时销售监控 | 智能趋势分析</div>', unsafe_allow_html=True)

# 加载数据
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("presale_stats.csv", encoding="utf-8-sig")
        df['日期'] = pd.to_datetime(df['日期'])
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

# 获取房屋面积信息
@st.cache_data
def get_house_area(building, room_number):
    try:
        # 映射楼栋号：13 -> 5-13, 14 -> 5-14, etc.
        if building.isdigit():
            mapped_building = f"5-{building}"
        else:
            mapped_building = building
            
        file_path = f"houses_by_building/houses_{mapped_building}#住宅楼.csv"
        if os.path.exists(file_path):
            house_df = pd.read_csv(file_path, encoding="utf-8-sig")
            # 直接查找包含房间号的房号
            for _, row in house_df.iterrows():
                house_number = str(row['房号'])
                if room_number in house_number:
                    return row['建筑面积(㎡)']
        return None
    except Exception as e:
        return None

# 解析最新成交户号并获取详细信息
def get_latest_transactions():
    if df is None or df.empty:
        return []
    
    latest_row = df.iloc[-1]
    house_numbers = str(latest_row['成交户号']).strip()
    
    if not house_numbers or house_numbers == 'nan':
        return []
    
    # 分割多个户号
    house_list = [h.strip() for h in house_numbers.split(',') if h.strip()]
    
    transactions = []
    total_area = latest_row['面积(M2)']
    
    for house in house_list:
        # 解析户号格式，如 "13#1-501" -> building="13", room_number="501"
        if '#' in house:
            building, room_part = house.split('#', 1)
            # 提取房间号（最后一部分）
            if '-' in room_part:
                room_number = room_part.split('-')[-1]  # 取最后一部分作为房间号
            else:
                room_number = room_part
            
            area = get_house_area(building, room_number)
            if area is None and total_area and len(house_list) > 0:
                # 如果找不到具体面积，从总面积平均分配
                area = total_area / len(house_list)
            
            transactions.append({
                '户号': house,
                '面积': area if area else "未找到"
            })
    
    return transactions

df = load_data()
if df is None or df.empty:
    st.stop()

# 关键指标卡片
st.markdown("## 📈 核心指标")
col1, col2, col3, col4 = st.columns(4)

latest = df.iloc[-1]

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{int(latest["已签约套数"])}</div>
        <div class="metric-label">已签约套数</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{latest["已签约面积(M2)"]:.1f}</div>
        <div class="metric-label">已签约面积 (M²)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">¥{latest["成交均价(￥/M2)"]:,.0f}</div>
        <div class="metric-label">成交均价 (¥/M²)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">¥{latest["均价(￥/M2)"]:,.0f}</div>
        <div class="metric-label">最新均价 (¥/M²)</div>
    </div>
    """, unsafe_allow_html=True)

# 最新成交户口
st.markdown("## 🏠 最新成交户口")
latest_transactions = get_latest_transactions()

if latest_transactions:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📋 成交户号")
        for transaction in latest_transactions:
            st.markdown(f"**{transaction['户号']}**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📐 对应面积 (M²)")
        for transaction in latest_transactions:
            if isinstance(transaction['面积'], str):
                st.markdown(f"**{transaction['面积']}**")
            else:
                st.markdown(f"**{transaction['面积']:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("暂无最新成交户口信息")

# 图表区域
st.markdown("## 📊 数据可视化")

# 均价趋势图
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown("### 📈 价格趋势分析")

fig_price = go.Figure()
fig_price.add_trace(go.Scatter(
    x=df['日期'], 
    y=df['成交均价(￥/M2)'], 
    mode='lines+markers',
    name='成交均价',
    line=dict(color='#3498db', width=3),
    marker=dict(size=8, color='#3498db')
))
fig_price.add_trace(go.Scatter(
    x=df['日期'], 
    y=df['均价(￥/M2)'], 
    mode='lines+markers',
    name='最新均价',
    line=dict(color='#e74c3c', width=3),
    marker=dict(size=8, color='#e74c3c')
))

fig_price.update_layout(
    title="",
    xaxis_title="日期",
    yaxis_title="价格 (¥/M²)",
    template="plotly_white",
    height=400,
    margin=dict(l=20, r=20, t=20, b=20)
)
st.plotly_chart(fig_price, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 签约套数和面积趋势
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 🏢 签约套数趋势")
    
    fig_units = px.bar(
        df, 
        x='日期', 
        y='已签约套数',
        color_discrete_sequence=['#27ae60']
    )
    fig_units.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_units, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📐 签约面积趋势")
    
    fig_area = px.area(
        df, 
        x='日期', 
        y='已签约面积(M2)',
        color_discrete_sequence=['#f39c12']
    )
    fig_area.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_area, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 数据详情表格
st.markdown("## 📋 详细数据")
with st.expander("展开查看完整数据表格", expanded=False):
    st.dataframe(
        df.style.format({
            '已签约面积(M2)': '{:.2f}',
            '成交均价(￥/M2)': '{:,.0f}',
            '均价(￥/M2)': '{:,.0f}',
            '面积(M2)': '{:.2f}',
            '总价(￥)': '{:,.0f}'
        }),
        use_container_width=True,
        hide_index=True
    )

# # 页脚
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; color: rgba(255,255,255,0.7); padding: 1rem;'>
#     <p>💡 数据来源：presale_stats.csv | 现代化设计 by GitHub Copilot</p>
#     <p>最后更新时间：{}</p>
# </div>
# """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)