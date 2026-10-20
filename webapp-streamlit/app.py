"""
Thailand Green Energy & EV Site Selection Planner
Streamlit Web Application - Harmonious VoltAgent Dual Theme (Light & Dark)
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from business_engine import calculate_business_scores

# 1. Page Configuration (Full width, no sidebar)
st.set_page_config(
    page_title="Thailand Green Energy & EV Planner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Session State Initialization
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"  # Default: Dark mode (VoltAgent Theme)

if "business_mode" not in st.session_state:
    st.session_state["business_mode"] = "EV"  # 'EV' or 'SOLAR'

if "cluster_filter" not in st.session_state:
    st.session_state["cluster_filter"] = "ALL"  # 'ALL', '2', '1', '0'

if "show_table_tools" not in st.session_state:
    st.session_state["show_table_tools"] = True

if "table_full_view" not in st.session_state:
    st.session_state["table_full_view"] = False

is_dark = st.session_state["theme_mode"] == "dark"
is_ev_mode = st.session_state["business_mode"] == "EV"
active_filter = st.session_state["cluster_filter"]
show_tools = st.session_state["show_table_tools"]

# Theme Tokens
if is_dark:
    bg_app = "#090a0f"
    bg_card = "#11141c"
    bg_card_inner = "#171b26"
    border_color = "#1f2637"
    text_main = "#f8fafc"
    text_sub = "#94a3b8"
    text_muted = "#64748b"
    btn_sec_bg = "#161b26"
    btn_sec_text = "#cbd5e1"
    btn_sec_border = "#262f42"
    plotly_grid = "#1c2230"
    radar_nat_color = "#64748b"
    radar_nat_fill = "rgba(100, 116, 139, 0.2)"
else:
    bg_app = "#f8fafc"
    bg_card = "#ffffff"
    bg_card_inner = "#f1f5f9"
    border_color = "#e2e8f0"
    text_main = "#0f172a"
    text_sub = "#334155"
    text_muted = "#64748b"
    btn_sec_bg = "#ffffff"
    btn_sec_text = "#334155"
    btn_sec_border = "#cbd5e1"
    plotly_grid = "#e2e8f0"
    radar_nat_color = "#94a3b8"
    radar_nat_fill = "rgba(148, 163, 184, 0.2)"

# Dynamic Theme CSS (Covers: App, Metrics, Buttons, Table, Dropdowns & Popovers)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Kanit', sans-serif;
    }}

    /* Hide Sidebar Completely */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* Streamlit Top Header Bar (Fix: Make top bar black in Dark Mode) */
    header[data-testid="stHeader"],
    .stApp > header,
    div[data-testid="stHeader"] {{
        background-color: {bg_app} !important;
        background: {bg_app} !important;
        color: {text_main} !important;
    }}

    header[data-testid="stHeader"] svg,
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] a,
    header[data-testid="stHeader"] span {{
        color: {text_main} !important;
        fill: {text_main} !important;
    }}

    header[data-testid="stHeader"] button:hover {{
        background-color: {'#1d2433' if is_dark else '#e2e8f0'} !important;
    }}

    /* Top Decoration Gradient Line */
    div[data-testid="stDecoration"] {{
        background: linear-gradient(90deg, #10b981, #059669) !important;
        height: 3px !important;
    }}

    /* Global App Background & Text */
    .stApp {{
        background-color: {bg_app} !important;
        color: {text_main} !important;
    }}

    /* All Headings & Paragraphs */
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {text_main} !important;
    }}

    /* Metric Cards */
    div[data-testid="stMetric"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        border-radius: 14px !important;
        padding: 12px 14px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
    }}

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] > div,
    div[data-testid="stMetricLabel"] p {{
        color: {text_muted} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: nowrap !important;
    }}

    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] > div {{
        color: {text_main} !important;
        font-family: 'JetBrains Mono', 'Prompt', monospace !important;
        font-weight: 700 !important;
        font-size: 20px !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: nowrap !important;
        letter-spacing: -0.3px !important;
    }}

    div[data-testid="stMetricDelta"] {{
        color: #10b981 !important;
        font-weight: 600 !important;
    }}

    /* Override Primary Buttons: ALWAYS Emerald Green (NEVER Red) */
    button[kind="primary"], .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: 1px solid #10b981 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3) !important;
    }}

    /* Secondary Buttons */
    button[kind="secondary"], .stButton>button[kind="secondary"] {{
        background-color: {btn_sec_bg} !important;
        color: {btn_sec_text} !important;
        border: 1px solid {btn_sec_border} !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }}

    button[kind="secondary"]:hover, .stButton>button[kind="secondary"]:hover {{
        border-color: #10b981 !important;
        color: #10b981 !important;
    }}

    /* Download Button - Positioned clearly below table without overlapping */
    div.st-key-btn_download_full_report,
    div[data-testid="stElementContainer"]:has(div[data-testid="stDownloadButton"]),
    div[data-testid="stDownloadButton"] {{
        margin-top: 20px !important;
        margin-bottom: 24px !important;
        clear: both !important;
        display: block !important;
        position: relative !important;
        z-index: 10 !important;
        width: 100% !important;
    }}

    div[data-testid="stDownloadButton"]>button {{
        background-color: rgba(16, 185, 129, 0.12) !important;
        color: #10b981 !important;
        border: 1px solid rgba(16, 185, 129, 0.35) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }}

    div[data-testid="stDownloadButton"]>button:hover {{
        background-color: #10b981 !important;
        color: #ffffff !important;
    }}

    /* Input Box */
    input, .stTextInput>div>div>input {{
        background-color: {bg_card} !important;
        color: {text_main} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
    }}

    input::placeholder {{
        color: {text_muted} !important;
    }}

    /* Selectbox Widget */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] label p {{
        color: {text_main} !important;
        font-weight: 600 !important;
    }}

    div[data-baseweb="select"] {{
        background-color: transparent !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        color: {text_main} !important;
    }}

    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span {{
        color: {text_main} !important;
    }}

    div[data-baseweb="select"] input {{
        color: {text_main} !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    div[data-baseweb="select"] svg {{
        fill: {text_sub} !important;
        color: {text_sub} !important;
    }}

    /* Dropdown Popover & Menu Items (Full width, dark in dark mode) */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > ul,
    ul[role="listbox"],
    div[role="listbox"],
    div[data-testid="stSelectboxVirtualDropdown"] {{
        background-color: {bg_card} !important;
        color: {text_main} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    }}

    ul[role="listbox"] li,
    li[role="option"],
    div[role="option"],
    [data-baseweb="menu-item"] {{
        background-color: {bg_card} !important;
        color: {text_main} !important;
        padding: 9px 14px !important;
        font-size: 14px !important;
        white-space: normal !important;
        word-break: break-word !important;
        border-bottom: 1px solid {border_color} !important;
    }}

    ul[role="listbox"] li:hover,
    li[role="option"]:hover,
    div[role="option"]:hover,
    [data-baseweb="menu-item"]:hover,
    li[role="option"][aria-selected="true"],
    li[data-highlighted="true"] {{
        background-color: {'#1d2433' if is_dark else '#e2e8f0'} !important;
        color: #10b981 !important;
    }}

    ul[role="listbox"] li *,
    li[role="option"] *,
    div[role="option"] * {{
        color: inherit !important;
    }}

    /* Columns Relative Anchor (So absolute children stay inside their respective column) */
    div[data-testid="stColumn"],
    div[data-testid="column"],
    [data-testid="stColumn"],
    [data-testid="column"] {{
        position: relative !important;
    }}

    /* Table Container Styling - Keep native height so download button never overlaps */
    div.st-key-main_ranking_table {{
        margin-bottom: 14px !important;
        clear: both !important;
        display: block !important;
    }}

    /* Fullscreen Wrapper & Plotly Fullscreen Dark Mode Background (without overriding table height) */
    div[data-testid="stFullScreenFrame"],
    div[data-testid="stFullScreenFrame"]:fullscreen,
    div[data-testid="stPlotlyChart"],
    div[data-testid="stPlotlyChart"]:fullscreen,
    .js-plotly-plot:fullscreen,
    .plotly:fullscreen,
    :fullscreen,
    ::backdrop {{
        background: {bg_card} !important;
        background-color: {bg_card} !important;
    }}

    div[data-testid="stDataFrame"] {{
        border-radius: 10px !important;
        border: 1px solid {border_color} !important;
        width: 100% !important;
    }}

    /* Target the resizable table grid for dark mode inversion without touching internal canvas DOM */
    div[data-testid="stDataFrameResizable"] {{
        {'filter: invert(0.92) hue-rotate(180deg) brightness(0.95) contrast(1.05) !important;' if is_dark else 'filter: none !important;'}
        border-radius: 8px !important;
        width: 100% !important;
    }}

    /* Table Quick Tool Button under Toggle Switch */
    div.st-key-btn_open_full_table,
    div.st-key-btn_open_full_table button {{
        width: 100% !important;
        font-size: 13px !important;
        padding: 5px 12px !important;
        height: 36px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        margin-top: 4px !important;
    }}

    /* Dialog Top CSV Button */
    div.st-key-btn_dlg_download {{
        margin-top: 0px !important;
        margin-bottom: 8px !important;
    }}

    div.st-key-btn_dlg_download button {{
        height: 36px !important;
        padding: 4px 12px !important;
        font-size: 13px !important;
    }}

    /* Main Menu 3-Dots Popover (Fix: Make 3-dots dropdown menu dark in dark mode) */
    div[data-testid="stMainMenuPopover"],
    .stMainMenuPopover,
    div[data-testid="stMainMenuPopover"] > div,
    ul[data-testid="stMainMenuList"] {{
        background: {bg_card} !important;
        background-color: {bg_card} !important;
        color: {text_main} !important;
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    }}

    div[data-testid="stMainMenuPopover"] li,
    div[data-testid="stMainMenuPopover"] [role="menuitem"],
    div[data-testid="stMainMenuPopover"] div[data-testid="stMainMenuItemLabel"],
    div[data-testid="stMainMenuPopover"] span,
    div[data-testid="stMainMenuPopover"] p {{
        background-color: transparent !important;
        color: {text_main} !important;
    }}

    div[data-testid="stMainMenuPopover"] li:hover,
    div[data-testid="stMainMenuPopover"] [role="menuitem"]:hover {{
        background-color: {'#1d2433' if is_dark else '#e2e8f0'} !important;
        color: #10b981 !important;
    }}

    div[data-testid="stMainMenuPopover"] hr,
    div[data-testid="stMainMenuDivider"] {{
        border-color: {border_color} !important;
    }}

    /* Modal Dialog (st.dialog) Dark Theme Styling - Covers stDialog wrapper, inner card, header, and close button */
    div[data-testid="stDialog"] > div,
    .stDialog > div,
    div[role="dialog"],
    .react-aria-Dialog,
    div[data-testid="stModal"],
    div[data-baseweb="modal"],
    div[data-baseweb="modal"] > div {{
        background: {bg_card} !important;
        background-color: {bg_card} !important;
        color: {text_main} !important;
        border-radius: 16px !important;
        border: 1px solid {border_color} !important;
    }}

    div[data-testid="stDialog"] [slot="title"],
    div[role="dialog"] [slot="title"],
    div[role="dialog"] [data-testid="stModalHeader"],
    div[role="dialog"] h1,
    div[role="dialog"] h2,
    div[role="dialog"] h3,
    div[role="dialog"] p,
    div[role="dialog"] span,
    div[role="dialog"] label {{
        color: {text_main} !important;
    }}

    div[data-testid="stDialog"] button[aria-label="Close"],
    div[role="dialog"] button[aria-label="Close"] {{
        color: {text_main} !important;
        background-color: {'#1d2433' if is_dark else '#f1f5f9'} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
    }}

    div[data-testid="stDialog"] button[aria-label="Close"]:hover,
    div[role="dialog"] button[aria-label="Close"]:hover {{
        border-color: #10b981 !important;
        color: #10b981 !important;
    }}

    div[data-testid="stDialog"] button[aria-label="Close"] svg,
    div[role="dialog"] button[aria-label="Close"] svg,
    div[role="dialog"] button[aria-label="Close"] path {{
        fill: {text_main} !important;
        stroke: {text_main} !important;
        color: {text_main} !important;
    }}

    /* Hide Streamlit's Internal Floating Toolbar Completely */
    div[data-testid="stElementToolbar"],
    .stElementToolbar,
    div[data-testid="stElementToolbarButtonContainer"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}

    /* Tooltip Popover (Fix: BaseWeb Tooltip - Crisp Dark Bubble, White Text) */
    div[data-baseweb="tooltip"],
    div[data-baseweb="tooltip"] > div,
    div[role="tooltip"],
    div[role="tooltip"] > div,
    [data-testid="stTooltipContent"] {{
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        filter: none !important;
    }}

    div[data-baseweb="tooltip"] *,
    div[role="tooltip"] *,
    [data-testid="stTooltipContent"] * {{
        color: #ffffff !important;
        background-color: transparent !important;
    }}

    /* Fullscreen Plotly Charts */
    :fullscreen,
    ::backdrop {{
        background-color: {bg_app} !important;
        background: {bg_app} !important;
        color: {text_main} !important;
    }}

    /* Alerts (st.success, st.info) */
    div[data-testid="stAlert"] {{
        background-color: {'#111a1f' if is_dark else '#f0fdf4'} !important;
        border: 1px solid {'#1f3a33' if is_dark else '#bbf7d0'} !important;
        border-radius: 8px !important;
    }}

    div[data-testid="stAlert"] * {{
        color: {text_main} !important;
    }}

    /* Slider styling */
    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] div[data-testid="stWidgetLabel"] p {{
        color: {text_main} !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background-color: {bg_card};
        padding: 4px;
        border-radius: 10px;
        border: 1px solid {border_color};
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px;
        padding: 6px 14px;
        color: {text_sub};
        font-weight: 500;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #10b981 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }}
</style>
""", unsafe_allow_html=True)

