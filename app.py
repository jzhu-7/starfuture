import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import json
import sys
import subprocess
import html
import textwrap
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 页面配置与全局样式
# ==========================================
st.set_page_config(
    page_title="星耀未来销售数据",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLOR_PRIMARY = "#007b8c"  # 累计/主色
COLOR_SECONDARY = "#f28e52" # 当日/辅助色
COLOR_BG = "#f8fafc"

# 自定义CSS样式
# ==========================================
# 1. 页面配置与全局样式 (完整替换版)
# ==========================================
st.markdown("""
<style>
    /* 1. 强制全局字体和背景 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f0f2f6 !important;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    }

    /* 2. 侧边栏“更新数据”按钮专供样式 */
    [data-testid="stSidebar"] .stButton:first-of-type button {
        background: #007b8c !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1rem !important;
        border-radius: 24px !important;
        font-weight: 700 !important;
        height: 3.5rem !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(0, 123, 140, 0.2) !important;
        transition: all 0.3s ease !important;
        display: block !important;
    }

    [data-testid="stSidebar"] .stButton:first-of-type button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(0, 123, 140, 0.4) !important;
        filter: brightness(1.05);
    }

    /* 3. 主界面“跳转/操作”按钮样式 */
    .stButton button {
        background: #f28e52 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(242, 142, 82, 0.3) !important;
        transition: all 0.2s ease !important;
        width: auto !important;
        min-width: 160px;
    }

    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 20px rgba(242, 142, 82, 0.4) !important;
    }

    /* 按钮公用点击缩放 */
    button:active {
        transform: scale(0.97) !important;
    }

    /* 4. 标题美化 */
    .main-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #007b8c 0%, #00b5b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 1.5rem 0;
        letter-spacing: -1px;
    }

    /* 5. 核心指标卡片美化 */
    .metric-container {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border: 1px solid #f1f5f9;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.08);
        border-color: #e2e8f0;
    }

    .metric-container::after {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 4px;
        background: linear-gradient(90deg, #007b8c, #00b5b8);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 8px;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 环比气泡 */
    .kpi-change {
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        position: absolute;
        top: 15px;
        right: 15px;
    }
    .kpi-change.up { background-color: #dcfce7; color: #166534; }
    .kpi-change.down { background-color: #fee2e2; color: #991b1b; }
    .kpi-change.none { background-color: #f1f5f9; color: #475569; }

    /* 6. 成交房号卡片 */
    .house-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 5px solid #f28e52;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }
    .house-card:hover {
        background-color: #f8fafc;
        transform: translateX(4px);
    }
    .house-info {
        flex: 1 1 auto;
        min-width: 0;
    }
    .house-no {
        font-weight: 800;
        color: #0f172a;
        font-size: 1.05rem; /* 字号加大 */
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 8px;
    }
    .house-area {
        color: #475569;
        font-size: 0.95rem;
    }
    .house-price {
        background: linear-gradient(90deg,#f28e52,#ffb380);
        color: white;
        font-weight: 900;
        padding: 0.6rem 1.2rem; /* 更大内边距 */
        border-radius: 999px;
        box-shadow: 0 10px 30px rgba(242,142,82,0.18);
        margin-left: 16px;
        white-space: nowrap;
        flex-shrink: 0;
        font-size: 1.05rem; /* 更大字号 */
        min-width: 96px;
        text-align: center;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .house-price:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 12px 36px rgba(242,142,82,0.22);
    }

    /* 7. 成交明细总体卡片 */
    .detail-card {
        position: relative; /* 允许 ::after 定位 */
        background: white;
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 8px 30px rgba(15,23,42,0.06);
        border: 1px solid transparent;
        margin-bottom: 1rem;
        height: 580px; /* 固定高度，增加以容纳完整图表 */
        box-sizing: border-box;
        overflow: hidden;
    }
    .detail-card::after {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 6px; /* 渐变条高度 */
        background: linear-gradient(90deg, #f28e52 0%, #ffb380 100%); /* 纯橙色渐变 */
        border-top-left-radius: 14px;
        border-top-right-radius: 14px;
    }
    .detail-card .card-header {
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding-bottom:0.5rem;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom:0.75rem;
        height: 56px;
    }
    .detail-card .card-title {
        font-size:1.1rem;
        font-weight:800;
        color:#0f172a;
    }
    .detail-card .card-body {
        height: calc(100% - 56px);
        overflow-y:auto;
        padding-right:6px;
        padding-bottom: 16px;
    }

    /* 空状态样式：居中显示信息 */
    .detail-empty {
        display:flex;
        align-items:center;
        justify-content:center;
        color:#64748b;
        font-weight:700;
        padding:1.5rem 0;
    }

    /* 将紧跟在卡片后的按钮上移，视觉上看起来像在卡片内部 */
    .detail-card + .stButton {
        margin-top: -52px;
        display:flex;
        justify-content:flex-end;
        margin-right: 10px;
    }
    .detail-card + .stButton button {
        border-radius: 10px !important;
        background: #f28e52 !important;
        color: white !important;
        box-shadow: 0 6px 18px rgba(242, 142, 82, 0.24) !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 数据加载与处理函数
# ==========================================

@st.cache_data
def load_all_data(project: str = "house"):
    """加载指定项目的完整 JSON 数据并转换为 DataFrame
    project: 'house' 或 'warehouse'
    """
    file_path = os.path.join("data", project, "total.json")
    if not os.path.exists(file_path):
        return pd.DataFrame()  # 返回空DataFrame避免报错

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)
        if not df.empty and '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values(by='日期')  # 确保按日期排序

            # 转换数值列，处理空字符串等无效值为NaN
            numeric_columns = [
                '已签约套数', '已签约面积(M2)', '成交均价(￥/M2)',
                '面积(M2)', '总价(￥)', '均价(￥/M2)'
            ]
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()
    
def run_update_script(project: str = "house", command: str = "data", timeout=300):
    """执行后端更新脚本（可以指定 project 与 command）
    command: 'data' 或 'areas'
    """
    try:
        env = os.environ.copy()
        base_path = os.path.dirname(os.path.abspath(__file__))  # 项目根
        env['PYTHONPATH'] = base_path

        result = subprocess.run(
            [sys.executable, '-u', '-m', 'core.main', command, project],
            capture_output=True,
            text=True,
            env=env,
            cwd=base_path,
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired as e:
        return f"脚本执行超时: {e}"
    except Exception as e:
        return str(e)
    
# ==========================================
# 3. 侧边栏：控制区
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/25/25694.png", width=50)
    st.header("控制面板")

    # 项目选择（住宅 / 仓储）
    project_map = {"住宅": "house", "仓储": "warehouse"}
    default_proj = os.environ.get('PROJECT_TYPE', 'house')
    default_label = '住宅' if default_proj == 'house' else '仓储'

    def _on_project_change():
        st.cache_data.clear()
        # 不直接修改与 selectbox 对应的 session_state（修改后可能导致 Streamlit 错误）
        # 我们使用基于项目的 selectbox key（例如 selected_date_house / selected_date_warehouse）来避免冲突
        # 仅清理缓存，组件会在下一次交互时依据当前项目自动显示正确的选项

    selected_label = st.radio(
        "🔁 切换数据视角",
        options=list(project_map.keys()),
        index=0 if default_label == '住宅' else 1,
        key='project_label',
        horizontal=True,
        on_change=_on_project_change
    )
    project = project_map[selected_label]

    # 更新数据：已改为自动定时更新（见仓库 Actions）。手动更新按钮已移除，避免在 UI 中直接触发抓取。
    st.info("🔁 已启用自动定时更新：每天 **07:00、12:00、20:00（CST / UTC+8）**，住宅与仓储均会更新；若需立即触发，请在本地或 CI 中运行 `python -m core.main data [house|warehouse]`。")

    st.divider()

    # 2. 数据加载（按项目）
    df_all = load_all_data(project)

    if df_all.empty:
        st.warning(f"⚠️ 暂无数据，请先更新数据或检查 data/{project}/total.json")
        st.stop()  # 停止后续渲染

    # 3. 日期选择器
    # 获取所有可用日期字符串列表（倒序）
    available_dates = df_all['日期'].dt.strftime('%Y-%m-%d').tolist()
    available_dates.reverse() # 最新的在前面
    
    # 使用基于项目的 key，避免不同项目共享同一个会话状态导致冲突
    selected_date_key = f"selected_date_{project}"

    # 在可选日期存在时创建 selectbox（确保 index 0 为最新日期）
    if available_dates:
        selected_date_str = st.selectbox(
            "📅 选择查看日期",
            available_dates,
            index=0,
            key=selected_date_key
        )
    else:
        st.warning(f"⚠️ 未找到日期数据，请先更新 data/{project}/total.json")
        st.stop()  # 停止后续渲染

    # 保证 selected_date_str 有值（以防 selectbox 返回空字符串）
    if not selected_date_str and available_dates:
        selected_date_str = available_dates[0]

    # 获取选中日期的数据行
    selected_row = df_all[df_all['日期'].dt.strftime('%Y-%m-%d') == selected_date_str].iloc[0]

    # 获取最新数据行（用于顶部大指标）
    latest_row = df_all.iloc[-1]

    st.info(f"当前显示: {selected_date_str}")
    st.caption("数据来源: 北京住建委")

# ==========================================
# 4. 主界面：核心指标
# ==========================================

st.markdown('<div class="main-title">星耀未来成交数据看板</div>', unsafe_allow_html=True)

# 顶部指标栏
col1, col2, col3, col4 = st.columns(4)

# 辅助函数：渲染漂亮的指标卡片
def render_metric(label, value, col):
    col.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

with col1:
    render_metric("累计签约套数", int(latest_row["已签约套数"]), st)
with col2:
    render_metric("累计签约面积 (㎡)", f"{latest_row['已签约面积(M2)']:,.1f}", st)
with col3:
    price_val = latest_row.get('成交均价(￥/M2)')
    if pd.isna(price_val):
        render_metric("累计成交均价", "N/A", st)
    else:
        render_metric("累计成交均价", f"¥{price_val:,.2f}", st)
with col4:
    # 先提取所有有当日均价的记录（已在前面的 load_all_data 中转为数值 + NaN 处理）
    valid_prices_df = df_all[
        pd.notna(df_all['均价(￥/M2)']) & 
        (df_all['均价(￥/M2)'] > 0)
    ].sort_values('日期').reset_index(drop=True)  # 按日期升序，便于找前后

    if valid_prices_df.empty:
        # 完全没有当日均价数据
        st.markdown(f"""
        <div class="metric-container">
            <div class="kpi-change none">—</div>
            <div class="metric-value">N/A</div>
            <div class="metric-label">当日均价</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 找到选中日期对应的行（如果有）
        selected_date = pd.to_datetime(selected_date_str)
        selected_valid_row = valid_prices_df[valid_prices_df['日期'] == selected_date]

        if not selected_valid_row.empty:
            # 选中日期本身有数据，直接使用
            current_row = selected_valid_row.iloc[0]
            current_date_str = selected_date_str
            is_substitute = False
        else:
            # 选中日期无数据：以数据集中**最新**的有记录日期为准（即始终以最新数据为基准）
            current_row = valid_prices_df.iloc[-1]    # 使用数据中最新的有记录日期
            current_date_str = current_row['日期'].strftime('%Y-%m-%d')
            is_substitute = True

        current_price = current_row['均价(￥/M2)']

        # 找到它的“前一个有记录的日期”（严格前一个）
        current_idx = valid_prices_df[valid_prices_df['日期'] == current_row['日期']].index[0]
        if current_idx > 0:
            prev_row = valid_prices_df.iloc[current_idx - 1]
            prev_price = prev_row['均价(￥/M2)']
            change_pct = (current_price - prev_price) / prev_price * 100
            change_str = f"{'↑' if change_pct > 0 else '↓'} {abs(change_pct):.1f}%"
            change_class = "up" if change_pct > 0 else "down"
        else:
            change_str = "—"
            change_class = "none"

        # 标签文字
        if not is_substitute:
            label_text = f"{selected_date_str} 当日均价"
        else:
            label_text = f"最新均价({current_date_str})"

        current_price_display = f"¥{current_price:,.2f}" if not pd.isna(current_price) else "N/A"

        st.markdown(f"""
        <div class="metric-container">
            <div class="kpi-change {change_class}">{change_str}</div>
            <div class="metric-value">{current_price_display}</div>
            <div class="metric-label">{label_text}</div>
        </div>
        """, unsafe_allow_html=True) 

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 5. 主界面：具体成交明细 & 趋势图
# ==========================================

col_detail, col_chart = st.columns([4, 6])

# 左侧：成交明细列表
with col_detail:
    # 将成交明细渲染为卡片样式，整体更美观
    price = selected_row.get('均价(￥/M2)', 0)
    if price == 0 or pd.isna(price):
        # 当天无成交：在卡片内显示空状态并在卡片下方（视觉上为卡片内）放置跳转按钮
        if not valid_prices_df.empty:
            latest_valid_date_str = valid_prices_df.iloc[-1]['日期'].strftime('%Y-%m-%d')
            def _goto_latest():
                st.session_state[selected_date_key] = latest_valid_date_str

            card_html = textwrap.dedent(f"""
<div class="detail-card">
  <div class="card-header">
    <div class="card-title">{selected_date_str} 成交明细</div>
  </div>
  <div class="card-body">
    <div class="detail-empty">当天暂无成交记录。</div>
  </div>
</div>
""").strip()
            st.markdown(card_html, unsafe_allow_html=True)

            st.button("跳转至最新成交", on_click=_goto_latest)
        else:
            # 全部数据都没有的兜底信息，仍然放在卡片内提醒用户
            card_html = textwrap.dedent(f"""
<div class="detail-card">
  <div class="card-header">
    <div class="card-title">{selected_date_str} 成交明细</div>
  </div>
  <div class="card-body">
    <div class="detail-empty">暂无数据，请先更新或检查 data/total.json</div>
  </div>
</div>
""").strip()
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        house_data = selected_row.get('成交户号', [])
        if house_data and isinstance(house_data, list) and len(house_data) > 0:
            # 将所有条目拼接为一个 HTML 块再一次性渲染，确保子元素在卡片内部
            items_html = ""
            for house in house_data:
                b_name = house.get('building_name', '')
                h_no = house.get('house_no', '')
                area = house.get('area', 0)

                if b_name and h_no:
                    display_b_name = b_name.replace('#住宅楼', '').replace('5-', '')
                    full_house_no = f"{display_b_name}#{h_no}"
                else:
                    full_house_no = f"{b_name} {h_no}".strip()

                if not full_house_no:
                    full_house_no = "未知房号"

                # 转义用户数据，防止注入或标签未闭合导致页面异常显示
                safe_full_house_no = html.escape(full_house_no)
                safe_area = html.escape(str(area))

                # 计算总价（建筑面积 * 当日均价），当 area 或 当日均价 无效时显示 N/A
                try:
                    area_val = float(area)
                except Exception:
                    area_val = None

                if price and not pd.isna(price) and area_val and area_val > 0:
                    total_price = area_val * price
                    price_str = f"¥{total_price:,.2f}"
                else:
                    price_str = "N/A"

                safe_price_str = html.escape(price_str)

                items_html += f"""
<div class="house-card">
  <div class="house-info">
    <div class="house-no">{safe_full_house_no}</div>
    <div class="house-area">
      <span>建筑面积: <b>{safe_area} ㎡</b></span>
    </div>
  </div>
  <div class="house-price">{safe_price_str}</div>
</div>
"""

            # 去除每行的缩进，避免被 Markdown 识别为代码块
            items_html = textwrap.dedent(items_html).strip()

            # 一次性渲染卡片及其内部内容，避免 Streamlit 将子块分离到不同容器中
            card_html = textwrap.dedent(f"""
<div class="detail-card">
  <div class="card-header">
    <div class="card-title">{selected_date_str} 成交明细</div>
  </div>
  <div class="card-body">
{items_html}
  </div>
</div>
""").strip()
            st.markdown(card_html, unsafe_allow_html=True)

            # 将跳转按钮也渲染（视觉上位于卡片内部右下方）
            # latest_valid_date_str = valid_prices_df.iloc[-1]['日期'].strftime('%Y-%m-%d') if not valid_prices_df.empty else None
            # def _goto_latest():
            #     if latest_valid_date_str:
            #         st.session_state['selected_date'] = latest_valid_date_str

            # st.button("跳转至最新成交", on_click=_goto_latest)
        else:
            # 当天有均价但无具体户号信息：若存在面积或总价，则以与其他成交卡片相同的格式显示一条合成记录，
            # 仅将户号替换为占位文本（默认：“无户号”），否则显示空状态
            area_val = selected_row.get('面积(M2)')
            total_val = selected_row.get('总价(￥)')
            avg_val = selected_row.get('均价(￥/M2)')

            has_area_or_total = ((area_val is not None and not pd.isna(area_val) and str(area_val) != "") or
                                 (total_val is not None and not pd.isna(total_val) and str(total_val) != ""))

            if has_area_or_total:
                # 构造一条合成记录，保持与实际户号项完全一致的渲染逻辑（只是替换户号文本）
                placeholder = "无户号"
                fake_house = {
                    'building_name': '',
                    'house_no': placeholder,
                    'area': area_val if area_val is not None and not pd.isna(area_val) and str(area_val) != "" else 0
                }

                # 按原有单条 house 渲染逻辑构建 HTML
                b_name = fake_house.get('building_name', '')
                h_no = fake_house.get('house_no', '')
                area = fake_house.get('area', 0)

                if b_name and h_no:
                    display_b_name = b_name.replace('#住宅楼', '').replace('5-', '')
                    full_house_no = f"{display_b_name}#{h_no}"
                else:
                    full_house_no = f"{b_name} {h_no}".strip()

                if not full_house_no:
                    full_house_no = "未知房号"

                safe_full_house_no = html.escape(full_house_no)
                safe_area = html.escape(str(area))

                try:
                    area_val_f = float(area)
                except Exception:
                    area_val_f = None

                # 优先使用面积*当日均价计算总价，若不可用则使用 provided total_val
                if price and not pd.isna(price) and area_val_f and area_val_f > 0:
                    total_price = area_val_f * price
                    price_str = f"¥{total_price:,.2f}"
                else:
                    try:
                        if total_val is not None and not pd.isna(total_val) and str(total_val) != "":
                            price_str = f"¥{float(total_val):,.2f}"
                        else:
                            price_str = "N/A"
                    except Exception:
                        price_str = "N/A"

                safe_price_str = html.escape(price_str)

                items_html = f"""
<div class="house-card">
  <div class="house-info">
    <div class="house-no">{safe_full_house_no}</div>
    <div class="house-area">
      <span>建筑面积: <b>{safe_area} ㎡</b></span>
    </div>
  </div>
  <div class="house-price">{safe_price_str}</div>
</div>
"""
                items_html = textwrap.dedent(items_html).strip()

                card_html = textwrap.dedent(f"""
<div class="detail-card">
  <div class="card-header">
    <div class="card-title">{selected_date_str} 成交明细</div>
  </div>
  <div class="card-body">
{items_html}
  </div>
</div>
""").strip()
                st.markdown(card_html, unsafe_allow_html=True)
            else:
                # 仍然显示空状态
                card_html = textwrap.dedent(f"""
<div class="detail-card">
  <div class="card-header">
    <div class="card-title">{selected_date_str} 成交明细</div>
  </div>
  <div class="card-body">
    <div class="detail-empty">当天暂无具体的成交户号记录。</div>
  </div>
</div>
""").strip()
                st.markdown(card_html, unsafe_allow_html=True)

# 右侧：价格走势图表
with col_chart:
    # 按照当前图表显示的“起始坐标”（即每条曲线自身的最小值 - 小缓冲）作为基线，保持无控件、始终启用渐变，每条曲线单独一个面积
    # 小工具：将 HEX 转为 RGB
    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    # 小工具：在给定基线下构造平滑渐变（通过较多层的细微 alpha 插值近似线性渐变）
    # 说明：Plotly 原生不支持直接对单个 fill 使用线性渐变，因此使用多层细分近似，视觉上更接近连续渐变且无明显带状分层感
    def add_gradient_fill_between_baseline(fig, x, y, hex_color, baseline, legendgroup=None, n_layers=40, alpha_min=0.005, alpha_max=0.26):
        r, g, b = hex_to_rgb(hex_color)
        # 添加基线 trace（透明，不显示在图例），同时设置 legendgroup 以便与线条联动
        fig.add_trace(go.Scatter(
            x=x, y=[baseline] * len(x),
            mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip', legendgroup=legendgroup
        ))
        # 使用 n_layers 层平滑插值，alpha 从 alpha_min 线性增长到 alpha_max
        if n_layers < 2:
            n_layers = 2
        for i in range(n_layers):
            frac = (i + 1) / float(n_layers)
            alpha = float(alpha_min + (alpha_max - alpha_min) * (i / float(n_layers - 1)))
            y_frac = baseline + (y - baseline) * frac
            fig.add_trace(go.Scatter(
                x=x, y=y_frac,
                mode='lines', line=dict(width=0), fill='tonexty',
                fillcolor=f'rgba({r},{g},{b},{alpha})', hoverinfo='skip', showlegend=False, legendgroup=legendgroup
            ))

    # 构建图表（我们先为每条曲线添加渐变填充，再添加对应的线条，保证线条在最上层）
    fig = go.Figure()

    x = df_all['日期']
    y_primary = df_all['成交均价(￥/M2)']
    y_secondary = df_all['均价(￥/M2)']

    # 使用全局基线：取两条曲线的最小值并减去 5% 缓冲，保证两条曲线的面积都从相同的“图表底部”开始
    combined_min = pd.concat([y_primary.dropna(), y_secondary.dropna()]) if (not y_primary.dropna().empty or not y_secondary.dropna().empty) else pd.Series([])
    if not combined_min.empty:
        combined_min_val = float(combined_min.min())
        combined_max_val = float(combined_min.max())
        r = (combined_max_val - combined_min_val) if (combined_max_val - combined_min_val) != 0 else max(abs(combined_min_val) * 0.02, 1.0)
        baseline_common = float(combined_min_val - r * 0.05)
    else:
        baseline_common = 0.0

    # 为每条曲线添加渐变面积（各自独立地基于相同的 baseline），使用较低的 alpha 以保持数据可读性
    if not y_primary.dropna().empty:
        # 使用连续近似渐变：40 层默认，alpha 从 0.005 至 0.26
        add_gradient_fill_between_baseline(fig, x, y_primary, COLOR_PRIMARY, baseline=baseline_common, legendgroup='累计均价', n_layers=40, alpha_min=0.005, alpha_max=0.26)
    if not y_secondary.dropna().empty:
        # 使用连续近似渐变：40 层默认，alpha 从 0.005 至 0.22
        add_gradient_fill_between_baseline(fig, x, y_secondary, COLOR_SECONDARY, baseline=baseline_common, legendgroup='当日均价', n_layers=40, alpha_min=0.005, alpha_max=0.22)

    # 累计均价线 - 青蓝色（置于渐变之上）
    fig.add_trace(go.Scatter(
        x=x, y=y_primary,
        mode='lines+markers', name='累计均价', legendgroup='累计均价',
        line=dict(width=3, color=COLOR_PRIMARY, shape='spline'),
        marker=dict(size=6, color='white', line=dict(width=2, color=COLOR_PRIMARY)),
        hovertemplate="累计均价: ¥%{y:,.2f}<extra></extra>"
    ))

    # 当日均价线 - 橙黄色（置于渐变之上）
    fig.add_trace(go.Scatter(
        x=x, y=y_secondary,
        mode='lines+markers', name='当日均价', legendgroup='当日均价',
        line=dict(width=3, color=COLOR_SECONDARY, shape='spline'),
        marker=dict(size=6, color='white', line=dict(width=2, color=COLOR_SECONDARY)),
        connectgaps=True,
        hovertemplate="当日均价: ¥%{y:,.2f}<extra></extra>"
    ))

    # 选中日期的高亮圈
    fig.add_trace(go.Scatter(
        x=[selected_row['日期']], y=[selected_row['成交均价(￥/M2)']],
        mode='markers', showlegend=False, legendgroup='累计均价',
        marker=dict(size=14, color=COLOR_PRIMARY, opacity=0.3, line=dict(width=2, color=COLOR_PRIMARY)),
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=[selected_row['日期']], y=[selected_row['均价(￥/M2)']],
        mode='markers', showlegend=False, legendgroup='当日均价',
        marker=dict(size=14, color=COLOR_SECONDARY, opacity=0.3, line=dict(width=2, color=COLOR_SECONDARY)),
        hoverinfo='skip'
    ))

    # 添加虚线（选中日期的垂直参考线）
    fig.add_trace(go.Scatter(
        x=[selected_row['日期'], selected_row['日期']], 
        y=[min(df_all['成交均价(￥/M2)'].min(), df_all['均价(￥/M2)'].min()), max(df_all['成交均价(￥/M2)'].max(), df_all['均价(￥/M2)'].max())], 
        mode='lines', 
        showlegend=False, 
        line=dict(color='lightgray', dash='dot', width=1.5),  # 使用点状虚线，颜色更柔和，宽度较细
        hoverinfo='skip'
    ))

    fig.update_layout(
        height=500,  # 提高图表高度避免被裁切
        margin=dict(l=40, r=20, t=18, b=100),  # 增加底部外边距以保证 x 轴标签完全可见
        hovermode="x unified",
        hoverlabel=dict(bgcolor='white', font_size=12, font_family="PingFang SC, Microsoft YaHei, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            tickformat="%Y-%m-%d",
            linecolor='#e2e8f0',
            showline=True,
            showticklabels=True,
            ticks='outside',
            tickangle=-45,
            tickfont=dict(color='#475569', size=11),
            automargin=True
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f1f5f9',
            tickformat=",.0f",
            showline=True,
            linecolor='#e2e8f0',
            showticklabels=True,
            tickfont=dict(color='#475569', size=11),
            automargin=True
        )
    )

    # 嵌入图表到与成交明细一致的卡片中（使用内联样式以便在 iframe 中正确显示）
    fig_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    # 包一层容器并加上小的 CSS reset，确保没有 body margin 导致溢出
    wrapped_fig = textwrap.dedent(f"""
<style>html,body{{margin:0;padding:0;background:transparent;}} .modebar, .plotly .modebar, .js-plotly-plot .modebar{{display:none !important;}} </style>
<div style="background: white; border-radius: 14px; padding: 1rem; box-shadow: 0 8px 30px rgba(15,23,42,0.06); border: 1px solid transparent; margin-bottom: 1rem; height: 580px; box-sizing: border-box; position: relative; overflow: hidden;">
  <div style="position:absolute; top:0; left:0; width:100%; height:6px; background: linear-gradient(90deg, #f28e52 0%, #ffb380 100%); border-top-left-radius:14px; border-top-right-radius:14px;"></div>
  <div style="display:flex; align-items:center; height:56px; padding-left:6px;">
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a;">价格趋势</div>
  </div>
  <!-- 与成交明细一致的浅色分隔线 -->
  <div style="border-bottom:1px solid #f1f5f9; margin: 0 8px 12px 8px; border-radius:4px;"></div>
  <div style="height: calc(100% - 56px); overflow:visible; padding-right:6px; padding-left:6px; padding-bottom:96px;">
    <div style="width:100%; height:100%; box-sizing:border-box;">
{fig_html}
    </div>
  </div>
</div>
""").strip()

    # 禁用 components 的 iframe 滚动，让 iframe 尺寸由 height 决定（我们已微调图高度）
    components.html(wrapped_fig, height=580, scrolling=False)
    
# ==========================================
# 6. 页脚
# ==========================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #95a5a6; font-size: 0.8rem;'>"
    f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | © Star Future Data View"
    "</div>", 
    unsafe_allow_html=True
)