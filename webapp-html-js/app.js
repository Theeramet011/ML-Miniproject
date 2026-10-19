// Thailand Green Energy & EV Site Selection Planner - Business Logic & UI Controller

// ค่าเฉลี่ยและสถิติทั้งประเทศ
let globalStats = {
    avgHouseElec: 0,
    avgIndRatio: 0,
    avgHouseholdSize: 0,
    minHouse: 0, maxHouse: 0,
    minInd: 0, maxInd: 0,
    minHH: 0, maxHH: 0
};

let processedProvinces = [];
let currentFilter = 'ALL';
let currentMode = 'EV'; // 'EV' or 'SOLAR'
let radarChartInstance = null;
let topBarChartInstance = null;
let selectedProvinceCode = 10; // Default: กรุงเทพฯ

// ฟังก์ชันเริ่มต้นระบบ
function initApp() {
    calculateGlobalMinMax();
    calculateAllScores();
    renderKPICards();
    renderRankingTable();
    initCharts();
    setupEventListeners();
    updateProvinceDeepDive(selectedProvinceCode);
}

// คำนวณ Min/Max และค่าเฉลี่ย
function calculateGlobalMinMax() {
    const houses = PROVINCES_DATA.map(p => p.elec_per_house);
    const inds = PROVINCES_DATA.map(p => p.ind_elec_ratio);
    const hhs = PROVINCES_DATA.map(p => p.avg_household_size);

    globalStats.minHouse = Math.min(...houses);
    globalStats.maxHouse = Math.max(...houses);
    globalStats.minInd = Math.min(...inds);
    globalStats.maxInd = Math.max(...inds);
    globalStats.minHH = Math.min(...hhs);
    globalStats.maxHH = Math.max(...hhs);

    globalStats.avgHouseElec = houses.reduce((a, b) => a + b, 0) / houses.length;
    globalStats.avgIndRatio = inds.reduce((a, b) => a + b, 0) / inds.length;
    globalStats.avgHouseholdSize = hhs.reduce((a, b) => a + b, 0) / hhs.length;
}

// คำนวณคะแนน EV Readiness และ Solar Potential
function calculateAllScores(wHouse = 0.35, wInd = 0.25, wCluster = 0.25, wUrban = 0.15) {
    processedProvinces = PROVINCES_DATA.map(p => {
        // Normalization (0 - 1)
        const normHouse = (p.elec_per_house - globalStats.minHouse) / (globalStats.maxHouse - globalStats.minHouse);
        const normInd = (p.ind_elec_ratio - globalStats.minInd) / (globalStats.maxInd - globalStats.minInd);
        const normUrban = (globalStats.maxHH - p.avg_household_size) / (globalStats.maxHH - globalStats.minHH);
        
        let clusterWeight = 0.40;
        if (p.cluster_id === 2) clusterWeight = 1.00;
        else if (p.cluster_id === 1) clusterWeight = 0.75;

        // สูตร EV Readiness Score (0 - 100)
        const rawEV = (normHouse * wHouse) + (normInd * wInd) + (clusterWeight * wCluster) + (normUrban * wUrban);
        const evScore = Math.min(100, Math.max(10, Math.round(rawEV * 100 * 10) / 10));

        // กำหนด Tier และคำแนะนำหัวชาร์จ
        let evTier = 'Tier 3';
        let evBadgeClass = 'bg-blue-100 text-blue-800 border-blue-300';
        let chargerTech = 'AC Destination Charge (7-22 kW)';
        let targetLocations = 'สถานที่ราชการ, ชุมชนอำเภอเมือง, โรงพยาบาล';

        if (evScore >= 75) {
            evTier = 'Tier 1 (ทำเลทอง)';
            evBadgeClass = 'bg-emerald-100 text-emerald-800 border-emerald-300';
            chargerTech = 'Ultra Fast DC Charge (120-150 kW)';
            targetLocations = 'ห้างสรรพสินค้า, ปั๊มน้ำมันสายหลัก, ย่านคอนโดมิเนียม';
        } else if (evScore >= 55) {
            evTier = 'Tier 2 (ศักยภาพสูง)';
            evBadgeClass = 'bg-amber-100 text-amber-800 border-amber-300';
            chargerTech = 'DC Fast (50-60 kW) + AC (22 kW)';
            targetLocations = 'โรงแรม, รีสอร์ต, คอมมูนิตี้มอลล์, แหล่งท่องเที่ยว';
        }

        // สูตร Solar Potential (0 - 100) & Payback
        const solarScore = Math.min(100, Math.max(15, Math.round((normHouse * 0.75 + (1 - normUrban) * 0.25) * 100 * 10) / 10));
        // คำนวณระยะเวลาคืนทุนโดยประมาณ (4.5 - 8.5 ปี ตามระดับการใช้ไฟบ้าน)
        let payback = (8.5 - (normHouse * 4.0)).toFixed(1);
        if (parseFloat(payback) < 4.0) payback = '4.0';
        if (parseFloat(payback) > 8.5) payback = '8.5';

        return {
            ...p,
            evScore,
            evTier,
            evBadgeClass,
            chargerTech,
            targetLocations,
            solarScore,
            paybackYears: payback
        };
    });

    // เรียงลำดับตามคะแนนโหมดปัจจุบัน
    sortProvinces();
}