# 3. Load Dataset (77 rows - computed dynamically without stale cache)
st.cache_data.clear()

def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, "clustered_provinces_2563.csv")
    if not os.path.exists(csv_file):
        csv_file = os.path.join(base_dir, "..", "Datasets-20261018T071705Z-1-001", "Datasets", "code-ผล", "clustered_provinces_2563.csv")
    
    df = pd.read_csv(csv_file)
    return calculate_business_scores(df)

df_all = load_data()

# 4. Top Header (Logo + Title on Left | Business Mode & Theme Switch on Right)
col_hdr_left, col_hdr_right = st.columns([6, 6])

with col_hdr_left:
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; padding:4px 0;">
            <div style="width:44px; height:44px; border-radius:12px; background:linear-gradient(135deg, #10b981 0%, #059669 100%); display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(16,185,129,0.35); flex-shrink:0;">
                <span style="font-size:22px; color:#ffffff;">⚡</span>
            </div>
            <div>
                <h2 style="margin:0; font-size:20px; font-weight:700; color:{text_main}; line-height:1.2;">Thailand Green Energy & EV Planner</h2>
                <p style="margin:2px 0 0 0; font-size:12px; color:{text_muted};">ระบบวางแผนธุรกิจพลังงานสะอาดและทำเลสถานีชาร์จจากผลลัพธ์ K-Means (77 จังหวัด)</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_hdr_right:
    col_b1, col_b2, col_th = st.columns([3, 3, 2.5])
    
    with col_b1:
        btn_ev_type = "primary" if is_ev_mode else "secondary"
        if st.button("⚡ สถานีชาร์จ EV", key="btn_ev", type=btn_ev_type, use_container_width=True):
            st.session_state["business_mode"] = "EV"
            st.rerun()
            
    with col_b2:
        btn_sol_type = "primary" if not is_ev_mode else "secondary"
        if st.button("☀️ โซลาร์รูฟท็อป", key="btn_sol", type=btn_sol_type, use_container_width=True):
            st.session_state["business_mode"] = "SOLAR"
            st.rerun()

    with col_th:
        th_label = "☀️ โหมดสว่าง" if is_dark else "🌙 โหมดมืด"
        if st.button(th_label, key="btn_theme_toggle", type="secondary", use_container_width=True):
            st.session_state["theme_mode"] = "light" if is_dark else "dark"
            st.rerun()

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# 5. Filter Data based on Active Cluster Filter
if active_filter == "ALL":
    df_filtered = df_all.copy()
