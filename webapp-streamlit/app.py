"""
Thailand Green Energy & EV Site Selection Planner
Streamlit Web Application - VoltAgent Design System (Void-Black + Emerald Accent)
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from business_engine import calculate_business_scores

# 1. Page Configuration
st.set_page_config(
    page_title="Thailand Green Energy & EV Planner | VoltAgent Theme",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: VoltAgent Design System (Void-Black + Emerald Accent)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Kanit', sans-serif;
    }

    /* Void-Black Backgrounds */
    .stApp {
        background-color: #07080b;
        color: #f1f5f9;
    }

    /* Sidebar Width & VoltAgent Theme */
    section[data-testid="stSidebar"] {
        min-width: 380px !important;
        max-width: 420px !important;
        background-color: #0d0f14 !important;
        border-right: 1px solid #1a1f29 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.8rem;
    }

    /* Fix Dropdown & Multiselect Truncation: Allow Full Text & Wrapping */
    div[data-baseweb="select"] {
        width: 100% !important;
    }
    
    div[data-baseweb="tag"] {
        max-width: 100% !important;
        height: auto !important;
        white-space: normal !important;
        padding-top: 5px !important;
        padding-bottom: 5px !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
        background-color: rgba(16, 185, 129, 0.12) !important;
        border: 1px solid rgba(16, 185, 129, 0.35) !important;
        border-radius: 6px !important;
        margin-bottom: 4px !important;
    }

    div[data-baseweb="tag"] span {
        white-space: normal !important;
        word-break: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
        font-size: 13px !important;
        line-height: 1.3 !important;
        color: #34d399 !important;
    }

    /* Dropdown List Items */
    ul[role="listbox"] {
        background-color: #0e1117 !important;
        border: 1px solid #242b38 !important;
        border-radius: 8px !important;
        max-height: 380px !important;
    }

    ul[role="listbox"] li {
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
        font-size: 13px !important;
        padding: 10px 12px !important;
        border-bottom: 1px solid #161a23 !important;
    }

    ul[role="listbox"] li:hover {
        background-color: rgba(16, 185, 129, 0.14) !important;
        color: #10b981 !important;
    }

    /* Metric Cards: VoltAgent Terminal Aesthetic */
    div[data-testid="stMetric"] {
        background: #0f1218;
        border: 1px solid #1e2533;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
        transition: all 0.2s ease-in-out;
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(16, 185, 129, 0.45);
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.1);
        transform: translateY(-2px);
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        font-size: 26px !important;
    }

    div[data-testid="stMetricDelta"] {
        color: #10b981 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0b0e14;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #1a202c;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        color: #94a3b8;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stTabs [aria-selected="true"] {
        background-color: #10b981 !important;
        color: #041f17 !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3) !important;
    }

    /* Buttons */
    .stButton>button, div[data-testid="stDownloadButton"]>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #031e16 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.25) !important;
        transition: all 0.2s !important;
    }

    .stButton>button:hover, div[data-testid="stDownloadButton"]>button:hover {
        opacity: 0.92 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }

    /* Terminal Badge */
    .terminal-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        padding: 3px 10px;
        border-radius: 9999px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        letter-spacing: 0.05em;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
    }
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

# 3. Sidebar Controls
with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
            <div style="width:40px; height:40px; border-radius:10px; background:linear-gradient(135deg, #10b981, #047857); display:flex; align-items:center; justify-content:center; box-shadow:0 0 15px rgba(16,185,129,0.4);">
                <span style="font-size:22px;">⚡</span>
            </div>
            <div>
                <div style="font-weight:700; font-size:16px; color:#f8fafc; letter-spacing:-0.02em;">VOLTAGENT PLANNER</div>
                <div class="terminal-badge"><span class="status-dot"></span>SYSTEM ONLINE</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.caption("ระบบวางแผนทำเลธุรกิจพลังงานสะอาดและวิเคราะห์โครงข่ายไฟฟ้า (77 จังหวัด)")
    st.divider()

    # เลือกโหมดการวิเคราะห์
    mode = st.radio(
        "🎯 เลือกประเภทธุรกิจเป้าหมาย:",
        ("⚡ สถานีชาร์จ EV (EV Charging)", "☀️ โซลาร์เซลล์หลังคาบ้าน (Solar Rooftop)"),
        index=0
    )
    is_ev_mode = "EV" in mode

    st.divider()

    # ตัวกรองกลุ่มคลัสเตอร์ (ข้อความกระชับ ชัดเจน ขยายเต็ม ไม่ถูกตัดคำ)
    st.subheader("🔍 ตัวกรองกลุ่มคลัสเตอร์ (Clusters)")
    selected_clusters = st.multiselect(
        "เลือกกลุ่มจังหวัดที่ต้องการแสดง:",
        options=[2, 1, 0],
        default=[2, 1, 0],
        format_func=lambda x: {
            2: "⚡ Cluster 2: ศูนย์กลางเศรษฐกิจ/อุตสาหกรรม (13 จ.)",
            1: "🏖️ Cluster 1: ศูนย์กลางท่องเที่ยว/ภูมิภาค (32 จ.)",
            0: "🌾 Cluster 0: ชนบทและเกษตรกรรม (32 จ.)"
        }[x]
    )

    st.divider()
    st.markdown("""
        <div style="font-size:11px; color:#64748b; line-height:1.5;">
            <strong>Data Sources:</strong><br>
            • กรมการปกครอง (DOPA) 2563<br>
            • สำนักงานนโยบายและแผนพลังงาน (สนพ.) 2563<br>
            • K-Means Machine Learning (K=3)
        </div>
    """, unsafe_allow_html=True)

# กรองข้อมูลตามกลุ่มที่เลือก
df_filtered = df_all[df_all["CLUSTER_ID"].isin(selected_clusters)].copy()
if is_ev_mode:
    df_filtered = df_filtered.sort_values(by="EV_SCORE", ascending=False).reset_index(drop=True)
else:
    df_filtered = df_filtered.sort_values(by="SOLAR_SCORE", ascending=False).reset_index(drop=True)

# 4. Header & Overview KPIs
st.markdown("""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
        <div>
            <h1 style="font-size:28px; font-weight:800; color:#f8fafc; margin-bottom:4px; letter-spacing:-0.03em;">
                THAILAND GREEN ENERGY & EV SITE SELECTION PLANNER
            </h1>
            <p style="color:#94a3b8; font-size:14px; margin:0;">
                ระบบวิเคราะห์ทำเลและวางแผนการลงทุนสถานีชาร์จรถยนต์ไฟฟ้า และศักยภาพโซลาร์เซลล์หลังคาเรือน จากการบูรณาการข้อมูลภาครัฐ 77 จังหวัด
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    top_p = df_filtered.iloc[0] if len(df_filtered) > 0 else df_all.iloc[0]
    top_score = top_p["EV_SCORE"] if is_ev_mode else top_p["SOLAR_SCORE"]
    st.metric(
        label="🏆 จังหวัดอันดับ 1",
        value=f"{top_p['PROVINCE_CLEAN']}",
        delta=f"{top_score:.1f} คะแนน"
    )

