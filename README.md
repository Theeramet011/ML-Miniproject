# 🇹🇭 Thailand Green Energy & EV Site Selection Planner
### Mini Project Machine Learning: การจัดกลุ่มจังหวัดตามพฤติกรรมการใช้พลังงานไฟฟ้าและขนาดเมืองด้วย K-Means Clustering

ระบบวิเคราะห์ทำเลและวางแผนธุรกิจพลังงานสะอาด (สถานีชาร์จรถยนต์ไฟฟ้า EV และ โซลาร์เซลล์หลังคาบ้าน Solar Rooftop) พัฒนาต่อยอดจากการบูรณาการชุดข้อมูลภาครัฐ 2 แหล่ง ครอบคลุมทั้ง 77 จังหวัดในประเทศไทย (ปี พ.ศ. 2563)

---

## 📊 ข้อมูลที่นำมาใช้ (Data Integration)
1. **สถิติจำนวนประชากรและบ้านในประเทศไทย (DOPA):** กรมการปกครอง กระทรวงมหาดไทย ร่วมกับ สำนักงานพัฒนารัฐบาลดิจิทัล (สพร.)
2. **สถิติการจำหน่ายพลังงานไฟฟ้ารายจังหวัด (EPPO):** สำนักงานนโยบายและแผนพลังงาน กระทรวงพลังงาน

---

## 🧠 การสร้างโมเดล Machine Learning (K-Means Clustering)
* **การทำ Feature Engineering:** สกัดเป็น 4 ตัวแปรอัตราส่วนเชิงพฤติกรรม (การใช้ไฟต่อคน, การใช้ไฟต่อหลังคาเรือน, สัดส่วนไฟฟ้าโรงงานอุตสาหกรรม, ขนาดครัวเรือนเฉลี่ย)
* **การปรับสเกล:** `StandardScaler`
* **การหาค่า K ที่เหมาะสม:** Elbow Method ร่วมกับ Silhouette Analysis ได้ข้อสรุปที่ **$K = 3$ กลุ่ม**:
  * **Cluster 0: เกษตรกรรมและชนบท (32 จังหวัด / 41.5%)** เช่น บุรีรัมย์, สุรินทร์, ศรีสะเกษ, แม่ฮ่องสอน
  * **Cluster 1: ศูนย์กลางภูมิภาคและท่องเที่ยว (32 จังหวัด / 41.5%)** เช่น เชียงใหม่, ภูเก็ต, สงขลา, ขอนแก่น
  * **Cluster 2: ศูนย์กลางเศรษฐกิจและอุตสาหกรรม (13 จังหวัด / 16.9%)** เช่น กรุงเทพมหานคร, ชลบุรี, ระยอง, สมุทรปราการ

---

## 💻 เว็บแอปพลิเคชัน (Web Applications)
โปรเจกต์นี้ได้รับการพัฒนาต่อยอดเป็นเว็บแอปพลิเคชัน 2 รูปแบบ:

### 1. 🌐 รูปแบบ HTML + CSS + JavaScript (`webapp-html-js/`)
* **เทคโนโลยี:** HTML5, Tailwind CSS, Chart.js, Lucide Icons, Vanilla JavaScript
* **จุดเด่น:** Standalone Single Page App **เปิดได้ทันทีโดยไม่ต้องรัน Server หรือติดตั้งโปรแกรมใดๆ**
* **วิธีเปิดใช้งาน:** เข้าไปที่โฟลเดอร์ `webapp-html-js` แล้วดับเบิลคลิกเปิดไฟล์ `index.html` บนเบราว์เซอร์

### 2. 🐍 รูปแบบ Python Streamlit (`webapp-streamlit/`)
* **เทคโนโลยี:** Python, Streamlit, Plotly Express & Graph Objects, Pandas
* **จุดเด่น:** สไตล์ Data Science & Business Dashboard พร้อมกราฟ Radar Chart และระบบ What-If Simulator
* **วิธีเปิดใช้งาน:**
  ```bash
  cd webapp-streamlit
  pip install -r requirements.txt
  streamlit run app.py
  ```
  *(หรือดับเบิลคลิกไฟล์ `run_streamlit.bat` บน Windows)*

---

## 📁 โครงสร้างโปรเจกต์ (Project Directory)

```text
ML-Miniproject/
├── webapp-html-js/                     # เว็บแอปพลิเคชันแบบ HTML + CSS + JS
│   ├── index.html                      # หน้าเว็บหลัก
│   ├── app.js                          # ลอจิกการคำนวณคะแนนและควบคุม UI
│   ├── style.css                       # สไตล์และการจัดวาง
│   └── data.js                         # ฐานข้อมูล 77 จังหวัด
│
├── webapp-streamlit/                   # เว็บแอปพลิเคชันแบบ Python Streamlit
│   ├── app.py                          # สคริปต์หลักของ Streamlit
│   ├── business_engine.py              # โมดูลสูตรคำนวณคะแนน EV & Solar
│   ├── clustered_provinces_2563.csv    # ผลลัพธ์ข้อมูล 77 จังหวัดที่จัดกลุ่มแล้ว
│   ├── requirements.txt                # รายการไลบรารีที่ต้องใช้
│   └── run_streamlit.bat               # ไฟล์ Batch สั่งรันด้วยคลิกเดียว
│
├── Datasets-20261018T071705Z-1-001/    # ชุดข้อมูลต้นฉบับและรายงาน
│   └── Datasets/
│       ├── code-ผล/                    # โค้ด ML Pipeline (run_kmeans_pipeline.py) และกราฟรายงาน
│       ├── ข้อมูลทรัพยากร ประชากรในประเทศไทย/
│       └── ไฟฟ้า/
│
├── EV_PLANNER_DETAILED_PLAN.md         # แผนการพัฒนาอย่างละเอียด
└── README.md
```

---

## 👥 ผู้จัดทำ
Mini Project วิชา Machine Learning  
GitHub: [@Theeramet011](https://github.com/Theeramet011)
