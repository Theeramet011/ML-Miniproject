"""
Thailand Green Energy & EV Site Selection Planner
Streamlit Web Application - Modern Top Header & Dual Theme (Light & VoltAgent Dark)
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from business_engine import calculate_business_scores

# 1. Page Configuration (No Sidebar, Expanded Full Width)
st.set_page_config(
    page_title="Thailand Green Energy & EV Planner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"  # Default: Light mode as requested

if "business_mode" not in st.session_state:
    st.session_state["business_mode"] = "EV"  # 'EV' or 'SOLAR'

if "cluster_filter" not in st.session_state:
    st.session_state["cluster_filter"] = "ALL"  # 'ALL', '2', '1', '0'

is_dark = st.session_state["theme_mode"] == "dark"
is_ev_mode = st.session_state["business_mode"] == "EV"

# Theme Variables
if is_dark:
    # VoltAgent Void-Black Theme
    bg_app = "#07080b"
    bg_surface = "#0f1218"
    bg_card_inner = "#141923"
    border_color = "#1f2637"
    text_primary = "#f8fafc"
    text_secondary = "#94a3b8"
    text_muted = "#64748b"
    table_header_bg = "#11141c"
    plotly_bg = "rgba(0,0,0,0)"
    plotly_grid = "#1e2533"
    radar_nat_color = "#64748b"
    radar_nat_fill = "rgba(100, 116, 139, 0.2)"
else:
    # Clean White VoltAgent Light Theme (Matches Image 2)
    bg_app = "#f8fafc"
    bg_surface = "#ffffff"
    bg_card_inner = "#f1f5f9"
    border_color = "#e2e8f0"
    text_primary = "#0f172a"
    text_secondary = "#475569"
    text_muted = "#94a3b8"
    table_header_bg = "#f8fafc"
    plotly_bg = "rgba(0,0,0,0)"
    plotly_grid = "#e2e8f0"
    radar_nat_color = "#94a3b8"
    radar_nat_fill = "rgba(148, 163, 184, 0.2)"

# Custom CSS Injection
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

    .stApp {{
        background-color: {bg_app} !important;
        color: {text_primary} !important;
    }}

    /* Top Navigation Header Card */
    .top-navbar {{
        background: {bg_surface};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 14px 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}

    /* Metric Cards */
    div[data-testid="stMetric"] {{
        background: {bg_surface} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease !important;
    }}

    div[data-testid="stMetric"]:hover {{
        border-color: rgba(16, 185, 129, 0.5) !important;
        transform: translateY(-2px) !important;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {text_secondary} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: {text_primary} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        font-size: 26px !important;
    }}

    div[data-testid="stMetricDelta"] {{
        color: #10b981 !important;
        font-weight: 600 !important;
    }}

    /* Card Panels */
    .content-panel {{
        background: {bg_surface};
        border: 1px solid {border_color};
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }}

    /* Inputs */
    input, .stTextInput>div>div>input {{
        background-color: {bg_card_inner} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {bg_surface};
        padding: 6px;
        border-radius: 12px;
        border: 1px solid {border_color};
        margin-bottom: 12px;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 18px;
        color: {text_secondary};
        font-weight: 500;
        transition: all 0.2s;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #10b981 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.25) !important;
    }}

    /* General Buttons */
    .stButton>button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
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
</style>
""", unsafe_allow_html=True)

# 2. Load & Cache Dataset
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, "clustered_provinces_2563.csv")
    if not os.path.exists(csv_file):
        csv_file = os.path.join(base_dir, "..", "Datasets-20261018T071705Z-1-001", "Datasets", "code-ผล", "clustered_provinces_2563.csv")
    
    df = pd.read_csv(csv_file)
    return calculate_business_scores(df)

df_all = load_data()