else:
    df_filtered = df_all[df_all["CLUSTER_ID"] == int(active_filter)].copy()

if is_ev_mode:
    df_filtered = df_filtered.sort_values(by="EV_SCORE", ascending=False).reset_index(drop=True)
else:
    df_filtered = df_filtered.sort_values(by="SOLAR_SCORE", ascending=False).reset_index(drop=True)

# 6. 4 KPI Metrics Row
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    top_p = df_filtered.iloc[0] if len(df_filtered) > 0 else df_all.iloc[0]
    top_score = top_p["EV_SCORE"] if is_ev_mode else top_p["SOLAR_SCORE"]
    st.metric(
        label="🏆 จังหวัดอันดับ 1",
        value=f"{top_p['PROVINCE_CLEAN']} ({top_score:.1f})",
        delta="ทำเลทองอันดับ 1"
    )

with col_kpi2:
    avg_score = df_filtered["EV_SCORE"].mean() if is_ev_mode else df_filtered["SOLAR_SCORE"].mean()
    st.metric(
        label="📊 คะแนนเฉลี่ยกลุ่มที่เลือก",
        value=f"{avg_score:.1f} / 100",
        delta="มาตรฐานระดับประเทศ"
    )

with col_kpi3:
    tier1_cnt = (df_filtered["EV_SCORE"] >= 75).sum()
    st.metric(
        label="⭐ ทำเลทอง Tier 1 (>=75)",
        value=f"{tier1_cnt} จังหวัด",
        delta="ความคุ้มค่าสูง"
    )

