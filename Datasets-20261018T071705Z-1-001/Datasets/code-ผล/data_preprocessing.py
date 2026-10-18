"""
Data Preprocessing Script for Thailand Population & Housing Statistics (1993 - 2020 / 2536 - 2563)
Source: สำนักงานพัฒนารัฐบาลดิจิทัล (สพร. / DGA) & กรมการปกครอง (DOPA)
"""

import os
import sys
import pandas as pd
import numpy as np

# กำหนด Path ต้นทางและปลายทาง
RAW_DATA_DIR = r"C:\Users\AI\Downloads\statbyyear-fb3phj"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleaned_data")

def ensure_dir(path: str):
    """สร้างโฟลเดอร์หากยังไม่มีอยู่"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[Setup] Created output directory: {path}")

def parse_yymm(series: pd.Series):
    """
    แปลงค่า YYMM เช่น 6312 ->
    YEAR_BE = 2563
    YEAR_CE = 2020
    MONTH = 12
    """
    series_int = series.astype(int)
    yy = series_int // 100
    month = series_int % 100
    year_be = 2500 + yy
    year_ce = year_be - 543
    return year_be, year_ce, month

def clean_common_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    ทำความสะอาดข้อมูลเบื้องต้นที่ใช้ร่วมกันทุกระดับ:
    - ตัดคอลัมน์ว่างด้านหลัง (จาก trailing pipe '|')
    - ตัดช่องว่าง (whitespace) หน้าหลังของคอลัมน์ข้อความ
    - แปลงตัวเลขจาก String ที่มี comma เป็นตัวเลขจำนวนเต็ม (int64)
    - เพิ่มคอลัมน์ปี พ.ศ. (YEAR_BE), ปี ค.ศ. (YEAR_CE), และเดือน (MONTH)
    """
    # 1. ตัดคอลัมน์ที่ว่างทั้งหมด (trailing pipe column)
    df = df.dropna(how="all", axis=1).copy()
    
    # 2. ทำความสะอาดคอลัมน์ประเภท Object (String)
    obj_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in obj_cols:
        # ตัดช่องว่าง
        df[col] = df[col].astype(str).str.strip()
        # ตรวจสอบและแปลงตัวเลขที่มี comma คั่น
        sample_val = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else ""
        if sample_val.replace(",", "").replace("-", "").isdigit():
            cleaned_num = df[col].str.replace(",", "", regex=False)
            df[col] = pd.to_numeric(cleaned_num, errors="coerce").fillna(0).astype("int64")

    # 3. จัดการคอลัมน์ตัวเลข MALE, FEMALE, TOTAL, HOUSE ให้แน่ใจว่าเป็น int64
    for num_col in ["MALE", "FEMALE", "TOTAL", "HOUSE"]:
        if num_col in df.columns and df[num_col].dtype == object:
            df[num_col] = (
                df[num_col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .pipe(pd.to_numeric, errors="coerce")
                .fillna(0)
                .astype("int64")
            )

    # 4. แปลงปีและเดือน
    if "YYMM" in df.columns:
        year_be, year_ce, month = parse_yymm(df["YYMM"])
        df.insert(1, "YEAR_BE", year_be)
        df.insert(2, "YEAR_CE", year_ce)
        df.insert(3, "MONTH", month)

    return df

def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    เพิ่ม Features พื้นฐานสำหรับการวิเคราะห์และ Machine Learning:
    - SEX_RATIO: อัตราส่วนชายต่อหญิง (MALE / FEMALE)
    - AVG_HOUSEHOLD_SIZE: ขนาดครัวเรือนเฉลี่ย (TOTAL / HOUSE)
    - FEMALE_PCT: สัดส่วนประชากรหญิง (%)
    """
    # ป้องกันการหารด้วยศูนย์
    female_nonzero = df["FEMALE"].replace(0, np.nan)
    house_nonzero = df["HOUSE"].replace(0, np.nan)
    total_nonzero = df["TOTAL"].replace(0, np.nan)

    df["SEX_RATIO"] = (df["MALE"] / female_nonzero).round(4)
    df["AVG_HOUSEHOLD_SIZE"] = (df["TOTAL"] / house_nonzero).round(2)
    df["FEMALE_PCT"] = ((df["FEMALE"] / total_nonzero) * 100).round(2)

    return df

def preprocess_province(raw_path: str, output_dir: str):
    """ทำความสะอาดข้อมูลระดับจังหวัด"""
    print("\n" + "="*50)
    print(">>> 1. Processing Province Level (รายจังหวัด)...")
    df = pd.read_csv(raw_path, sep="|", index_col=False, encoding="utf-8")
    raw_rows = len(df)
    df = clean_common_data(df)

    # แยกข้อมูลสรุปรวมทั่วประเทศ (National Total: CC-CODE == 0)
    df_national = df[df["CC-CODE"] == 0].copy()
    df_national = add_derived_features(df_national)
    df_national = df_national.drop(columns=[
        "RCODE-CODE", "RCODE-DESC", "CCAATT-CODE", "CCAATT-DESC", "CCAATTMM-CODE", "CCAATTMM-DESC"
    ], errors="ignore")
    national_out = os.path.join(output_dir, "cleaned_national_summary.csv")
    df_national.sort_values("YEAR_CE").to_csv(national_out, index=False, encoding="utf-8-sig")
    print(f"  - Extracted National Totals: {len(df_national)} rows -> saved to {national_out}")

    # ข้อมูลเฉพาะรายจังหวัด (CC-CODE > 0)
    df_prov = df[df["CC-CODE"] > 0].copy()
    df_prov = add_derived_features(df_prov)
    # ตัดคอลัมน์ระดับอำเภอ ตำบล หมู่บ้าน ที่เป็นค่าว่างทิ้ง
    cols_to_drop = [
        "RCODE-CODE", "RCODE-DESC", "CCAATT-CODE", "CCAATT-DESC", "CCAATTMM-CODE", "CCAATTMM-DESC"
    ]
    df_prov = df_prov.drop(columns=cols_to_drop, errors="ignore")
    
    # จัดเรียงลำดับ
    df_prov = df_prov.sort_values(by=["YEAR_CE", "CC-CODE"]).reset_index(drop=True)
    prov_out = os.path.join(output_dir, "cleaned_province.csv")
    df_prov.to_csv(prov_out, index=False, encoding="utf-8-sig")
    print(f"  - Cleaned Province Data: {raw_rows} raw rows -> {len(df_prov)} clean rows")
    print(f"  - Saved to: {prov_out}")
    return df_prov, df_national

def preprocess_amphoe(raw_path: str, output_dir: str):
    """ทำความสะอาดข้อมูลระดับอำเภอ/เขต"""
    print("\n" + "="*50)
    print(">>> 2. Processing Amphoe/District Level (รายอำเภอ)...")
    df = pd.read_csv(raw_path, sep="|", index_col=False, encoding="utf-8")
    raw_rows = len(df)
    df = clean_common_data(df)

    # กรองเฉพาะระดับอำเภอที่แท้จริง (RCODE-CODE > 0) ตัดยอดรวมระดับจังหวัดและประเทศออก
    df_amp = df[df["RCODE-CODE"] > 0].copy()
    df_amp = add_derived_features(df_amp)

    # ตัดคอลัมน์ระดับตำบลและหมู่บ้านออก
    cols_to_drop = ["CCAATT-CODE", "CCAATT-DESC", "CCAATTMM-CODE", "CCAATTMM-DESC"]
    df_amp = df_amp.drop(columns=cols_to_drop, errors="ignore")

    df_amp = df_amp.sort_values(by=["YEAR_CE", "CC-CODE", "RCODE-CODE"]).reset_index(drop=True)
    amp_out = os.path.join(output_dir, "cleaned_amphoe.csv")
    df_amp.to_csv(amp_out, index=False, encoding="utf-8-sig")
    print(f"  - Cleaned Amphoe Data: {raw_rows} raw rows -> {len(df_amp)} clean rows (removed aggregation rows)")
    print(f"  - Saved to: {amp_out}")
    return df_amp

def preprocess_tambon(raw_path: str, output_dir: str):
    """ทำความสะอาดข้อมูลระดับตำบล"""
    print("\n" + "="*50)
    print(">>> 3. Processing Tambon/Subdistrict Level (รายตำบล)...")
    df = pd.read_csv(raw_path, sep="|", index_col=False, encoding="utf-8")
    raw_rows = len(df)
    df = clean_common_data(df)

    # กรองเฉพาะระดับตำบลที่แท้จริง (CCAATT-CODE > 0)
    df_tam = df[df["CCAATT-CODE"] > 0].copy()
    df_tam = add_derived_features(df_tam)

    # ตัดคอลัมน์หมู่บ้านออก (เนื่องจากไม่มีข้อมูล)
    cols_to_drop = ["CCAATTMM-CODE", "CCAATTMM-DESC"]
    df_tam = df_tam.drop(columns=cols_to_drop, errors="ignore")

    df_tam = df_tam.sort_values(by=["YEAR_CE", "CC-CODE", "RCODE-CODE", "CCAATT-CODE"]).reset_index(drop=True)
    tam_out = os.path.join(output_dir, "cleaned_tambon.csv")
    df_tam.to_csv(tam_out, index=False, encoding="utf-8-sig")
    print(f"  - Cleaned Tambon Data: {raw_rows} raw rows -> {len(df_tam)} clean rows (removed higher aggregation rows)")
    print(f"  - Saved to: {tam_out}")
    return df_tam

def main():
    print("="*60)
    print("Starting Thailand Population & Housing Data Preprocessing Pipeline")
    print("="*60)
    ensure_dir(OUTPUT_DIR)

    prov_file = os.path.join(RAW_DATA_DIR, "raaycchanghwad.csv")
    amp_file = os.path.join(RAW_DATA_DIR, "raay-ameph.csv")
    tam_file = os.path.join(RAW_DATA_DIR, "raaytambl.csv")

    # ตรวจสอบไฟล์ต้นทาง
    for f in [prov_file, amp_file, tam_file]:
        if not os.path.exists(f):
            print(f"[Error] Source file not found: {f}")
            sys.exit(1)

    # ทำการประมวลผลแต่ละระดับ
    df_prov, df_nat = preprocess_province(prov_file, OUTPUT_DIR)
    df_amp = preprocess_amphoe(amp_file, OUTPUT_DIR)
    df_tam = preprocess_tambon(tam_file, OUTPUT_DIR)

    print("\n" + "="*60)
    print("Preprocessing completed successfully!")
    print(f"Output files saved in: {OUTPUT_DIR}")
    print("Summary of clean datasets:")
    print(f"  1. cleaned_national_summary.csv : {len(df_nat):,} rows | {len(df_nat.columns)} columns")
    print(f"  2. cleaned_province.csv         : {len(df_prov):,} rows | {len(df_prov.columns)} columns")
    print(f"  3. cleaned_amphoe.csv           : {len(df_amp):,} rows | {len(df_amp.columns)} columns")
    print(f"  4. cleaned_tambon.csv           : {len(df_tam):,} rows | {len(df_tam.columns)} columns")
    print("="*60)

if __name__ == "__main__":
    main()