# 3. Top Navigation Bar (Header)
with st.container():
    col_hdr_logo, col_hdr_controls = st.columns([6, 6])
    
    with col_hdr_logo:
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:46px; height:46px; border-radius:12px; background:linear-gradient(135deg, #10b981 0%, #059669 100%); display:flex; align-items:center; justify-content:center; box-shadow:0 4px 14px rgba(16,185,129,0.35); flex-shrink:0;">
                    <span style="font-size:24px; color:#ffffff;">⚡</span>
                </div>
                <div>
                    <h1 style="font-size:20px; font-weight:800; color:{text_primary}; margin:0; line-height:1.2; letter-spacing:-0.02em;">
                        Thailand Green Energy & EV Planner
                    </h1>
                    <p style="font-size:12px; color:{text_muted}; margin:2px 0 0 0;">
                        ระบบวางแผนธุรกิจพลังงานสะอาดและทำเลสถานีชาร์จจากผลลัพธ์ K-Means (77 จังหวัด)
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_hdr_controls:
        c_mode_ev, c_mode_sol, c_theme = st.columns([3, 3, 2.5])
        
        with c_mode_ev:
            btn_ev_type = "primary" if is_ev_mode else "secondary"
            if st.button("⚡ สถานีชาร์จ EV", key="btn_ev", type=btn_ev_type, use_container_width=True):
                st.session_state["business_mode"] = "EV"
                st.rerun()

        with c_mode_sol:
            btn_sol_type = "primary" if not is_ev_mode else "secondary"
            if st.button("☀️ โซลาร์รูฟท็อป", key="btn_sol", type=btn_sol_type, use_container_width=True):
                st.session_state["business_mode"] = "SOLAR"
                st.rerun()

        with c_theme:
            theme_label = "☀️ โหมดสว่าง" if is_dark else "🌙 โหมดมืด"
            if st.button(theme_label, key="btn_toggle_theme", use_container_width=True):
                st.session_state["theme_mode"] = "light" if is_dark else "dark"
                st.rerun()

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Filter Data according to active cluster filter
active_filter = st.session_state["cluster_filter"]
if active_filter == "ALL":
    df_filtered = df_all.copy()
else:
    df_filtered = df_all[df_all["CLUSTER_ID"] == int(active_filter)].copy()

if is_ev_mode:
    df_filtered = df_filtered.sort_values(by="EV_SCORE", ascending=False).reset_index(drop=True)
else:
    df_filtered = df_filtered.sort_values(by="SOLAR_SCORE", ascending=False).reset_index(drop=True)

# 4. 4 KPI Metrics Row (Horizontal across top)
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
        label="📊 คะแนนเฉลี่ยทั่วประเทศ",
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

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# 5. Main 2-Column Layout (Matching Image 2)
col_left_table, col_right_details = st.columns([5, 7])

# ==================== LEFT COLUMN: Table & Cluster Filter Pills ====================
with col_left_table:
    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
            <h3 style="margin:0; font-size:16px; font-weight:700; color:{text_primary}; display:flex; align-items:center; gap:6px;">
                <span>📋</span> ตารางจัดอันดับความคุ้มค่า 77 จังหวัด
            </h3>
            <span style="font-size:12px; color:{text_muted};">แสดง {len(df_filtered)} จาก 77 จังหวัด</span>
        </div>
    """, unsafe_allow_html=True)

    # Search Box
    search_query = st.text_input("ค้นหาชื่อจังหวัด:", "", placeholder="🔍 ค้นหา เช่น นนทบุรี, ระยอง, เชียงใหม่...", label_visibility="collapsed")
    if search_query:
        df_table_view = df_filtered[df_filtered["PROVINCE_CLEAN"].str.contains(search_query.strip())]
    else:
        df_table_view = df_filtered

    # Cluster Filter Pills (4 Horizontal Buttons right above the table)
    c_lbl, c_all, c_c2, c_c1, c_c0 = st.columns([1.1, 1.6, 2.3, 2.3, 2.2])
    with c_lbl:
        st.markdown(f"<div style='padding-top:6px; font-size:12px; color:{text_muted};'>กลุ่ม:</div>", unsafe_allow_html=True)
    with c_all:
        if st.button("ทั้งหมด", key="f_all", type="primary" if active_filter == "ALL" else "secondary", use_container_width=True):
            st.session_state["cluster_filter"] = "ALL"
            st.rerun()
    with c_c2:
        if st.button("C2 (อุตสาหกรรม)", key="f_c2", type="primary" if active_filter == "2" else "secondary", use_container_width=True):
            st.session_state["cluster_filter"] = "2"
            st.rerun()
    with c_c1:
        if st.button("C1 (ท่องเที่ยว)", key="f_c1", type="primary" if active_filter == "1" else "secondary", use_container_width=True):
            st.session_state["cluster_filter"] = "1"
            st.rerun()
    with c_c0:
        if st.button("C0 (เกษตร)", key="f_c0", type="primary" if active_filter == "0" else "secondary", use_container_width=True):
            st.session_state["cluster_filter"] = "0"
            st.rerun()

    # Ranking Table Dataframe
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

    display_df = df_table_view[show_cols].rename(columns=rename_dict)
    display_df.index = np.arange(1, len(display_df) + 1)
    st.dataframe(display_df, use_container_width=True, height=480)

    # Download CSV Button
    csv_data = df_table_view.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดรายงานฉบับเต็ม (CSV)",
        data=csv_data,
        file_name=f"thailand_green_energy_ranking_{'ev' if is_ev_mode else 'solar'}.csv",
        mime="text/csv"
    )

# ==================== RIGHT COLUMN: Province Deep Dive & Charts ====================
with col_right_details:
    prov_list = df_all["PROVINCE_CLEAN"].tolist()
    default_idx = prov_list.index("นนทบุรี") if "นนทบุรี" in prov_list else 0
    selected_prov = st.selectbox("เลือกจังหวัดที่ต้องการวิเคราะห์เจาะลึก:", prov_list, index=default_idx)
    
    prov_row = df_all[df_all["PROVINCE_CLEAN"] == selected_prov].iloc[0]
    score_val = prov_row["EV_SCORE"] if is_ev_mode else prov_row["SOLAR_SCORE"]

    # Selected Province Card (Styled matching Image 2)
    st.markdown(f"""
        <div style="background:{bg_surface}; border:1px solid {border_color}; border-left:4px solid #10b981; border-radius:16px; padding:18px 22px; margin-bottom:14px; box-shadow:0 4px 10px -2px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <h2 style="margin:0; font-size:22px; font-weight:800; color:{text_primary};">{prov_row['CC-DESC']} ({prov_row['PROVINCE_CLEAN']})</h2>
                        <span style="font-size:12px; font-weight:600; padding:2px 10px; border-radius:9999px; background:rgba(16,185,129,0.12); color:#10b981; border:1px solid rgba(16,185,129,0.3);">
                            {prov_row['EV_TIER']}
                        </span>
                    </div>
                    <p style="margin:4px 0 0 0; color:{text_muted}; font-size:13px;">{prov_row['CLUSTER_NAME']}</p>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:11px; color:{text_muted}; font-weight:500;">ดัชนีคะแนนรวม</span>
                    <div style="font-family:'JetBrains Mono'; font-size:32px; font-weight:800; color:#10b981; line-height:1;">
                        {score_val}
                    </div>
                </div>
            </div>
            
            <!-- Strategic Advice Box -->
            <div style="background:{'#0a1a14' if is_dark else '#ecfdf5'}; border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:12px 16px; margin-top:14px;">
                <div style="font-size:13px; font-weight:700; color:#10b981; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
                    <span>✓</span> คำแนะนำกลยุทธ์การลงทุน (Strategic Recommendation):
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; font-size:12px;">
                    <div style="background:{bg_surface}; padding:8px 10px; border-radius:8px; border:1px solid {border_color};">
                        <span style="color:{text_muted}; display:block; font-size:11px;">ประเภทหัวชาร์จแนะนำ</span>
                        <strong style="color:{text_primary};">{prov_row['CHARGER_TECH']}</strong>
                    </div>
                    <div style="background:{bg_surface}; padding:8px 10px; border-radius:8px; border:1px solid {border_color};">
                        <span style="color:{text_muted}; display:block; font-size:11px;">ทำเลเป้าหมาย</span>
                        <strong style="color:{text_primary};">{prov_row['TARGET_LOCATIONS']}</strong>
                    </div>
                    <div style="background:{bg_surface}; padding:8px 10px; border-radius:8px; border:1px solid {border_color};">
                        <span style="color:{text_muted}; display:block; font-size:11px;">ระยะคืนทุนโซลาร์</span>
                        <strong style="color:#10b981;">ประมาณ {prov_row['SOLAR_PAYBACK_YEARS']} ปี</strong>
                    </div>
                </div>
            </div>
            
            <!-- Statistics Grid -->
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-top:12px; text-align:center;">
                <div style="background:{bg_card_inner}; padding:8px; border-radius:10px; border:1px solid {border_color};">
                    <span style="font-size:11px; color:{text_muted}; display:block;">ค่าไฟบ้านต่อหลัง</span>
                    <strong style="font-size:13px; color:{text_primary};">{prov_row['ELEC_PER_HOUSE']:,.0f} kWh</strong>
                </div>
                <div style="background:{bg_card_inner}; padding:8px; border-radius:10px; border:1px solid {border_color};">
                    <span style="font-size:11px; color:{text_muted}; display:block;">ค่าไฟบ้านต่อคน</span>
                    <strong style="font-size:13px; color:{text_primary};">{prov_row['ELEC_PER_CAPITA']:,.0f} kWh</strong>
                </div>
                <div style="background:{bg_card_inner}; padding:8px; border-radius:10px; border:1px solid {border_color};">
                    <span style="font-size:11px; color:{text_muted}; display:block;">สัดส่วนไฟโรงงาน</span>
                    <strong style="font-size:13px; color:{text_primary};">{prov_row['IND_ELEC_RATIO']:.1f}%</strong>
                </div>
                <div style="background:{bg_card_inner}; padding:8px; border-radius:10px; border:1px solid {border_color};">
                    <span style="font-size:11px; color:{text_muted}; display:block;">ขนาดครัวเรือน</span>
                    <strong style="font-size:13px; color:{text_primary};">{prov_row['AVG_HOUSEHOLD_SIZE']} คน/บ้าน</strong>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Sub-tabs for Details, Charts, and What-If
    t_radar, t_bar, t_whatif, t_pca = st.tabs([
        "🕸️ เรดาร์เปรียบเทียบ",
        "🏆 Top 10 กราฟแท่ง",
        "💡 แบบจำลอง What-If",
        "🗺️ PCA 2D"
    ])

    with t_radar:
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
            fillcolor='rgba(16, 185, 129, 0.3)'
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color=text_muted, gridcolor=plotly_grid),
                angularaxis=dict(color=text_secondary, gridcolor=plotly_grid),
                bgcolor=plotly_bg
            ),
            paper_bgcolor=plotly_bg,
            plot_bgcolor=plotly_bg,
            font=dict(family="Kanit", color=text_primary),
            showlegend=True,
            legend=dict(orientation="h", y=-0.12, x=0.2),
            height=360,
            margin=dict(l=30, r=30, t=15, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with t_bar:
        top10_df = df_filtered.head(10).copy()
        score_col = "EV_SCORE" if is_ev_mode else "SOLAR_SCORE"
        score_label = "คะแนนความพร้อม EV" if is_ev_mode else "คะแนนศักยภาพโซลาร์"

        fig_bar = px.bar(
            top10_df,
            x=score_col,
            y="PROVINCE_CLEAN",
            orientation="h",
            color="CLUSTER_ID",
            color_discrete_map={2: "#10b981", 1: "#3b82f6", 0: "#f59e0b"},
            labels={score_col: score_label, "PROVINCE_CLEAN": "จังหวัด", "CLUSTER_ID": "Cluster"},
            text=score_col
        )
        fig_bar.update_layout(
            yaxis=dict(autorange="reversed", color=text_secondary),
            xaxis=dict(color=text_secondary, gridcolor=plotly_grid),
            paper_bgcolor=plotly_bg,
            plot_bgcolor=plotly_bg,
            font=dict(family="Kanit", color=text_primary),
            height=360,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False
        )
        fig_bar.update_traces(
            textposition='outside',
            textfont=dict(family="JetBrains Mono", size=11, color="#10b981")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with t_whatif:
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

            st.markdown(f"""
                <div style="background:{bg_card_inner}; border:1px solid {border_color}; border-radius:12px; padding:16px; text-align:center;">
                    <span style="color:{text_muted}; font-size:12px;">ผลการจำลองสำหรับ {prov_row['PROVINCE_CLEAN']}</span>
                    <div style="font-family:'JetBrains Mono'; font-size:32px; font-weight:800; color:#10b981; margin:4px 0;">
                        {new_score} <span style="font-size:16px; font-weight:600; color:{'#10b981' if score_diff >= 0 else '#f43f5e'};">({'+' if score_diff >= 0 else ''}{score_diff})</span>
                    </div>
                    <div style="font-size:12px; color:{text_secondary};">คะแนนเดิม: {prov_row['EV_SCORE']} คะแนน</div>
                </div>
            """, unsafe_allow_html=True)

    with t_pca:
        st.caption("แสดงพิกัดของทั้ง 77 จังหวัดในมิติ PCA ที่ลดรูปมาจาก 4 ตัวแปรหลัก")
        fig_pca = px.scatter(
            df_all,
            x="PCA1",
            y="PCA2",
            color="CLUSTER_NAME",
            hover_name="PROVINCE_CLEAN",
            hover_data={"ELEC_PER_HOUSE": True, "IND_ELEC_RATIO": True, "EV_SCORE": True, "CLUSTER_NAME": False},
            labels={"PCA1": "PC1 (74.1%)", "PCA2": "PC2 (15.9%)"},
            color_discrete_map={
                "Cluster 2: ศูนย์กลางเศรษฐกิจและอุตสาหกรรม (Industrial & Metropolitan Hub)": "#10b981",
                "Cluster 1: เมืองศูนย์กลางภูมิภาคและท่องเที่ยว (Urban & Tourism Hub)": "#3b82f6",
                "Cluster 0: เกษตรกรรมและชุมชนชนบท (Rural & Agricultural)": "#f59e0b"
            }
        )
        fig_pca.update_traces(marker=dict(size=10, line=dict(width=1, color='#ffffff')))
        fig_pca.update_layout(
            paper_bgcolor=plotly_bg,
            plot_bgcolor=plotly_bg,
            font=dict(family="Kanit", color=text_primary),
            xaxis=dict(gridcolor=plotly_grid, color=text_muted),
            yaxis=dict(gridcolor=plotly_grid, color=text_muted),
            height=360,
            margin=dict(l=20, r=20, t=10, b=10),
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig_pca, use_container_width=True)