with col_kpi4:
    c2_cnt = (df_all["CLUSTER_ID"] == 2).sum()
    st.metric(
        label="🏭 กลุ่มอุตสาหกรรม/มหานคร (C2)",
        value=f"{c2_cnt} จังหวัด",
        delta="ศูนย์กลางเศรษฐกิจ"
    )

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# 7. Modal Dialog for Full Table View (รูปแบบ A: ตารางจอใหญ่เต็มตา)
@st.dialog("📋 ตารางจัดอันดับความคุ้มค่า 77 จังหวัด (ฉบับเต็ม)", width="large")
def show_full_table_dialog():
    filter_opts = ["ทั้งหมด", "Cluster 2 (อุตสาหกรรม/มหานคร)", "Cluster 1 (ท่องเที่ยว/บริการ)", "Cluster 0 (เกษตรกรรม/ชนบท)"]
    default_f_idx = 0 if active_filter == "ALL" else (1 if active_filter == "2" else (2 if active_filter == "1" else 3))

    curr_dlg_search = st.session_state.get("dlg_table_search", "").strip()
    curr_dlg_filter = st.session_state.get("dlg_cluster_select", filter_opts[default_f_idx])

    # Pre-filter Data so Top CSV button always matches current filter
    dlg_df = df_all.copy()
    if "Cluster 2" in curr_dlg_filter:
        dlg_df = dlg_df[dlg_df["CLUSTER_ID"] == 2]
    elif "Cluster 1" in curr_dlg_filter:
        dlg_df = dlg_df[dlg_df["CLUSTER_ID"] == 1]
    elif "Cluster 0" in curr_dlg_filter:
        dlg_df = dlg_df[dlg_df["CLUSTER_ID"] == 0]

    if curr_dlg_search:
        dlg_df = dlg_df[dlg_df["PROVINCE_CLEAN"].str.contains(curr_dlg_search)]

    score_col = "EV_SCORE" if is_ev_mode else "SOLAR_SCORE"
    dlg_df = dlg_df.sort_values(by=score_col, ascending=False)

    # Top Header Bar: Subtitle on Left | CSV Download Button on Right (next to X close button)
    d_hdr_left, d_hdr_right = st.columns([7.2, 4.8])
    with d_hdr_left:
        st.markdown(
            f"<p style='color:{text_sub}; font-size:13px; margin:6px 0 0 0;'>"
            f"แสดงข้อมูลผลลัพธ์การจัดกลุ่มและการวิเคราะห์เจาะลึก (<b>{len(dlg_df)}</b> จาก 77 จังหวัด)</p>",
            unsafe_allow_html=True
        )
    with d_hdr_right:
        dlg_csv = dlg_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลตารางนี้ (CSV)",
            data=dlg_csv,
            file_name=f"thailand_green_energy_full_{'ev' if is_ev_mode else 'solar'}.csv",
            mime="text/csv",
            key="btn_dlg_download",
            use_container_width=True
        )

    # Dialog Filters
    d_c1, d_c2 = st.columns([7, 5])
    with d_c1:
        st.text_input("ค้นหาจังหวัด:", placeholder="🔍 พิมพ์ชื่อจังหวัด เช่น นนทบุรี, ระยอง, เชียงใหม่...", key="dlg_table_search", label_visibility="collapsed")
    with d_c2:
        st.selectbox("กรองกลุ่ม:", options=filter_opts, index=default_f_idx, key="dlg_cluster_select", label_visibility="collapsed")
    
    if is_ev_mode:
        dlg_cols = ["PROVINCE_CLEAN", "CLUSTER_ID", "EV_SCORE", "EV_TIER", "CHARGER_TECH", "TARGET_LOCATIONS"]
        dlg_rename = {
            "PROVINCE_CLEAN": "จังหวัด",
            "CLUSTER_ID": "กลุ่ม",
            "EV_SCORE": "คะแนน EV",
            "EV_TIER": "ระดับความพร้อม",
            "CHARGER_TECH": "หัวชาร์จแนะนำ",
            "TARGET_LOCATIONS": "ทำเลเป้าหมายหลัก"
        }
    else:
        dlg_cols = ["PROVINCE_CLEAN", "CLUSTER_ID", "SOLAR_SCORE", "SOLAR_PAYBACK_YEARS", "ELEC_PER_HOUSE", "SOLAR_REC"]
        dlg_rename = {
            "PROVINCE_CLEAN": "จังหวัด",
            "CLUSTER_ID": "กลุ่ม",
            "SOLAR_SCORE": "คะแนน Solar",
            "SOLAR_PAYBACK_YEARS": "คืนทุน (ปี)",
            "ELEC_PER_HOUSE": "ค่าไฟบ้าน (kWh)",
            "SOLAR_REC": "คำแนะนำการติดตั้ง"
        }
        
    view_df = dlg_df[[c for c in dlg_cols if c in dlg_df.columns]].rename(columns=dlg_rename)
    view_df.index = np.arange(1, len(view_df) + 1)
    
    st.dataframe(view_df, use_container_width=True, height=520, key="dialog_ranking_table")

