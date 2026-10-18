"""
K-Means Clustering Pipeline: Thailand Demographic & Electricity Consumption (2563 / 2020)
Mini Project Machine Learning
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# กำหนดฟอนต์ภาษาไทยสำหรับ Matplotlib บน Windows
plt.rcParams['font.family'] = 'Tahoma'
plt.rcParams['axes.unicode_minus'] = False

# กำหนด Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POPULATION_FILE = os.path.join(BASE_DIR, "cleaned_data", "cleaned_province.csv")
ELECTRICITY_FILE = os.path.join(BASE_DIR, "electricity_consumption_2563.xlsx")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
FIG_DIR = os.path.join(REPORT_DIR, "figures")

os.makedirs(FIG_DIR, exist_ok=True)

print("="*65)
print("  STEP 1: DATA INGESTION & MERGING (โหลดและผสานข้อมูล)")
print("="*65)

# 1. โหลดข้อมูลประชากร (เฉพาะปี 2563)
df_pop = pd.read_csv(POPULATION_FILE)
df_pop_2563 = df_pop[df_pop["YEAR_BE"] == 2563].copy()
print(f"Loaded Population (Year 2563): {len(df_pop_2563)} provinces")

# 2. โหลดข้อมูลการใช้ไฟฟ้า (ปี 2563)
df_elec = pd.read_excel(ELECTRICITY_FILE)
print(f"Loaded Electricity Consumption: {len(df_elec)} provinces")

# 3. Merge ข้อมูลด้วย CC-CODE == รหัสจังหวัด
merged_df = pd.merge(
    df_pop_2563,
    df_elec,
    left_on="CC-CODE",
    right_on="รหัสจังหวัด",
    how="inner"
)
print(f"Merged Result: {len(merged_df)} provinces matched (100% complete)\n")

print("="*65)
print("  STEP 2: FEATURE ENGINEERING (สร้างตัวแปรเพื่อการจัดกลุ่ม)")
print("="*65)

# คำนวณยอดการใช้ไฟฟ้ารวมทุกสาขา
elec_kwh_cols = [c for c in df_elec.columns if "(kWh)" in c]
merged_df["TOTAL_ELEC_KWH"] = merged_df[elec_kwh_cols].sum(axis=1)

# สร้างตัวแปรเชิงพฤติกรรม (Normalized Rates)
# 1. อัตราการใช้ไฟบ้านต่อคน (kWh/person)
merged_df["ELEC_PER_CAPITA"] = (merged_df["บ้านอยู่อาศัย(kWh)"] / merged_df["TOTAL"]).round(2)

# 2. อัตราการใช้ไฟบ้านต่อหลังคาเรือน (kWh/household)
merged_df["ELEC_PER_HOUSE"] = (merged_df["บ้านอยู่อาศัย(kWh)"] / merged_df["HOUSE"]).round(2)

# 3. สัดส่วนการใช้ไฟภาคโรงงานอุตสาหกรรมขนาดใหญ่ (% of total)
merged_df["IND_ELEC_RATIO"] = ((merged_df["กิจการขนาดใหญ่(kWh)"] / merged_df["TOTAL_ELEC_KWH"]) * 100).round(2)

# 4. ขนาดครัวเรือนเฉลี่ย (คน/หลังคาเรือน)
merged_df["AVG_HOUSEHOLD_SIZE"] = (merged_df["TOTAL"] / merged_df["HOUSE"]).round(2)

feature_cols = [
    "ELEC_PER_CAPITA",      # การใช้ไฟต่อหัว
    "ELEC_PER_HOUSE",       # การใช้ไฟต่อบ้าน
    "IND_ELEC_RATIO",       # สัดส่วนไฟอุตสาหกรรม (%)
    "AVG_HOUSEHOLD_SIZE"    # ขนาดครัวเรือน
]

X = merged_df[feature_cols].copy()
print("Selected Features for K-Means:")
for col in feature_cols:
    print(f"  - {col}: Mean={X[col].mean():.2f}, Std={X[col].std():.2f}, Min={X[col].min():.2f}, Max={X[col].max():.2f}")

print("\n" + "="*65)
print("  STEP 3: FEATURE SCALING (ปรับสเกลตัวแปรด้วย StandardScaler)")
print("="*65)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("Scaled feature matrix shape:", X_scaled.shape)
print("Mean after scaling:", np.round(X_scaled.mean(axis=0), 4))
print("Std after scaling:", np.round(X_scaled.std(axis=0), 4))

print("\n" + "="*65)
print("  STEP 4: FINDING OPTIMAL K (Elbow Method & Silhouette Score)")
print("="*65)

k_range = range(2, 9)
inertias = []
sil_scores = []

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    sil = silhouette_score(X_scaled, labels)
    sil_scores.append(sil)
    print(f"K = {k}: Inertia = {km.inertia_:>8.2f} | Silhouette Score = {sil:.4f}")

# บันทึกกราฟ Elbow & Silhouette
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(k_range, inertias, marker='o', linewidth=2.5, color='#1f77b4')
ax1.set_title("Elbow Method (Inertia vs Number of Clusters)", fontsize=13, fontweight='bold')
ax1.set_xlabel("Number of Clusters (K)", fontsize=11)
ax1.set_ylabel("Inertia (Within-Cluster Sum of Squares)", fontsize=11)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.axvline(x=3, color='crimson', linestyle=':', label='Chosen K = 3')
ax1.legend(fontsize=11)

ax2.plot(k_range, sil_scores, marker='s', linewidth=2.5, color='#2ca02c')
ax2.set_title("Silhouette Score vs Number of Clusters", fontsize=13, fontweight='bold')
ax2.set_xlabel("Number of Clusters (K)", fontsize=11)
ax2.set_ylabel("Silhouette Score", fontsize=11)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.axvline(x=3, color='crimson', linestyle=':', label='Chosen K = 3')
ax2.legend(fontsize=11)

plt.tight_layout()
elbow_fig_path = os.path.join(FIG_DIR, "elbow_silhouette_method.png")
plt.savefig(elbow_fig_path, dpi=300)
plt.close()
print(f"\nSaved Elbow & Silhouette chart -> {elbow_fig_path}")

# เลือก K = 3
OPTIMAL_K = 3

print("\n" + "="*65)
print(f"  STEP 5: TRAINING K-MEANS MODEL (K = {OPTIMAL_K})")
print("="*65)

kmeans = KMeans(n_clusters=OPTIMAL_K, random_state=42, n_init=30)
merged_df["CLUSTER_ID"] = kmeans.fit_predict(X_scaled)

# จัดเรียง Cluster ให้เข้าใจง่ายตามระดับความเข้มข้นของการใช้พลังงาน
# ให้ 0 = ชนบท/เกษตร, 1 = เมืองเติบโต/ท่องเที่ยว, 2 = อุตสาหกรรม/มหานคร
cluster_order = (
    merged_df.groupby("CLUSTER_ID")["ELEC_PER_HOUSE"]
    .mean()
    .sort_values()
    .index
)
mapping = {old_id: new_id for new_id, old_id in enumerate(cluster_order)}
merged_df["CLUSTER_ID"] = merged_df["CLUSTER_ID"].map(mapping)

cluster_labels = {
    0: "Cluster 0: เกษตรกรรมและชุมชนชนบท (Rural & Agricultural)",
    1: "Cluster 1: เมืองศูนย์กลางภูมิภาคและท่องเที่ยว (Urban & Tourism Hub)",
    2: "Cluster 2: ศูนย์กลางเศรษฐกิจและอุตสาหกรรม (Industrial & Metropolitan Hub)"
}
merged_df["CLUSTER_NAME"] = merged_df["CLUSTER_ID"].map(cluster_labels)

print("Provinces count per cluster:")
for c_id, count in merged_df["CLUSTER_ID"].value_counts().sort_index().items():
    print(f"  - {cluster_labels[c_id]}: {count} จังหวัด")

print("\n" + "="*65)
print("  STEP 6: VISUALIZATION & CLUSTER PROFILING")
print("="*65)

# ทำ PCA ลดมิติเหลือ 2D เพื่อพล็อตกราฟภาพรวม
pca = PCA(n_components=2, random_state=42)
pca_coords = pca.fit_transform(X_scaled)
merged_df["PCA1"] = pca_coords[:, 0]
merged_df["PCA2"] = pca_coords[:, 1]
print(f"PCA Explained Variance Ratio: PC1={pca.explained_variance_ratio_[0]:.2%}, PC2={pca.explained_variance_ratio_[1]:.2%}")

# พล็อตกราฟที่ 1: PCA 2D Scatter Plot
plt.figure(figsize=(12, 8))
colors = ['#2b83ba', '#abdda4', '#d7191c']
sns.scatterplot(
    data=merged_df,
    x="PCA1",
    y="PCA2",
    hue="CLUSTER_NAME",
    palette=colors,
    s=110,
    alpha=0.9,
    edgecolor="black"
)

# ติดป้ายชื่อจังหวัดสำคัญ
highlight_provinces = [
    "กรุงเทพมหานคร", "จังหวัดระยอง", "จังหวัดชลบุรี", "จังหวัดสมุทรปราการ", "จังหวัดพระนครศรีอยุธยา",
    "จังหวัดเชียงใหม่", "จังหวัดภูเก็ต", "จังหวัดขอนแก่น", "จังหวัดนครราชสีมา", "จังหวัดสงขลา",
    "จังหวัดแม่ฮ่องสอน", "จังหวัดนราธิวาส", "จังหวัดบึงกาฬ", "จังหวัดสกลนคร"
]

for _, row in merged_df.iterrows():
    name = row["CC-DESC"].replace("จังหวัด", "")
    if row["CC-DESC"] in highlight_provinces:
        plt.annotate(
            name,
            (row["PCA1"] + 0.08, row["PCA2"] + 0.08),
            fontsize=10,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.75, edgecolor='gray', linewidth=0.5)
        )

plt.title("การจัดกลุ่มจังหวัดตามพฤติกรรมการใช้พลังงานและขนาดเมือง (K-Means 2D PCA Projection)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel(f"Principal Component 1 ({pca.explained_variance_ratio_[0]:.1%} variance)", fontsize=11)
plt.ylabel(f"Principal Component 2 ({pca.explained_variance_ratio_[1]:.1%} variance)", fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title="กลุ่มจังหวัด (Clusters)", fontsize=10, loc='best')

pca_fig_path = os.path.join(FIG_DIR, "kmeans_clusters_pca.png")
plt.tight_layout()
plt.savefig(pca_fig_path, dpi=300)
plt.close()
print(f"Saved PCA Scatter plot -> {pca_fig_path}")

# พล็อตกราฟที่ 2: Scatter Plot ระหว่าง ค่าไฟต่อบ้าน vs สัดส่วนไฟอุตสาหกรรม
plt.figure(figsize=(11, 7))
sns.scatterplot(
    data=merged_df,
    x="IND_ELEC_RATIO",
    y="ELEC_PER_HOUSE",
    hue="CLUSTER_NAME",
    palette=colors,
    s=120,
    alpha=0.9,
    edgecolor="black"
)

for _, row in merged_df.iterrows():
    name = row["CC-DESC"].replace("จังหวัด", "")
    if row["CC-DESC"] in highlight_provinces:
        plt.annotate(
            name,
            (row["IND_ELEC_RATIO"] + 0.8, row["ELEC_PER_HOUSE"] + 20),
            fontsize=9.5,
            fontweight='bold'
        )

plt.title("พฤติกรรมการใช้ไฟฟ้า: ค่าไฟต่อบ้าน เทียบกับ สัดส่วนไฟฟ้าโรงงานอุตสาหกรรม", fontsize=13, fontweight='bold', pad=15)
plt.xlabel("สัดส่วนไฟฟ้าโรงงานอุตสาหกรรมขนาดใหญ่ (Large Industry Ratio %)", fontsize=11)
plt.ylabel("ปริมาณการใช้ไฟฟ้าเฉลี่ยต่อหลังคาเรือน (kWh/Household)", fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title="กลุ่มจังหวัด (Clusters)", fontsize=10, loc='upper left')

scatter_fig_path = os.path.join(FIG_DIR, "kmeans_scatter_house_vs_industry.png")
plt.tight_layout()
plt.savefig(scatter_fig_path, dpi=300)
plt.close()
print(f"Saved Scatter plot (House vs Industry) -> {scatter_fig_path}")

# คำนวณตารางสรุป Cluster Profile
cluster_summary = merged_df.groupby(["CLUSTER_ID", "CLUSTER_NAME"])[feature_cols].mean().reset_index()
cluster_summary["COUNT_PROVINCES"] = merged_df["CLUSTER_ID"].value_counts().sort_index().values

# เพิ่มตัวอย่างจังหวัดในแต่ละกลุ่ม
sample_provs = []
for c_id in range(OPTIMAL_K):
    prov_names = (
        merged_df[merged_df["CLUSTER_ID"] == c_id]["CC-DESC"]
        .str.replace("จังหวัด", "")
        .head(6)
        .tolist()
    )
    sample_provs.append(", ".join(prov_names))
cluster_summary["SAMPLE_PROVINCES"] = sample_provs

summary_csv_path = os.path.join(REPORT_DIR, "cluster_summary.csv")
cluster_summary.to_csv(summary_csv_path, index=False, encoding="utf-8-sig")
print(f"Saved Cluster Summary -> {summary_csv_path}")

# บันทึกไฟล์ผลลัพธ์หลักที่รวม Cluster Label แล้ว
output_merged_csv = os.path.join(BASE_DIR, "clustered_provinces_2563.csv")
merged_df.to_csv(output_merged_csv, index=False, encoding="utf-8-sig")
print(f"Saved Clustered Provinces Dataset -> {output_merged_csv}")

print("\n" + "="*65)
print("  CLUSTER PROFILES SUMMARY (สรุปผลการจัดกลุ่ม)")
print("="*65)
for _, r in cluster_summary.iterrows():
    print(f"\n[{r['CLUSTER_NAME']}] - จำนวน {r['COUNT_PROVINCES']} จังหวัด")
    print(f"  - ตัวอย่างจังหวัด: {r['SAMPLE_PROVINCES']}")
    print(f"  - ค่าไฟบ้านต่อคน : {r['ELEC_PER_CAPITA']:,.2f} kWh/คน")
    print(f"  - ค่าไฟบ้านต่อหลัง : {r['ELEC_PER_HOUSE']:,.2f} kWh/หลัง")
    print(f"  - สัดส่วนไฟอุตสาหกรรม : {r['IND_ELEC_RATIO']:.2f}%")
    print(f"  - ขนาดครัวเรือนเฉลี่ย : {r['AVG_HOUSEHOLD_SIZE']:.2f} คน/บ้าน")

print("\nPipeline executed successfully!")