with col_kpi2:
    avg_score = df_filtered["EV_SCORE"].mean() if is_ev_mode else df_filtered["SOLAR_SCORE"].mean()
    st.metric(
        label="📊 คะแนนเฉลี่ยกลุ่มที่เลือก",
        value=f"{avg_score:.1f} / 100",
        delta="ระดับประเทศ"
    )

with col_kpi3:
    tier1_cnt = (df_filtered["EV_SCORE"] >= 75).sum()
    st.metric(
        label="⭐ ทำเลทอง Tier 1 (>=75)",
        value=f"{tier1_cnt} จังหวัด",
        delta="ความคุ้มค่าสูง"
    )

with col_kpi4:
    c2_cnt = (df_filtered["CLUSTER_ID"] == 2).sum()
    st.metric(
        label="🏭 เมืองอุตสาหกรรม/เศรษฐกิจ",
        value=f"{c2_cnt} จังหวัด",
        delta="Cluster 2"
    )

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# 5. Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 ตารางจัดอันดับ & กราฟ Top 10",
    "🔍 เจาะลึกรายจังหวัด (Deep Dive)",
    "💡 แบบจำลองสถานการณ์ (What-If)",
    "🗺️ แผนภูมิ PCA Clusters 2D"
])

# ----------------- TAB 1: Ranking & Top 10 -----------------
with tab1:
    col_t1, col_t2 = st.columns([6, 4])

    with col_t1:
        st.subheader("📋 ตารางจัดอันดับความคุ้มค่า")
        
        # ค้นหาชื่อจังหวัด
        search_query = st.text_input("🔎 ค้นหาชื่อจังหวัด:", "", placeholder="พิมพ์ชื่อจังหวัด เช่น เชียงใหม่, ระยอง...")
        if search_query:
            df_display = df_filtered[df_filtered["PROVINCE_CLEAN"].str.contains(search_query)]
        else:
            df_display = df_filtered

        # เลือกคอลัมน์แสดงผล
        if is_ev_mode:
            show_cols = ["PROVINCE_CLEAN", "CLUSTER_ID", "EV_SCORE", "EV_TIER", "CHARGER_TECH", "ELEC_PER_HOUSE", "IND_ELEC_RATIO"]
            rename_dict = {
                "PROVINCE_CLEAN": "จังหวัด",
                "CLUSTER_ID": "Cluster",
                "EV_SCORE": "คะแนน EV",
                "EV_TIER": "ระดับความพร้อม",
                "CHARGER_TECH": "หัวชาร์จแนะนำ",
                "ELEC_PER_HOUSE": "ค่าไฟบ้านต่อหลัง (kWh)",
                "IND_ELEC_RATIO": "สัดส่วนโรงงาน (%)"
            }
        else:
            show_cols = ["PROVINCE_CLEAN", "CLUSTER_ID", "SOLAR_SCORE", "SOLAR_PAYBACK_YEARS", "ELEC_PER_HOUSE", "ELEC_PER_CAPITA"]
            rename_dict = {
                "PROVINCE_CLEAN": "จังหวัด",
                "CLUSTER_ID": "Cluster",
                "SOLAR_SCORE": "คะแนนโซลาร์",
                "SOLAR_PAYBACK_YEARS": "คืนทุน (ปี)",
                "ELEC_PER_HOUSE": "ค่าไฟบ้านต่อหลัง (kWh)",
                "ELEC_PER_CAPITA": "ค่าไฟบ้านต่อคน (kWh)"
            }

        table_df = df_display[show_cols].rename(columns=rename_dict)
        table_df.index = np.arange(1, len(table_df) + 1)
        st.dataframe(table_df, use_container_width=True, height=450)

        # Download CSV
        csv_data = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดรายงานฉบับเต็ม (CSV)",
            data=csv_data,
            file_name=f"thailand_green_energy_ranking_{'ev' if is_ev_mode else 'solar'}.csv",
            mime="text/csv"
        )

    with col_t2:
        st.subheader("🏆 Top 10 จังหวัดคะแนนสูงสุด")
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
            yaxis=dict(autorange="reversed", color="#cbd5e1"),
            xaxis=dict(color="#cbd5e1", gridcolor="#1e2533"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Kanit", color="#e2e8f0"),
            height=480,
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=False
        )
        fig_bar.update_traces(
            textposition='outside',
            textfont=dict(family="JetBrains Mono", size=12, color="#34d399"),
            marker=dict(line=dict(width=1, color="rgba(16,185,129,0.3)"))
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- TAB 2: Province Deep Dive -----------------
with tab2:
    st.subheader("🔍 วิเคราะห์เจาะลึกศักยภาพรายจังหวัด")
    
    col_d1, col_d2 = st.columns([5, 5])
    
    with col_d1:
        prov_list = df_all["PROVINCE_CLEAN"].tolist()
        default_idx = prov_list.index("กรุงเทพมหานคร") if "กรุงเทพมหานคร" in prov_list else 0
        selected_prov = st.selectbox("เลือกจังหวัดที่ต้องการวิเคราะห์:", prov_list, index=default_idx)
        
        prov_row = df_all[df_all["PROVINCE_CLEAN"] == selected_prov].iloc[0]

        st.markdown(f"""
            <div style="background:#0e1117; border:1px solid #1f2533; border-left:4px solid #10b981; border-radius:12px; padding:18px; margin-bottom:15px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h3 style="margin:0; font-size:22px; color:#f8fafc; font-weight:700;">📍 {prov_row['CC-DESC']}</h3>
                        <p style="margin:4px 0 0 0; color:#10b981; font-size:13px; font-weight:600;">{prov_row['CLUSTER_NAME']}</p>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:11px; color:#94a3b8;">ดัชนีคะแนนรวม</span>
                        <div style="font-family:'JetBrains Mono'; font-size:28px; font-weight:800; color:#34d399;">
                            {prov_row['EV_SCORE'] if is_ev_mode else prov_row['SOLAR_SCORE']}
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 💡 คำแนะนำเชิงกลยุทธ์ (Strategic Advice):")
        if is_ev_mode:
            st.markdown(f"""
                <div style="background:#0a1c17; border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:14px; margin-bottom:12px;">
                    <div style="color:#34d399; font-weight:600; font-size:13px; margin-bottom:4px;">🔌 หัวชาร์จแนะนำ: {prov_row['CHARGER_TECH']}</div>
                    <div style="color:#cbd5e1; font-size:13px;">📍 ทำเลเป้าหมาย: {prov_row['TARGET_LOCATIONS']}</div>
                    <div style="color:#94a3b8; font-size:12px; margin-top:6px;">ระดับความพร้อม: <strong style="color:#10b981;">{prov_row['EV_TIER']}</strong></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background:#0a1c17; border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:14px; margin-bottom:12px;">
                    <div style="color:#34d399; font-weight:600; font-size:13px; margin-bottom:4px;">☀️ ระยะเวลาคืนทุนโซลาร์: ประมาณ {prov_row['SOLAR_PAYBACK_YEARS']} ปี</div>
                    <div style="color:#cbd5e1; font-size:13px;">ความคุ้มค่า: เหมาะสำหรับบ้านเดี่ยว/ที่อยู่อาศัยที่ใช้เครื่องปรับอากาศช่วงกลางวัน</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; margin-top:10px;">
                <div style="background:#0f1218; border:1px solid #1a202c; border-radius:8px; padding:10px; text-align:center;">
                    <span style="font-size:11px; color:#64748b;">ประชากร</span>
                    <div style="font-weight:700; color:#e2e8f0; font-size:14px;">{prov_row['TOTAL']:,} คน</div>
                </div>
                <div style="background:#0f1218; border:1px solid #1a202c; border-radius:8px; padding:10px; text-align:center;">
                    <span style="font-size:11px; color:#64748b;">จำนวนบ้าน</span>
                    <div style="font-weight:700; color:#e2e8f0; font-size:14px;">{prov_row['HOUSE']:,} หลัง</div>
                </div>
                <div style="background:#0f1218; border:1px solid #1a202c; border-radius:8px; padding:10px; text-align:center;">
                    <span style="font-size:11px; color:#64748b;">ขนาดครัวเรือน</span>
                    <div style="font-weight:700; color:#e2e8f0; font-size:14px;">{prov_row['AVG_HOUSEHOLD_SIZE']} คน/บ้าน</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_d2:
        st.markdown("#### 🕸️ กราฟเรดาร์เปรียบเทียบสถิติกับค่าเฉลี่ยทั้งประเทศ")

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
            line_color='#64748b',
            fillcolor='rgba(100, 116, 139, 0.2)'
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
                radialaxis=dict(visible=True, range=[0, 100], color="#64748b", gridcolor="#1e2533"),
                angularaxis=dict(color="#cbd5e1", gridcolor="#1e2533"),
                bgcolor="rgba(0,0,0,0)"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Kanit", color="#e2e8f0"),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1, x=0.2),
            height=430,
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# ----------------- TAB 3: What-If Simulator -----------------
with tab3:
    st.subheader("💡 แบบจำลองสถานการณ์การเติบโตของเมือง (What-If Simulator)")
    st.caption("ทดลองปรับเปลี่ยนพารามิเตอร์การขยายตัวของเมือง เพื่อดูว่าคะแนนความคุ้มค่าในการลงทุนสถานีชาร์จจะเปลี่ยนไปอย่างไร")

    col_s1, col_s2 = st.columns([5, 5])
    with col_s1:
        sim_prov = st.selectbox("เลือกจังหวัดที่จะจำลอง:", prov_list, index=default_idx, key="sim_select")
        p_row = df_all[df_all["PROVINCE_CLEAN"] == sim_prov].iloc[0]

        growth_house = st.slider("📈 อัตราการเติบโตของการใช้ไฟบ้าน (%):", 0, 100, 15, step=5)
        growth_ind = st.slider("🏭 อัตราการขยายตัวของโรงงาน/อุตสาหกรรม (%):", 0, 100, 10, step=5)

    with col_s2:
        sim_h = p_row["ELEC_PER_HOUSE"] * (1 + growth_house / 100.0)
        sim_i = p_row["IND_ELEC_RATIO"] * (1 + growth_ind / 100.0)
        
        min_h, max_h = df_all["ELEC_PER_HOUSE"].min(), df_all["ELEC_PER_HOUSE"].max()
        min_i, max_i = df_all["IND_ELEC_RATIO"].min(), df_all["IND_ELEC_RATIO"].max()
        min_hh, max_hh = df_all["AVG_HOUSEHOLD_SIZE"].min(), df_all["AVG_HOUSEHOLD_SIZE"].max()

        norm_h = (sim_h - min_h) / (max_h - min_h)
        norm_i = (sim_i - min_i) / (max_i - min_i)
        norm_u = (max_hh - p_row["AVG_HOUSEHOLD_SIZE"]) / (max_hh - min_hh)
        c_weight = {2: 1.0, 1: 0.75, 0: 0.4}.get(p_row["CLUSTER_ID"], 0.5)

        new_score = np.clip(np.round(((norm_h * 0.35) + (norm_i * 0.25) + (c_weight * 0.25) + (norm_u * 0.15)) * 100, 1), 10.0, 100.0)
        score_diff = np.round(new_score - p_row["EV_SCORE"], 1)

        st.markdown(f"""
            <div style="background:#0f1218; border:1px solid #1e2533; border-radius:12px; padding:20px; text-align:center;">
                <span style="color:#94a3b8; font-size:13px;">ผลการจำลองสำหรับจังหวัด {p_row['PROVINCE_CLEAN']}</span>
                <div style="font-family:'JetBrains Mono'; font-size:36px; font-weight:800; color:#34d399; margin:6px 0;">
                    {new_score} <span style="font-size:18px; font-weight:500; color:{'#10b981' if score_diff >= 0 else '#f43f5e'};">({'+' if score_diff >= 0 else ''}{score_diff})</span>
                </div>
                <div style="font-size:13px; color:#cbd5e1;">คะแนนเดิม: {p_row['EV_SCORE']} คะแนน</div>
            </div>
        """, unsafe_allow_html=True)

        if new_score >= 75 and p_row["EV_SCORE"] < 75:
            st.balloons()
            st.success("🎉 จากการเติบโตดังกล่าว จังหวัดนี้จะยกระดับขึ้นเป็น **Tier 1 (ทำเลทอง)** ทันที!")
        elif new_score >= 55 and p_row["EV_SCORE"] < 55:
            st.info("⬆️ จังหวัดนี้จะยกระดับขึ้นสู่ **Tier 2 (ศักยภาพสูง)**")
        else:
            st.caption("สถานะการลงทุนยังคงอยู่ใน Tier เดิม แต่มี Margin ความคุ้มค่าและปริมาณรถหมุนเวียนสูงขึ้น")

# ----------------- TAB 4: PCA Visual -----------------
with tab4:
    st.subheader("🗺️ แผนภูมิ PCA 2D Cluster Projection")
    st.caption("แสดงพิกัดของทั้ง 77 จังหวัดในมิติ PCA ที่ลดรูปมาจาก 4 ตัวแปรหลัก (อธิบายความแปรปรวน 90.02%)")

    fig_pca = px.scatter(
        df_all,
        x="PCA1",
        y="PCA2",
        color="CLUSTER_NAME",
        hover_name="PROVINCE_CLEAN",
        hover_data={"ELEC_PER_HOUSE": True, "IND_ELEC_RATIO": True, "EV_SCORE": True, "CLUSTER_NAME": False},
        labels={"PCA1": "Principal Component 1 (74.1% variance)", "PCA2": "Principal Component 2 (15.9% variance)"},
        color_discrete_map={
            "Cluster 2: ศูนย์กลางเศรษฐกิจและอุตสาหกรรม (Industrial & Metropolitan Hub)": "#10b981",
            "Cluster 1: เมืองศูนย์กลางภูมิภาคและท่องเที่ยว (Urban & Tourism Hub)": "#3b82f6",
            "Cluster 0: เกษตรกรรมและชุมชนชนบท (Rural & Agricultural)": "#f59e0b"
        }
    )
    fig_pca.update_traces(marker=dict(size=12, line=dict(width=1, color='#ffffff')))
    fig_pca.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Kanit", color="#e2e8f0"),
        xaxis=dict(gridcolor="#1e2533", color="#94a3b8"),
        yaxis=dict(gridcolor="#1e2533", color="#94a3b8"),
        height=550,
        legend=dict(orientation="h", y=-0.15)
    )
    st.plotly_chart(fig_pca, use_container_width=True)