# 8. Main 2-Column Section (Table on Left, Deep Dive & Charts on Right)
col_left, col_right = st.columns([5, 7])

# ---------- LEFT COLUMN: Table & Cluster Filter Pills ----------
with col_left:
    curr_search = st.session_state.get("table_search_input", "").strip()
    if curr_search:
        df_display = df_filtered[df_filtered["PROVINCE_CLEAN"].str.contains(curr_search)]
    else:
        df_display = df_filtered

    c_tbl_title, c_tbl_toggle = st.columns([6.2, 3.8])
    with c_tbl_title:
        st.markdown(f"<h3 style='margin:0 0 2px 0; font-size:16px; font-weight:700;'>📋 ตารางจัดอันดับความคุ้มค่า 77 จังหวัด</h3>", unsafe_allow_html=True)
        st.caption(f"แสดง {len(df_display)} จาก 77 จังหวัด")
    with c_tbl_toggle:
        if st.button("⛶ ดูตารางเต็มจอ", key="btn_open_full_table", use_container_width=True, help="เปิดดูข้อมูลทั้งหมด 77 จังหวัดแบบกว้างเต็มหน้าจอ"):
            show_full_table_dialog()

    # Search Box
    search_query = st.text_input("ค้นหาชื่อจังหวัด:", placeholder="🔍 ค้นหา เช่น นนทบุรี, ระยอง, เชียงใหม่...", label_visibility="collapsed", key="table_search_input")

    # Cluster Filter Horizontal Pills
    c_lbl, c_all, c_c2, c_c1, c_c0 = st.columns([1.1, 1.6, 2.3, 2.3, 2.2])
    with c_lbl:
        st.markdown(f"<div style='padding-top:6px; font-size:12px; color:{text_muted};'>กลุ่ม:</div>", unsafe_allow_html=True)
    with c_all:
        if st.button("ทั้งหมด", key="btn_f_all", type="primary" if active_filter == "ALL" else "secondary", use_container_width=True):
            st.session_state["cluster_filter"] = "ALL"
            st.rerun()
    with c_c2:
        if st.button("C2 (อุตสาหกรรม)", key="btn_f_c2", type="primary" if active_filter == "2" else "secondary", use_container_width=True):
            st.session_state["cluster_filter"] = "2"
            st.rerun()
    with c_c1:
        if st.button("C1 (ท่องเที่ยว)", key="btn_f_c1", type="primary" if active_filter == "1" else "secondary", use_container_width=True):
            st.session_state["cluster_filter"] = "1"
            st.rerun()
    with c_c0:
        if st.button("C0 (เกษตร)", key="btn_f_c0", type="primary" if active_filter == "0" else "secondary", use_container_width=True):
            st.session_state["cluster_filter"] = "0"
            st.rerun()

    # Table View
    if is_ev_mode:
        show_cols = ["PROVINCE_CLEAN", "CLUSTER_ID", "EV_SCORE", "EV_TIER", "CHARGER_TECH"]
        rename_dict = {
            "PROVINCE_CLEAN": "จังหวัด",
            "CLUSTER_ID": "กลุ่ม",
            "EV_SCORE": "คะแนน",
            "EV_TIER": "ระดับความพร้อม",
            "CHARGER_TECH": "หัวชาร์จแนะนำ"
        }
    else:
        show_cols = ["PROVINCE_CLEAN", "CLUSTER_ID", "SOLAR_SCORE", "SOLAR_PAYBACK_YEARS", "ELEC_PER_HOUSE"]
        rename_dict = {
            "PROVINCE_CLEAN": "จังหวัด",
            "CLUSTER_ID": "กลุ่ม",
            "SOLAR_SCORE": "คะแนน",
            "SOLAR_PAYBACK_YEARS": "คืนทุน (ปี)",
            "ELEC_PER_HOUSE": "ค่าไฟบ้าน (kWh)"
        }

    table_df = df_display[show_cols].rename(columns=rename_dict)
    table_df.index = np.arange(1, len(table_df) + 1)
    st.dataframe(table_df, use_container_width=True, height=480, key="main_ranking_table")

    st.markdown("<div style='height: 24px; clear: both; display: block;'></div>", unsafe_allow_html=True)

    # Download CSV
    csv_data = df_display.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดรายงานฉบับเต็ม (CSV)",
        data=csv_data,
        file_name=f"thailand_green_energy_ranking_{'ev' if is_ev_mode else 'solar'}.csv",
        mime="text/csv",
        key="btn_download_full_report",
        use_container_width=True
    )