function sortProvinces() {
    if (currentMode === 'EV') {
        processedProvinces.sort((a, b) => b.evScore - a.evScore);
    } else {
        processedProvinces.sort((a, b) => b.solarScore - a.solarScore);
    }
}

// อัปเดตการ์ด KPI ด้านบน
function renderKPICards() {
    const topProv = processedProvinces[0];
    const avgScore = (processedProvinces.reduce((sum, p) => sum + (currentMode === 'EV' ? p.evScore : p.solarScore), 0) / processedProvinces.length).toFixed(1);
    const tier1Count = processedProvinces.filter(p => p.evScore >= 75).length;
    const cluster2Count = processedProvinces.filter(p => p.cluster_id === 2).length;

    document.getElementById('kpiTopProvince').innerText = `${topProv.name} (${currentMode === 'EV' ? topProv.evScore : topProv.solarScore} คะแนน)`;
    document.getElementById('kpiAvgScore').innerText = `${avgScore} / 100`;
    document.getElementById('kpiTier1Count').innerText = `${tier1Count} จังหวัด`;
    document.getElementById('kpiCluster2Count').innerText = `${cluster2Count} จังหวัด`;
}

// แสดงตารางอันดับ
function renderRankingTable(searchTerm = '') {
    const tbody = document.getElementById('provinceTableBody');
    tbody.innerHTML = '';

    const filtered = processedProvinces.filter(p => {
        const matchFilter = (currentFilter === 'ALL') || (p.cluster_id.toString() === currentFilter);
        const matchSearch = p.name.includes(searchTerm) || p.fullname.includes(searchTerm);
        return matchFilter && matchSearch;
    });

    filtered.forEach((p, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 cursor-pointer transition border-b border-slate-100 text-sm';
        if (p.code === selectedProvinceCode) {
            tr.className += ' bg-emerald-50/70 font-semibold';
        }

        const score = currentMode === 'EV' ? p.evScore : p.solarScore;
        const subText = currentMode === 'EV' ? p.chargerTech.split(' ')[0] : `คืนทุน ~${p.paybackYears} ปี`;

        let clusterBadgeColor = 'bg-blue-100 text-blue-700';
        if (p.cluster_id === 2) clusterBadgeColor = 'bg-rose-100 text-rose-700';
        else if (p.cluster_id === 1) clusterBadgeColor = 'bg-amber-100 text-amber-700';

        tr.innerHTML = `
            <td class="py-3 px-3 text-slate-500 font-mono text-center">${idx + 1}</td>
            <td class="py-3 px-3">
                <span class="font-medium text-slate-800">${p.name}</span>
                <span class="block text-xs text-slate-400">ประชากร: ${(p.population / 1000).toFixed(0)}k คน</span>
            </td>
            <td class="py-3 px-2 text-center">
                <span class="px-2 py-0.5 rounded-full text-xs font-medium ${clusterBadgeColor}">
                    C${p.cluster_id}
                </span>
            </td>
            <td class="py-3 px-3 text-right">
                <span class="text-base font-bold text-emerald-600">${score}</span>
            </td>
            <td class="py-3 px-3">
                <span class="px-2 py-0.5 rounded-md text-xs border ${p.evBadgeClass}">
                    ${p.evTier}
                </span>
                <span class="block text-[11px] text-slate-500 mt-0.5">${subText}</span>
            </td>
            <td class="py-3 px-2 text-center">
                <button onclick="selectProvince(${p.code})" class="text-xs text-emerald-600 hover:text-emerald-800 font-medium underline">
                    วิเคราะห์
                </button>
            </td>
        `;
        tr.onclick = (e) => {
            if (e.target.tagName !== 'BUTTON') selectProvince(p.code);
        };
        tbody.appendChild(tr);
    });

    document.getElementById('tableCountLabel').innerText = `แสดง ${filtered.length} จาก 77 จังหวัด`;
}

