"""
Business Scoring Engine for Thailand Green Energy & EV Site Selection Planner
Calculates EV Readiness Index and Solar Rooftop Potential from K-Means Clustered Dataset
"""

import pandas as pd
import numpy as np

def calculate_business_scores(df: pd.DataFrame, w_house=0.35, w_ind=0.25, w_cluster=0.25, w_urban=0.15) -> pd.DataFrame:
    """คำนวณคะแนน EV Readiness และ Solar Potential จากตัวแปรทางสถิติ"""
    df = df.copy()

    # ลบคำว่า "จังหวัด" ออกจากชื่อถ้ามี
    df["PROVINCE_CLEAN"] = df["CC-DESC"].astype(str).str.replace("จังหวัด", "").str.strip()

    # Normalization (0 ถึง 1)
    min_h, max_h = df["ELEC_PER_HOUSE"].min(), df["ELEC_PER_HOUSE"].max()
    min_ind, max_ind = df["IND_ELEC_RATIO"].min(), df["IND_ELEC_RATIO"].max()
    min_hh, max_hh = df["AVG_HOUSEHOLD_SIZE"].min(), df["AVG_HOUSEHOLD_SIZE"].max()

    norm_house = (df["ELEC_PER_HOUSE"] - min_h) / (max_h - min_h)
    norm_ind = (df["IND_ELEC_RATIO"] - min_ind) / (max_ind - min_ind)
    norm_urban = (max_hh - df["AVG_HOUSEHOLD_SIZE"]) / (max_hh - min_hh)

    # Cluster Weighting
    cluster_weights = df["CLUSTER_ID"].map({2: 1.00, 1: 0.75, 0: 0.40}).fillna(0.5)

    # 1. คำนวณคะแนน EV Readiness Score (0 - 100)
    raw_ev = (norm_house * w_house) + (norm_ind * w_ind) + (cluster_weights * w_cluster) + (norm_urban * w_urban)
    df["EV_SCORE"] = np.clip(np.round(raw_ev * 100, 1), 10.0, 100.0)

    # จัดกลุ่ม Tier และเทคโนโลยีหัวชาร์จ
    def get_ev_tier(score):
        if score >= 75:
            return "Tier 1 (ทำเลทอง)"
        elif score >= 55:
            return "Tier 2 (ศักยภาพสูง)"
        else:
            return "Tier 3 (รองรับทั่วไป)"

    def get_charger_tech(score):
        if score >= 75:
            return "Ultra Fast DC (120-150 kW)"
        elif score >= 55:
            return "Fast DC (50-60 kW) + AC 22 kW"
        else:
            return "AC Destination (7-22 kW)"

    def get_target_locations(score):
        if score >= 75:
            return "ห้างสรรพสินค้า, ปั๊มน้ำมันสายหลัก, ย่านคอนโดมิเนียม"
        elif score >= 55:
            return "โรงแรม, รีสอร์ต, จุดแวะพักเมืองท่องเที่ยว"
        else:
            return "สถานที่ราชการ, ชุมชนอำเภอเมือง"

    df["EV_TIER"] = df["EV_SCORE"].apply(get_ev_tier)
    df["CHARGER_TECH"] = df["EV_SCORE"].apply(get_charger_tech)
    df["TARGET_LOCATIONS"] = df["EV_SCORE"].apply(get_target_locations)

    # 2. คำนวณคะแนน Solar Potential (0 - 100) & Payback
    raw_solar = (norm_house * 0.75) + ((1 - norm_urban) * 0.25)
    df["SOLAR_SCORE"] = np.clip(np.round(raw_solar * 100, 1), 15.0, 100.0)

    # คำนวณระยะเวลาคืนทุนโดยประมาณ (4.5 - 8.5 ปี ตามระดับการใช้ไฟบ้าน)
    payback = (8.5 - (norm_house * 4.0)).round(1)
    df["SOLAR_PAYBACK_YEARS"] = np.clip(payback, 4.0, 8.5)

    return df