# ---------- RIGHT COLUMN: Deep Dive & Details ----------
with col_right:
    prov_list = df_all["PROVINCE_CLEAN"].tolist()
    default_idx = prov_list.index("นนทบุรี") if "นนทบุรี" in prov_list else 0
    selected_prov = st.selectbox("เลือกจังหวัดที่ต้องการวิเคราะห์เจาะลึก:", prov_list, index=default_idx)
    
    prov_row = df_all[df_all["PROVINCE_CLEAN"] == selected_prov].iloc[0]
    score_val = prov_row["EV_SCORE"] if is_ev_mode else prov_row["SOLAR_SCORE"]

    # Header Card with Selected Province Details
    c_p_info, c_p_score = st.columns([8, 4])
    with c_p_info:
        st.markdown(f"<h3 style='margin:0; font-size:20px; font-weight:700;'>📍 {prov_row['CC-DESC']} ({prov_row['PROVINCE_CLEAN']})</h3>", unsafe_allow_html=True)
        st.caption(f"กลุ่ม: {prov_row['CLUSTER_NAME']}")
    with c_p_score:
        st.metric(
            label="ดัชนีคะแนนรวม",
            value=f"{score_val:.1f}",
            delta=prov_row["EV_TIER"] if is_ev_mode else f"คืนทุน ~{prov_row['SOLAR_PAYBACK_YEARS']} ปี"
        )

    # Strategic Advice
    if is_ev_mode:
        st.success(f"🔌 **หัวชาร์จแนะนำ:** {prov_row['CHARGER_TECH']}")
        st.info(f"📍 **ทำเลเป้าหมาย:** {prov_row['TARGET_LOCATIONS']}")
    else:
        st.success(f"☀️ **ระยะเวลาคืนทุนโดยประมาณ:** {prov_row['SOLAR_PAYBACK_YEARS']} ปี")
        st.info("💡 **ความคุ้มค่า:** เหมาะสำหรับบ้านเดี่ยว/ที่อยู่อาศัยที่ใช้เครื่องปรับอากาศช่วงกลางวัน")

    # 4 Core Statistics
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("ค่าไฟบ้าน/หลัง", f"{prov_row['ELEC_PER_HOUSE']:,.0f} kWh")
    with s2:
        st.metric("ค่าไฟบ้าน/คน", f"{prov_row['ELEC_PER_CAPITA']:,.0f} kWh")
    with s3:
        st.metric("สัดส่วนไฟโรงงาน", f"{prov_row['IND_ELEC_RATIO']:.1f}%")
    with s4:
        st.metric("ขนาดครัวเรือน", f"{prov_row['AVG_HOUSEHOLD_SIZE']} คน/บ้าน")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Sub-tabs for Charts and Simulation
    tab_radar, tab_bar, tab_whatif, tab_pca = st.tabs([
        "🕸️ เรดาร์เปรียบเทียบ",
        "🏆 กราฟแท่งจัดอันดับ",
        "💡 แบบจำลอง What-If",
        "🗺️ PCA 2D"
    ])

    with tab_radar:
        def norm_val(val, min_v, max_v):
            return np.clip(np.round(((val - min_v) / (max_v - min_v)) * 100, 1), 5, 100)

        categories = ['ค่าไฟบ้านต่อหลัง', 'สัดส่วนโรงงาน (%)', 'ความหนาแน่นเมือง/คอนโด', 'ค่าไฟบ้านต่อคน']
        
        prov_values = [
            norm_val(prov_row["ELEC_PER_HOUSE"], df_all["ELEC_PER_HOUSE"].min(), df_all["ELEC_PER_HOUSE"].max()),
            norm_val(prov_row["IND_ELEC_RATIO"], df_all["IND_ELEC_RATIO"].min(), df_all["IND_ELEC_RATIO"].max()),
            norm_val(df_all["AVG_HOUSEHOLD_SIZE"].max() - prov_row["AVG_HOUSEHOLD_SIZE"], 0, df_all["AVG_HOUSEHOLD_SIZE"].max() - df_all["AVG_HOUSEHOLD_SIZE"].min()),
            norm_val(prov_row["ELEC_PER_CAPITA"], df_all["ELEC_PER_CAPITA"].min(), df_all["ELEC_PER_CAPITA"].max())
        ]

        nat_values = [
            norm_val(df_all["ELEC_PER_HOUSE"].mean(), df_all["ELEC_PER_HOUSE"].min(), df_all["ELEC_PER_HOUSE"].max()),
            norm_val(df_all["IND_ELEC_RATIO"].mean(), df_all["IND_ELEC_RATIO"].min(), df_all["IND_ELEC_RATIO"].max()),
            norm_val(df_all["AVG_HOUSEHOLD_SIZE"].max() - df_all["AVG_HOUSEHOLD_SIZE"].mean(), 0, df_all["AVG_HOUSEHOLD_SIZE"].max() - df_all["AVG_HOUSEHOLD_SIZE"].min()),
            norm_val(df_all["ELEC_PER_CAPITA"].mean(), df_all["ELEC_PER_CAPITA"].min(), df_all["ELEC_PER_CAPITA"].max())
        ]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=nat_values,
            theta=categories,
            fill='toself',
            name='ค่าเฉลี่ยประเทศ',
            line_color=radar_nat_color,
            fillcolor=radar_nat_fill
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=prov_values,
            theta=categories,
            fill='toself',
            name=prov_row["PROVINCE_CLEAN"],
            line_color='#10b981',
            fillcolor='rgba(16, 185, 129, 0.25)'
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color=text_muted, gridcolor=plotly_grid),
                angularaxis=dict(color=text_sub, gridcolor=plotly_grid),
                bgcolor=bg_card
            ),
            paper_bgcolor=bg_card,
            plot_bgcolor=bg_card,
            font=dict(family="Kanit", color=text_main),
            showlegend=True,
            legend=dict(orientation="h", y=-0.12, x=0.2, font=dict(color=text_main)),
            height=360,
            margin=dict(l=30, r=30, t=15, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with tab_bar:
        target_cluster = prov_row["CLUSTER_ID"]
        score_col = "EV_SCORE" if is_ev_mode else "SOLAR_SCORE"
        score_label = "คะแนนความพร้อม EV" if is_ev_mode else "คะแนนศักยภาพโซลาร์"

        # ดึงทุกจังหวัดในกลุ่มเดียวกับจังหวัดที่เลือก เรียงลำดับจากคะแนนสูงสุดลงมา
        cluster_df = df_all[df_all["CLUSTER_ID"] == target_cluster].sort_values(by=score_col, ascending=False).copy()
        
        cluster_info_names = {
            2: "Cluster 2: ศูนย์กลางเศรษฐกิจและอุตสาหกรรม (13 จังหวัด)",
            1: "Cluster 1: เมืองศูนย์กลางภูมิภาคและท่องเที่ยว (32 จังหวัด)",
            0: "Cluster 0: เกษตรกรรมและชุมชนชนบท (32 จังหวัด)"
        }
        
        st.markdown(
            f"<div style='font-size:13px; color:{text_sub}; margin-bottom:10px;'>"
            f"เปรียบเทียบอันดับในกลุ่ม <b>{cluster_info_names.get(target_cluster, '')}</b> "
            f"โดยแท่งสีเขียวมรกต <span style='color:#10b981; font-weight:700;'>■ {prov_row['PROVINCE_CLEAN']}</span> คือจังหวัดที่คุณกำลังวิเคราะห์"
            f"</div>",
            unsafe_allow_html=True
        )

        # กำหนดสีแท่ง: จังหวัดที่เลือกจะใช้สีเขียวมรกตเด่นชัด (#10b981) ส่วนจังหวัดอื่นในกลุ่มจะใช้โทนสีของคลัสเตอร์
        cluster_base_colors = {
            2: "rgba(59, 130, 246, 0.45)",
            1: "rgba(14, 165, 233, 0.45)",
            0: "rgba(245, 158, 11, 0.45)"
        }
        base_c = cluster_base_colors.get(target_cluster, "rgba(100, 116, 139, 0.45)")
        highlight_c = "#10b981"

        bar_colors = [highlight_c if p == prov_row["PROVINCE_CLEAN"] else base_c for p in cluster_df["PROVINCE_CLEAN"]]
        border_colors = [highlight_c if p == prov_row["PROVINCE_CLEAN"] else "rgba(255, 255, 255, 0.15)" for p in cluster_df["PROVINCE_CLEAN"]]
        border_widths = [2.5 if p == prov_row["PROVINCE_CLEAN"] else 1 for p in cluster_df["PROVINCE_CLEAN"]]
        text_colors = [highlight_c if p == prov_row["PROVINCE_CLEAN"] else text_sub for p in cluster_df["PROVINCE_CLEAN"]]

        fig_bar = go.Figure(go.Bar(
            x=cluster_df[score_col],
            y=cluster_df["PROVINCE_CLEAN"],
            orientation="h",
            marker=dict(
                color=bar_colors,
                line=dict(color=border_colors, width=border_widths)
            ),
            text=cluster_df[score_col],
            textposition='outside',
            textfont=dict(size=11, color=text_colors, family="Kanit")
        ))

        # Dynamic Height ตามจำนวนจังหวัด: C2 (~420px), C1/C0 (~860px)
        chart_height = max(420, len(cluster_df) * 27)

        fig_bar.update_layout(
            yaxis=dict(autorange="reversed", color=text_sub, tickfont=dict(size=12, family="Kanit")),
            xaxis=dict(color=text_sub, gridcolor=plotly_grid, range=[0, max(cluster_df[score_col].max() + 10, 100)]),
            paper_bgcolor=bg_card,
            plot_bgcolor=bg_card,
            font=dict(family="Kanit", color=text_main),
            height=chart_height,
            margin=dict(l=0, r=40, t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab_whatif:
        st.caption("ทดลองปรับเปลี่ยนพารามิเตอร์การขยายตัวของเมือง เพื่อดูว่าคะแนนความคุ้มค่าจะเปลี่ยนไปอย่างไร")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            growth_house = st.slider("📈 อัตราการเติบโตของการใช้ไฟบ้าน (%):", 0, 100, 15, step=5)
            growth_ind = st.slider("🏭 อัตราการขยายตัวของโรงงาน (%):", 0, 100, 10, step=5)

        with col_w2:
            sim_h = prov_row["ELEC_PER_HOUSE"] * (1 + growth_house / 100.0)
            sim_i = prov_row["IND_ELEC_RATIO"] * (1 + growth_ind / 100.0)
            
            min_h, max_h = df_all["ELEC_PER_HOUSE"].min(), df_all["ELEC_PER_HOUSE"].max()
            min_i, max_i = df_all["IND_ELEC_RATIO"].min(), df_all["IND_ELEC_RATIO"].max()
            min_hh, max_hh = df_all["AVG_HOUSEHOLD_SIZE"].min(), df_all["AVG_HOUSEHOLD_SIZE"].max()

            norm_h = (sim_h - min_h) / (max_h - min_h)
            norm_i = (sim_i - min_i) / (max_i - min_i)
            norm_u = (max_hh - prov_row["AVG_HOUSEHOLD_SIZE"]) / (max_hh - min_hh)
            c_weight = {2: 1.0, 1: 0.75, 0: 0.4}.get(prov_row["CLUSTER_ID"], 0.5)

            new_score = np.clip(np.round(((norm_h * 0.35) + (norm_i * 0.25) + (c_weight * 0.25) + (norm_u * 0.15)) * 100, 1), 10.0, 100.0)
            score_diff = np.round(new_score - prov_row["EV_SCORE"], 1)

            st.metric(
                label=f"คะแนนจำลองใหม่ ({prov_row['PROVINCE_CLEAN']})",
                value=f"{new_score} คะแนน",
                delta=f"{'+' if score_diff >= 0 else ''}{score_diff} จากเดิม {prov_row['EV_SCORE']}"
            )

    with tab_pca:
        st.markdown(f"""
            <div style='background-color:{bg_card_inner}; border:1px solid {border_color}; border-radius:8px; padding:10px 14px; margin-bottom:10px; font-size:12px; line-height:1.6; color:{text_sub};'>
                💡 <b>คำอธิบายความหมายของแกน PCA:</b><br/>
                • <b>แกนนอน: PC1 (74.1%)</b> — <i>"แกนความเป็นเมืองและระดับการบริโภคพลังงาน"</i> (ขวาสุด = เมืองใหญ่/ใช้ไฟบ้านและไฟคนสูงมาก เช่น กทม., นนทบุรี, ระยอง / ซ้ายสุด = เกษตรกรรม/ชนบท)<br/>
                • <b>แกนตั้ง: PC2 (15.9%)</b> — <i>"แกนความเข้มข้นของภาคอุตสาหกรรม"</i> (บนสุด = สัดส่วนไฟโรงงานสูงมาก เช่น ระยอง, อยุธยา / ล่างสุด = เน้นที่อยู่อาศัยและพาณิชย์ เช่น กทม., นนทบุรี, ภูเก็ต)
            </div>
        """, unsafe_allow_html=True)
        fig_pca = px.scatter(
            df_all,
            x="PCA1",
            y="PCA2",
            color="CLUSTER_NAME",
            hover_name="PROVINCE_CLEAN",
            hover_data={"ELEC_PER_HOUSE": True, "IND_ELEC_RATIO": True, "EV_SCORE": True, "CLUSTER_NAME": False},
            labels={
                "PCA1": "แกนนอน: PC1 (74.1%) — แกนความเป็นเมืองและระดับการบริโภคพลังงาน",
                "PCA2": "แกนตั้ง: PC2 (15.9%) — แกนความเข้มข้นของภาคอุตสาหกรรม"
            },
            color_discrete_map={
                "Cluster 2: ศูนย์กลางเศรษฐกิจและอุตสาหกรรม (Industrial & Metropolitan Hub)": "#10b981",
                "Cluster 1: เมืองศูนย์กลางภูมิภาคและท่องเที่ยว (Urban & Tourism Hub)": "#3b82f6",
                "Cluster 0: เกษตรกรรมและชุมชนชนบท (Rural & Agricultural)": "#f59e0b"
            }
        )
        fig_pca.update_traces(
            marker=dict(size=10, line=dict(width=1, color='#ffffff')),
            hovertemplate=(
                "<b>📍 %{hovertext}</b><br><br>"
                "• <b>PC1 (ความเป็นเมือง/พลังงาน):</b> %{x:.2f}<br>"
                "• <b>PC2 (ความเข้มข้นอุตสาหกรรม):</b> %{y:.2f}<br>"
                "• <b>ค่าไฟบ้าน/หลัง:</b> %{customdata[0]:,.0f} kWh<br>"
                "• <b>สัดส่วนไฟโรงงาน:</b> %{customdata[1]:.1f}%<br>"
                "• <b>คะแนนความพร้อม EV:</b> %{customdata[2]:.1f} คะแนน"
                "<extra></extra>"
            )
        )
        fig_pca.update_layout(
            paper_bgcolor=bg_card,
            plot_bgcolor=bg_card,
            font=dict(family="Kanit", color=text_main),
            xaxis=dict(
                title=dict(
                    text="แกนนอน: PC1 (74.1%) — แกนความเป็นเมืองและระดับการบริโภคพลังงาน",
                    font=dict(size=12, family="Kanit", color=text_sub)
                ),
                gridcolor=plotly_grid,
                color=text_muted,
                automargin=True
            ),
            yaxis=dict(
                title=dict(
                    text="แกนตั้ง: PC2 (15.9%) — แกนความเข้มข้นของภาคอุตสาหกรรม",
                    font=dict(size=12, family="Kanit", color=text_sub)
                ),
                gridcolor=plotly_grid,
                color=text_muted,
                automargin=True
            ),
            height=400,
            margin=dict(l=30, r=30, t=10, b=20),
            legend=dict(orientation="h", y=-0.32, font=dict(color=text_main, size=11))
        )
        st.plotly_chart(fig_pca, use_container_width=True)