// เลือกจังหวัดเพื่อเจาะลึก
function selectProvince(code) {
    selectedProvinceCode = code;
    renderRankingTable(document.getElementById('searchInput').value);
    updateProvinceDeepDive(code);
}

// อัปเดตส่วน Province Deep Dive
function updateProvinceDeepDive(code) {
    const p = processedProvinces.find(item => item.code === code) || processedProvinces[0];
    
    document.getElementById('deepDiveTitle').innerText = `${p.fullname} (${p.name})`;
    document.getElementById('deepDiveScore').innerText = currentMode === 'EV' ? p.evScore : p.solarScore;
    document.getElementById('deepDiveTier').innerText = p.evTier;
    document.getElementById('deepDiveTier').className = `px-3 py-1 rounded-full text-xs font-semibold border ${p.evBadgeClass}`;
    
    document.getElementById('deepDiveClusterName').innerText = p.cluster_name;
    document.getElementById('deepDiveCharger').innerText = p.chargerTech;
    document.getElementById('deepDiveLocations').innerText = p.targetLocations;
    document.getElementById('deepDivePayback').innerText = `ประมาณ ${p.paybackYears} ปี`;

    document.getElementById('statHouseElec').innerText = `${p.elec_per_house.toLocaleString()} kWh/หลัง`;
    document.getElementById('statCapitaElec').innerText = `${p.elec_per_capita.toLocaleString()} kWh/คน`;
    document.getElementById('statIndRatio').innerText = `${p.ind_elec_ratio}%`;
    document.getElementById('statHouseholdSize').innerText = `${p.avg_household_size} คน/บ้าน`;

    updateRadarChart(p);
}

// สร้างและอัปเดต Radar Chart
function initCharts() {
    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    radarChartInstance = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: ['การใช้ไฟต่อบ้าน', 'สัดส่วนโรงงาน (%)', 'ความเข้มข้นเมือง (คอนโด)', 'การใช้ไฟต่อคน'],
            datasets: [
                {
                    label: 'ค่าเฉลี่ยประเทศ',
                    data: [50, 50, 50, 50],
                    backgroundColor: 'rgba(148, 163, 184, 0.2)',
                    borderColor: 'rgba(148, 163, 184, 0.8)',
                    pointBackgroundColor: 'rgba(148, 163, 184, 1)',
                    borderWidth: 1.5
                },
                {
                    label: 'จังหวัดที่เลือก',
                    data: [75, 60, 80, 70],
                    backgroundColor: 'rgba(16, 185, 129, 0.25)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    pointBackgroundColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: { display: false, stepSize: 25 },
                    pointLabels: { font: { family: 'Kanit', size: 11 } }
                }
            },
            plugins: {
                legend: { position: 'bottom', labels: { font: { family: 'Kanit' } } }
            }
        }
    });

    updateTopBarChart();
}

