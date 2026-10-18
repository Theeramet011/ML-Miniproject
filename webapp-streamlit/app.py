"""
Thailand Green Energy & EV Site Selection Planner
Streamlit Web Application
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
    page_title="Thailand Green Energy & EV Planner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Kanit', sans-serif;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .stButton>button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load & Cache Dataset
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, "clustered_provinces_2563.csv")
    if not os.path.exists(csv_file):
        # Fallback to Datasets folder
        csv_file = os.path.join(base_dir, "..", "Datasets-20261018T071705Z-1-001", "Datasets", "code-ผล", "clustered_provinces_2563.csv")
    
    df = pd.read_csv(csv_file)
    return calculate_business_scores(df)

df_all = load_data()

# 3. Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/lightning-bolt.png", width=64)
    st.title("⚡ Green Energy Planner")
    st.caption("ระบบวางแผนทำเลธุรกิจพลังงานสะอาดจาก Machine Learning")
    st.divider()

    # เลือกโหมดการวิเคราะห์
    mode = st.radio(
        "🎯 เลือกประเภทธุรกิจ:",
        ("⚡ สถานีชาร์จ EV (EV Charging)", "☀️ โซลาร์เซลล์หลังคาบ้าน (Solar Rooftop)"),
        index=0
    )
    is_ev_mode = "EV" in mode

    st.divider()

    # ตัวกรองกลุ่มคลัสเตอร์
    st.subheader("🔍 ตัวกรองกลุ่ม (Clusters)")
    selected_clusters = st.multiselect(
        "เลือกกลุ่มที่ต้องการแสดง:",
        options=[2, 1, 0],
        default=[2, 1, 0],
        format_func=lambda x: {
            2: "Cluster 2: ศูนย์กลางเศรษฐกิจ/อุตสาหกรรม (13 จังหวัด)",
            1: "Cluster 1: ศูนย์กลางท่องเที่ยว/ภูมิภาค (32 จังหวัด)",
            0: "Cluster 0: ชนบทและเกษตรกรรม (32 จังหวัด)"
        }[x]
    )

    st.divider()
    st.caption("Mini Project Machine Learning • ข้อมูลปี 2563 (DOPA & EPPO)")

# กรองข้อมูลตามกลุ่มที่เลือก
df_filtered = df_all[df_all["CLUSTER_ID"].isin(selected_clusters)].copy()
if is_ev_mode:
    df_filtered = df_filtered.sort_values(by="EV_SCORE", ascending=False).reset_index(drop=True)
else:
    df_filtered = df_filtered.sort_values(by="SOLAR_SCORE", ascending=False).reset_index(drop=True)

# 4. Header & Overview KPIs
st.title("🇹🇭 Thailand Green Energy & EV Site Selection Planner")
st.markdown("ระบบวิเคราะห์ทำเลและวางแผนการลงทุนสถานีชาร์จรถยนต์ไฟฟ้า และศักยภาพโซลาร์เซลล์หลังคาเรือน จากการบูรณาการข้อมูลภาครัฐ 77 จังหวัด")

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

st.divider()

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
        search_query = st.text_input("🔎 ค้นหาชื่อจังหวัด:", "")
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
            label="📥 ดาวน์โหลดตารางข้อมูลนี้ (CSV)",
            data=csv_data,
            file_name=f"thailand_green_energy_ranking_{'ev' if is_ev_mode else 'solar'}.csv",
            mime="text/csv"
        )

    with col_t2:
        st.subheader("🏆 Top 10 จังหวัดคะแนนสูงสุด")
        top10_df = df_filtered.head(10)
        score_col = "EV_SCORE" if is_ev_mode else "SOLAR_SCORE"
        score_label = "คะแนน EV Readiness" if is_ev_mode else "คะแนนศักยภาพโซลาร์"

        fig_bar = px.bar(
            top10_df,
            x=score_col,
            y="PROVINCE_CLEAN",
            orientation="h",
            color="CLUSTER_ID",
            color_continuous_scale="Viridis",
            labels={score_col: score_label, "PROVINCE_CLEAN": "จังหวัด", "CLUSTER_ID": "Cluster"},
            text=score_col
        )
        fig_bar.update_layout(yaxis=dict(autorange="reversed"), height=480, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- TAB 2: Province Deep Dive -----------------
with tab2:
    st.subheader("🔍 วิเคราะห์เจาะลึกศักยภาพรายจังหวัด")
    
    col_d1, col_d2 = st.columns([4, 6])
    
    with col_d1:
        prov_list = df_all["PROVINCE_CLEAN"].tolist()
        default_idx = prov_list.index("กรุงเทพมหานคร") if "กรุงเทพมหานคร" in prov_list else 0
        selected_prov = st.selectbox("เลือกจังหวัดที่ต้องการวิเคราะห์:", prov_list, index=default_idx)
        
        prov_row = df_all[df_all["PROVINCE_CLEAN"] == selected_prov].iloc[0]

        st.markdown(f"### 📍 {prov_row['CC-DESC']}")
        st.info(f"**กลุ่ม:** {prov_row['CLUSTER_NAME']}")

        st.metric(
            label="คะแนนความพร้อม EV Readiness" if is_ev_mode else "คะแนนศักยภาพโซลาร์เซลล์",
            value=f"{prov_row['EV_SCORE'] if is_ev_mode else prov_row['SOLAR_SCORE']} / 100",
            delta=prov_row["EV_TIER"] if is_ev_mode else f"คืนทุน ~{prov_row['SOLAR_PAYBACK_YEARS']} ปี"
        )

        st.markdown("#### 💡 คำแนะนำเชิงกลยุทธ์ (Strategic Advice):")
        if is_ev_mode:
            st.success(f"**หัวชาร์จที่แนะนำ:** {prov_row['CHARGER_TECH']}")
            st.write(f"**ทำเลติดตั้งเป้าหมาย:** {prov_row['TARGET_LOCATIONS']}")
        else:
            st.success(f"**ระยะเวลาคืนทุนโดยประมาณ:** {prov_row['SOLAR_PAYBACK_YEARS']} ปี")
            st.write(f"**ความคุ้มค่า:** เหมาะสำหรับบ้านที่มีค่าไฟเฉลี่ยเดือนละ 2,500 - 4,500 บาทขึ้นไป")

        st.markdown("---")
        st.write(f"• **ประชากร:** {prov_row['TOTAL']:,} คน")
        st.write(f"• **จำนวนบ้าน:** {prov_row['HOUSE']:,} หลังคาเรือน")
        st.write(f"• **ขนาดครัวเรือน:** {prov_row['AVG_HOUSEHOLD_SIZE']} คน/บ้าน")

    with col_d2:
        st.markdown("#### 🕸️ กราฟเรดาร์เปรียบเทียบสถิติกับค่าเฉลี่ยทั้งประเทศ")

        # Normalize metrics for radar (0 - 100)
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
            line_color='#94a3b8'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=prov_values,
            theta=categories,
            fill='toself',
            name=prov_row["PROVINCE_CLEAN"],
            line_color='#10b981'
        ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=450,
            margin=dict(l=40, r=40, t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# ----------------- TAB 3: What-If Simulator -----------------
with tab3:
    st.subheader("💡 แบบจำลองสถานการณ์การเติบโตของเมือง (What-If Simulator)")
    st.write("ทดลองปรับเปลี่ยนพารามิเตอร์การขยายตัวของเมือง เพื่อดูว่าคะแนนความคุ้มค่าในการลงทุนสถานีชาร์จจะเปลี่ยนไปอย่างไร")

    col_s1, col_s2 = st.columns([5, 5])
    with col_s1:
        sim_prov = st.selectbox("เลือกจังหวัดที่จะจำลอง:", prov_list, index=default_idx, key="sim_select")
        p_row = df_all[df_all["PROVINCE_CLEAN"] == sim_prov].iloc[0]

        growth_house = st.slider("📈 อัตราการเติบโตของการใช้ไฟบ้าน (%):", 0, 100, 10, step=5)
        growth_ind = st.slider("🏭 อัตราการขยายตัวของโรงงาน/อุตสาหกรรม (%):", 0, 100, 10, step=5)

    with col_s2:
        # คำนวณค่าจำลอง
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

        st.markdown(f"### ผลการจำลอง: {p_row['PROVINCE_CLEAN']}")
        st.metric(
            label="คะแนน EV Readiness จำลองใหม่",
            value=f"{new_score} คะแนน",
            delta=f"{'+' if score_diff >= 0 else ''}{score_diff} คะแนน"
        )

        if new_score >= 75 and p_row["EV_SCORE"] < 75:
            st.balloons()
            st.success("🎉 จากการเติบโตดังกล่าว จังหวัดนี้จะยกระดับขึ้นเป็น **Tier 1 (ทำเลทอง)** ทันที!")
        elif new_score >= 55 and p_row["EV_SCORE"] < 55:
            st.info("⬆️ จังหวัดนี้จะยกระดับขึ้นสู่ **Tier 2 (ศักยภาพสูง)**")
        else:
            st.write("สถานะการลงทุนยังคงอยู่ใน Tier เดิม แต่มี Margin ความคุ้มค่าสูงขึ้น")

# ----------------- TAB 4: PCA Visual -----------------
with tab4:
    st.subheader("🗺️ แผนภูมิ PCA 2D Cluster Projection")
    st.write("แสดงพิกัดของทั้ง 77 จังหวัดในมิติ PCA ที่ลดรูปมาจาก 4 ตัวแปรหลัก (อธิบายความแปรปรวน 90.02%)")

    fig_pca = px.scatter(
        df_all,
        x="PCA1",
        y="PCA2",
        color="CLUSTER_NAME",
        hover_name="PROVINCE_CLEAN",
        hover_data={"ELEC_PER_HOUSE": True, "IND_ELEC_RATIO": True, "EV_SCORE": True, "CLUSTER_NAME": False},
        labels={"PCA1": "Principal Component 1 (74.1% variance)", "PCA2": "Principal Component 2 (15.9% variance)"},
        color_discrete_sequence=["#2b83ba", "#fdae61", "#d7191c"]
    )
    fig_pca.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
    fig_pca.update_layout(height=550)
    st.plotly_chart(fig_pca, use_container_width=True)