function updateRadarChart(p) {
    if (!radarChartInstance) return;

    // Normalize to 0-100 scale for comparison
    const norm = (val, min, max) => Math.min(100, Math.max(0, Math.round(((val - min) / (max - min)) * 100)));

    const selectedData = [
        norm(p.elec_per_house, globalStats.minHouse, globalStats.maxHouse),
        norm(p.ind_elec_ratio, globalStats.minInd, globalStats.maxInd),
        norm(globalStats.maxHH - p.avg_household_size, 0, globalStats.maxHH - globalStats.minHH),
        norm(p.elec_per_capita, 300, 2100)
    ];

    const avgData = [
        norm(globalStats.avgHouseElec, globalStats.minHouse, globalStats.maxHouse),
        norm(globalStats.avgIndRatio, globalStats.minInd, globalStats.maxInd),
        norm(globalStats.maxHH - globalStats.avgHouseholdSize, 0, globalStats.maxHH - globalStats.minHH),
        norm(750, 300, 2100)
    ];

    radarChartInstance.data.datasets[0].data = avgData;
    radarChartInstance.data.datasets[1].label = p.name;
    radarChartInstance.data.datasets[1].data = selectedData;
    radarChartInstance.update();
}

function updateTopBarChart() {
    const top10 = processedProvinces.slice(0, 10);
    const ctxBar = document.getElementById('topBarChart').getContext('2d');

    if (topBarChartInstance) {
        topBarChartInstance.destroy();
    }

    topBarChartInstance = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: top10.map(p => p.name),
            datasets: [{
                label: currentMode === 'EV' ? 'คะแนนความพร้อม EV' : 'คะแนนศักยภาพโซลาร์',
                data: top10.map(p => currentMode === 'EV' ? p.evScore : p.solarScore),
                backgroundColor: top10.map(p => p.cluster_id === 2 ? '#f43f5e' : (p.cluster_id === 1 ? '#f59e0b' : '#3b82f6')),
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: { min: 0, max: 100, ticks: { font: { family: 'Kanit' } } },
                y: { ticks: { font: { family: 'Kanit' } } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// ตั้งค่า Event Listeners
function setupEventListeners() {
    // Mode Switcher
    document.getElementById('btnModeEV').addEventListener('click', () => {
        setMode('EV');
    });
    document.getElementById('btnModeSolar').addEventListener('click', () => {
        setMode('SOLAR');
    });

    // Cluster Filter Buttons
    const filterButtons = document.querySelectorAll('.cluster-filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('bg-emerald-600', 'text-white'));
            filterButtons.forEach(b => b.classList.add('bg-slate-100', 'text-slate-600'));
            btn.classList.remove('bg-slate-100', 'text-slate-600');
            btn.classList.add('bg-emerald-600', 'text-white');
            currentFilter = btn.dataset.cluster;
            renderRankingTable(document.getElementById('searchInput').value);
        });
    });

    // Search Input
    document.getElementById('searchInput').addEventListener('input', (e) => {
        renderRankingTable(e.target.value.trim());
    });

    // What-If Sliders
    const sliderHouse = document.getElementById('sliderHouseGrowth');
    const sliderInd = document.getElementById('sliderIndGrowth');

    function handleWhatIf() {
        const houseGrowth = parseFloat(sliderHouse.value);
        const indGrowth = parseFloat(sliderInd.value);

        document.getElementById('valHouseGrowth').innerText = `+${houseGrowth}%`;
        document.getElementById('valIndGrowth').innerText = `+${indGrowth}%`;

        // คำนวณผลกระทบต่อจังหวัดที่เลือก
        const p = processedProvinces.find(item => item.code === selectedProvinceCode);
        if (p) {
            const simulatedHouse = p.elec_per_house * (1 + houseGrowth / 100);
            const simulatedInd = p.ind_elec_ratio * (1 + indGrowth / 100);
            
            const normH = (simulatedHouse - globalStats.minHouse) / (globalStats.maxHouse - globalStats.minHouse);
            const normI = (simulatedInd - globalStats.minInd) / (globalStats.maxInd - globalStats.minInd);
            const normU = (globalStats.maxHH - p.avg_household_size) / (globalStats.maxHH - globalStats.minHH);
            const cWeight = p.cluster_id === 2 ? 1.0 : (p.cluster_id === 1 ? 0.75 : 0.4);

            const newScore = Math.min(100, Math.round(((normH * 0.35) + (normI * 0.25) + (cWeight * 0.25) + (normU * 0.15)) * 1000) / 10);
            const scoreDiff = (newScore - p.evScore).toFixed(1);

            document.getElementById('simResultScore').innerText = `${newScore} คะแนน`;
            document.getElementById('simResultDiff').innerText = `(${scoreDiff >= 0 ? '+' : ''}${scoreDiff})`;
            document.getElementById('simResultDiff').className = scoreDiff >= 0 ? 'text-emerald-600 font-bold' : 'text-rose-600 font-bold';
        }
    }

    sliderHouse.addEventListener('input', handleWhatIf);
    sliderInd.addEventListener('input', handleWhatIf);

    // Export CSV Button
    document.getElementById('btnExportCSV').addEventListener('click', exportCSV);
}

function setMode(mode) {
    currentMode = mode;
    const btnEV = document.getElementById('btnModeEV');
    const btnSolar = document.getElementById('btnModeSolar');

    if (mode === 'EV') {
        btnEV.className = 'flex-1 py-2 px-3 text-sm font-semibold rounded-lg bg-emerald-600 text-white shadow-sm transition';
        btnSolar.className = 'flex-1 py-2 px-3 text-sm font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
        document.getElementById('modeTitle').innerText = 'ระบบวิเคราะห์ทำเลสถานีชาร์จรถยนต์ไฟฟ้า (EV Charging Stations)';
    } else {
        btnSolar.className = 'flex-1 py-2 px-3 text-sm font-semibold rounded-lg bg-emerald-600 text-white shadow-sm transition';
        btnEV.className = 'flex-1 py-2 px-3 text-sm font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
        document.getElementById('modeTitle').innerText = 'ระบบวิเคราะห์ศักยภาพโซลาร์เซลล์หลังคาบ้าน (Solar Rooftop)';
    }

    sortProvinces();
    renderKPICards();
    renderRankingTable(document.getElementById('searchInput').value);
    updateTopBarChart();
    updateProvinceDeepDive(selectedProvinceCode);
}

// ฟังก์ชันดาวน์โหลดรายงาน CSV
function exportCSV() {
    let csvContent = 'data:text/csv;charset=utf-8,\uFEFF';
    csvContent += 'รหัสจังหวัด,ชื่อจังหวัด,กลุ่มคลัสเตอร์,คะแนน EV,Tier สถานีชาร์จ,คำแนะนำหัวชาร์จ,คะแนนโซลาร์,ระยะเวลาคืนทุน(ปี),ค่าไฟบ้านต่อหลัง(kWh),สัดส่วนโรงงาน(%)\n';

    processedProvinces.forEach(p => {
        const row = [
            p.code,
            `"${p.fullname}"`,
            p.cluster_id,
            p.evScore,
            `"${p.evTier}"`,
            `"${p.chargerTech}"`,
            p.solarScore,
            p.paybackYears,
            p.elec_per_house,
            p.ind_elec_ratio
        ].join(',');
        csvContent += row + '\n';
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `thailand_green_energy_planner_${currentMode.toLowerCase()}_2563.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// รันเมื่อโหลดหน้าเสร็จ
window.onload = initApp;
