// CAMPUS CARBON — Application Controller (Campus-Centric v2.0)
let currentCampusId = null;
let currentAssessmentId = null;
let currentAssessmentData = null;
let currentCampusData = null;

let waterfallChartInstance = null;
let scopeDonutChartInstance = null;
let scopeDonutChartTabInstance = null;
let buildingBarChartInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
  lucide.createIcons();
  updateCampusAreaCalculations();
  updateCampusPopCalculations();
  renderNewCampusBuildingRows();
  await loadCampuses();
  runLiveSimulation();
});

// --- Toast Notification Helper ---
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  const bgClass = type === 'success' ? 'bg-emerald-600 text-white' : type === 'error' ? 'bg-rose-600 text-white' : 'bg-slate-900 text-white';
  const iconName = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-triangle' : 'info';

  toast.className = `flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-xl text-xs font-bold transition-all duration-300 transform translate-y-2 pointer-events-auto ${bgClass}`;
  toast.innerHTML = `<i data-lucide="${iconName}" class="w-4 h-4"></i><span>${message}</span>`;
  container.appendChild(toast);
  lucide.createIcons();

  setTimeout(() => {
    toast.classList.add('opacity-0', '-translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// --- Navigation Tab Switching ---
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  const targetTab = document.getElementById(`tab-${tabId}`);
  if (targetTab) targetTab.classList.remove('hidden');

  const btn = document.querySelector(`[data-tab="${tabId}"]`);
  if (btn) btn.classList.add('active');

  lucide.createIcons();

  if (tabId === 'visualizations') renderDetailedCharts();
  if (tabId === 'building-analytics') loadBuildingAnalytics();
  if (tabId === 'recommendations') loadRecommendations();
  if (tabId === 'benchmarks') loadBenchmarks();
  if (tabId === 'factors') loadEmissionFactors();
  if (tabId === 'carbon-accounting') loadCarbonAccountingLogs();
  if (tabId === 'population-distribution') loadPopulationDistributionTable();
  if (tabId === 'campus-data-entry') refreshCampusDataEntryStudio();
}

function switchCampusActTab(tabId) {
  document.querySelectorAll('.cact-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.cact-tab').forEach(el => {
    el.classList.remove('active', 'bg-emerald-50', 'text-emerald-800', 'border-emerald-200');
    el.classList.add('bg-slate-100', 'text-slate-700');
  });

  const target = document.getElementById(tabId);
  if (target) target.classList.remove('hidden');

  const btn = document.querySelector(`[data-cact="${tabId}"]`);
  if (btn) {
    btn.classList.add('active', 'bg-emerald-50', 'text-emerald-800', 'border-emerald-200');
    btn.classList.remove('bg-slate-100', 'text-slate-700');
  }

  loadAllActivityLists();
}

// --- Data Loading & Campus Switcher ---
async function loadCampuses() {
  try {
    const res = await fetch('/api/campuses/');
    const campuses = await res.json();
    const select = document.getElementById('campusSelect');
    select.innerHTML = '';

    campuses.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = `${c.name} (${c.campus_type})`;
      select.appendChild(opt);
    });

    if (campuses.length > 0) {
      if (!currentCampusId || !campuses.some(c => c.id === currentCampusId)) {
        currentCampusId = campuses[0].id;
      }
      select.value = currentCampusId;
      await loadAssessments(currentCampusId);
    }
  } catch (err) {
    console.error('Error loading campuses:', err);
    showToast('Failed to load campuses from server.', 'error');
  }
}

async function loadAssessments(campusId) {
  try {
    const res = await fetch(`/api/assessments/?campus_id=${campusId}`);
    const assessments = await res.json();
    const select = document.getElementById('assessmentSelect');
    select.innerHTML = '';

    assessments.forEach(a => {
      const opt = document.createElement('option');
      opt.value = a.id;
      opt.textContent = `${a.reporting_year} Assessment (${a.status})`;
      select.appendChild(opt);
    });

    if (assessments.length > 0) {
      currentAssessmentId = assessments[0].id;
      await refreshAssessmentDashboard();
    }
  } catch (err) {
    console.error('Error loading assessments:', err);
  }
}

async function onCampusChange() {
  currentCampusId = parseInt(document.getElementById('campusSelect').value);
  await loadAssessments(currentCampusId);
}

async function onAssessmentChange() {
  currentAssessmentId = parseInt(document.getElementById('assessmentSelect').value);
  await refreshAssessmentDashboard();
}

async function refreshAssessmentDashboard() {
  if (!currentAssessmentId || !currentCampusId) return;

  try {
    const res = await fetch(`/api/assessments/${currentAssessmentId}`);
    const asm = await res.json();
    currentAssessmentData = asm;

    const campusRes = await fetch(`/api/campuses/${currentCampusId}`);
    const campus = await campusRes.json();
    currentCampusData = campus;

    // Populate Top Dashboard Info
    document.getElementById('dashCampusName').textContent = campus.name;
    document.getElementById('dashCampusType').textContent = campus.campus_type;
    document.getElementById('dashReportingYear').textContent = asm.reporting_year;
    document.getElementById('dashLocation').textContent = `${campus.city || 'India'} | Standard: ${asm.methodology}`;

    // Area & Built-up Area
    document.getElementById('dashAreaBoth').textContent = `${campus.area.toFixed(2)} ${campus.area_unit}`;
    document.getElementById('dashAreaSqm').textContent = `(${campus.area_sqm.toLocaleString()} m²)`;

    document.getElementById('dashBuiltUpAreaBoth').textContent = `${campus.calculated_built_up_area_acres.toFixed(2)} acres (${campus.built_up_percentage}%)`;
    document.getElementById('dashBuiltUpSqm').textContent = `(${campus.calculated_built_up_area_sqm.toLocaleString()} m²)`;

    // Population
    document.getElementById('dashTotalPop').textContent = `${campus.population.toLocaleString()} Total`;
    document.getElementById('dashPopBreakdown').textContent = `${campus.total_student_population.toLocaleString()} Students | ${campus.total_staff_population.toLocaleString()} Staff`;

    // Buildings Count
    document.getElementById('dashBuildingsCount').textContent = `${campus.buildings.length} Buildings`;
    const pill = document.getElementById('bldCountPill');
    if (pill) pill.textContent = `${campus.buildings.length} Buildings Configured`;

    // 5 Major KPI Cards
    const s = asm.summary || {
      gross_emissions: 0, eligible_reductions: 0, net_footprint: 0,
      scope1: 0, scope2: 0, scope3: 0,
      gross_per_person: 0, net_per_person: 0, gross_per_area: 0, net_per_area: 0,
      renewable_percentage: 0, waste_diversion_rate: 0
    };

    document.getElementById('dashGrossEmissions').textContent = s.gross_emissions.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('dashPositiveEmissions').textContent = s.gross_emissions.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('dashEligibleReductions').textContent = `-${s.eligible_reductions.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById('dashNetFootprint').textContent = s.net_footprint.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('dashNetPerPerson').textContent = s.net_per_person.toFixed(4);

    document.getElementById('dashScope1').textContent = s.scope1.toFixed(2);
    document.getElementById('dashScope2').textContent = s.scope2.toFixed(2);
    document.getElementById('dashScope3').textContent = s.scope3.toFixed(2);

    document.getElementById('dashGrossPerArea').textContent = (s.gross_per_area * 1000).toFixed(2);
    document.getElementById('dashNetPerArea').textContent = (s.net_per_area * 1000).toFixed(2);
    document.getElementById('dashRenewablePct').textContent = `${s.renewable_percentage.toFixed(1)}%`;
    document.getElementById('dashWasteDivRate').textContent = `${s.waste_diversion_rate.toFixed(1)}%`;

    // Populate Sub-views & Visualizations
    renderBuildingsInventoryTable(campus.buildings, campus.calculated_built_up_area_sqm);
    populateCanteenBuildingSelector(campus.buildings);
    renderDashboardCharts(s);
    refreshCampusDataEntryStudio();
    loadAllActivityLists();
    runLiveSimulation();

  } catch (err) {
    console.error('Error refreshing assessment:', err);
  }
}

// --- Campus & Buildings Inventory View ---
function renderBuildingsInventoryTable(buildings, targetBuiltUpSqm) {
  const tbody = document.getElementById('buildingsTableBody');
  if (!tbody) return;

  tbody.innerHTML = '';
  let totalBldArea = 0;

  buildings.forEach(b => {
    totalBldArea += b.built_up_area_sqm;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="p-3 font-bold text-slate-900">${b.building_code || '-'}</td>
      <td class="p-3 font-semibold text-slate-800">${b.name}</td>
      <td class="p-3"><span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-xs">${b.building_type}</span></td>
      <td class="p-3">${b.floors}</td>
      <td class="p-3 font-bold">${b.built_up_area_sqm.toLocaleString()} m²</td>
      <td class="p-3">${b.occupancy.toLocaleString()} occupants</td>
      <td class="p-3 text-slate-500">${b.description || '-'}</td>
    `;
    tbody.appendChild(tr);
  });

  const areaTargetEl = document.getElementById('areaRecalcTarget');
  const areaActualEl = document.getElementById('areaRecalcActual');
  const warningEl = document.getElementById('areaWarningBadge');

  if (areaTargetEl) areaTargetEl.textContent = `${targetBuiltUpSqm.toLocaleString()} m²`;
  if (areaActualEl) areaActualEl.textContent = `${totalBldArea.toLocaleString()} m²`;

  if (warningEl) {
    if (totalBldArea > targetBuiltUpSqm) {
      warningEl.classList.remove('hidden');
    } else {
      warningEl.classList.add('hidden');
    }
  }

  lucide.createIcons();
}

function populateCanteenBuildingSelector(buildings) {
  const select = document.getElementById('cCanteenBuilding');
  if (!select) return;
  select.innerHTML = '<option value="">-- Campus Wide (General Canteen) --</option>';
  buildings.forEach(b => {
    const opt = document.createElement('option');
    opt.value = b.id;
    opt.textContent = `${b.building_code ? '[' + b.building_code + '] ' : ''}${b.name}`;
    select.appendChild(opt);
  });
}

// --- Campus Activity Data Entry Studio Controller ---
function refreshCampusDataEntryStudio() {
  if (!currentCampusData) return;

  document.getElementById('entryCampusTitle').textContent = `Campus: ${currentCampusData.name}`;
  document.getElementById('entryYearBadge').textContent = `Assessment Year: ${currentAssessmentData ? currentAssessmentData.reporting_year : 2025}`;

  // Check which negative activities are enabled
  const neg = currentCampusData.negative_activities || {};

  const btnSolar = document.getElementById('tabBtnSolar');
  const btnWaterCons = document.getElementById('tabBtnWaterCons');
  const btnWaterBodies = document.getElementById('tabBtnWaterBodies');
  const btnAnimals = document.getElementById('tabBtnAnimals');
  const btnGreenery = document.getElementById('tabBtnGreenery');

  if (btnSolar) neg.solar_plant ? btnSolar.classList.remove('hidden') : btnSolar.classList.add('hidden');
  if (btnWaterCons) neg.water_conservation ? btnWaterCons.classList.remove('hidden') : btnWaterCons.classList.add('hidden');
  if (btnWaterBodies) neg.water_bodies ? btnWaterBodies.classList.remove('hidden') : btnWaterBodies.classList.add('hidden');
  if (btnAnimals) neg.animals ? btnAnimals.classList.remove('hidden') : btnAnimals.classList.add('hidden');
  if (btnGreenery) neg.gardening ? btnGreenery.classList.remove('hidden') : btnGreenery.classList.add('hidden');
}

// --- Population Distribution by Building Controller ---
async function loadPopulationDistributionTable() {
  if (!currentCampusId) return;

  const res = await fetch(`/api/campuses/${currentCampusId}/buildings`);
  const buildings = await res.json();
  const tbody = document.getElementById('popDistributionTableBody');
  if (!tbody) return;

  tbody.innerHTML = '';
  buildings.forEach(b => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="p-3 font-bold text-slate-900">${b.building_code}</td>
      <td class="p-3 font-semibold text-slate-800">${b.name}</td>
      <td class="p-3"><span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[10px]">${b.building_type}</span></td>
      <td class="p-3">${b.built_up_area_sqm.toLocaleString()} m²</td>
      <td class="p-2"><input type="number" id="pop_on_${b.id}" value="${b.students_on_campus}" oninput="recalcAllocatedPopTable()" min="0" class="w-20 bg-slate-50 border border-slate-300 rounded p-1 text-xs outline-none"></td>
      <td class="p-2"><input type="number" id="pop_off_${b.id}" value="${b.students_off_campus}" oninput="recalcAllocatedPopTable()" min="0" class="w-20 bg-slate-50 border border-slate-300 rounded p-1 text-xs outline-none"></td>
      <td class="p-2"><input type="number" id="pop_fac_${b.id}" value="${b.faculty_count}" oninput="recalcAllocatedPopTable()" min="0" class="w-20 bg-slate-50 border border-slate-300 rounded p-1 text-xs outline-none"></td>
      <td class="p-2"><input type="number" id="pop_non_${b.id}" value="${b.non_teaching_count}" oninput="recalcAllocatedPopTable()" min="0" class="w-20 bg-slate-50 border border-slate-300 rounded p-1 text-xs outline-none"></td>
      <td class="p-3 text-right font-bold text-slate-900" id="pop_tot_${b.id}">${b.occupancy}</td>
    `;
    tbody.appendChild(tr);
  });

  recalcAllocatedPopTable();
}

function recalcAllocatedPopTable() {
  if (!currentCampusData) return;
  const buildings = currentCampusData.buildings || [];
  let totalAllocated = 0;

  buildings.forEach(b => {
    const on = parseInt(document.getElementById(`pop_on_${b.id}`)?.value) || 0;
    const off = parseInt(document.getElementById(`pop_off_${b.id}`)?.value) || 0;
    const fac = parseInt(document.getElementById(`pop_fac_${b.id}`)?.value) || 0;
    const non = parseInt(document.getElementById(`pop_non_${b.id}`)?.value) || 0;

    const bldTot = on + off + fac + non;
    const totEl = document.getElementById(`pop_tot_${b.id}`);
    if (totEl) totEl.textContent = bldTot.toLocaleString();
    totalAllocated += bldTot;
  });

  const targetPop = currentCampusData.population;
  document.getElementById('popReconcileTarget').textContent = targetPop.toLocaleString();
  document.getElementById('popReconcileCurrent').textContent = totalAllocated.toLocaleString();

  const statusEl = document.getElementById('popReconcileStatus');
  if (totalAllocated === targetPop) {
    statusEl.innerHTML = '<i data-lucide="check-circle" class="w-5 h-5 text-emerald-600"></i><span class="text-emerald-700">Allocations perfectly match campus population!</span>';
  } else {
    statusEl.innerHTML = `<i data-lucide="alert-triangle" class="w-5 h-5 text-amber-600"></i><span class="text-amber-700">Warning: Building allocation (${totalAllocated.toLocaleString()}) does not match Campus Population (${targetPop.toLocaleString()})</span>`;
  }
  lucide.createIcons();
}

async function saveBuildingPopulationDistribution() {
  if (!currentCampusData) return;
  const buildings = currentCampusData.buildings || [];
  const payload = buildings.map(b => ({
    building_id: b.id,
    students_on_campus: parseInt(document.getElementById(`pop_on_${b.id}`)?.value) || 0,
    students_off_campus: parseInt(document.getElementById(`pop_off_${b.id}`)?.value) || 0,
    faculty_count: parseInt(document.getElementById(`pop_fac_${b.id}`)?.value) || 0,
    non_teaching_count: parseInt(document.getElementById(`pop_non_${b.id}`)?.value) || 0,
    other_occupants: 0
  }));

  try {
    const res = await fetch(`/api/campuses/${currentCampusId}/buildings/population`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.matches) {
      showToast('Building population allocations saved successfully!', 'success');
    } else {
      showToast('Saved with warning: Allocations do not equal campus total population.', 'error');
    }
    await refreshAssessmentDashboard();
  } catch (err) {
    console.error('Error saving building populations:', err);
    showToast('Failed to save population allocations.', 'error');
  }
}

// --- Dynamic Campus Creation Form Helpers ---
function openNewCampusModal() {
  document.getElementById('newCampusModal').classList.remove('hidden');
  updateCampusAreaCalculations();
  updateCampusPopCalculations();
  renderNewCampusBuildingRows();
}

function closeNewCampusModal() {
  document.getElementById('newCampusModal').classList.add('hidden');
}

function updateCampusAreaCalculations() {
  const areaVal = parseFloat(document.getElementById('wizCampusArea')?.value) || 0;
  const unit = document.getElementById('wizCampusAreaUnit')?.value || 'Acres';
  const pct = parseFloat(document.getElementById('wizBuiltUpPct')?.value) || 0;

  let areaAcres = 0;
  let areaSqm = 0;

  if (unit === 'Acres') {
    areaAcres = areaVal;
    areaSqm = areaVal * 4046.856;
  } else {
    areaSqm = areaVal;
    areaAcres = areaVal / 4046.856;
  }

  const builtUpAcres = areaAcres * (pct / 100.0);
  const builtUpSqm = areaSqm * (pct / 100.0);

  const dispTotal = document.getElementById('dispTotalAreaStr');
  const dispBuilt = document.getElementById('dispBuiltUpAreaStr');

  if (dispTotal) dispTotal.textContent = `${areaAcres.toFixed(2)} acres (${Math.round(areaSqm).toLocaleString()} m²)`;
  if (dispBuilt) dispBuilt.textContent = `${builtUpAcres.toFixed(2)} acres (${Math.round(builtUpSqm).toLocaleString()} m²)`;
}

function updateCampusPopCalculations() {
  const on = parseInt(document.getElementById('wizPopStudentsOn')?.value) || 0;
  const off = parseInt(document.getElementById('wizPopStudentsOff')?.value) || 0;
  const fac = parseInt(document.getElementById('wizPopFaculty')?.value) || 0;
  const non = parseInt(document.getElementById('wizPopNonTeaching')?.value) || 0;

  const totalStudents = on + off;
  const totalStaff = fac + non;
  const totalPop = totalStudents + totalStaff;

  const dispStud = document.getElementById('dispTotalStudents');
  const dispStaff = document.getElementById('dispTotalStaff');
  const dispPop = document.getElementById('dispTotalPop');

  if (dispStud) dispStud.textContent = totalStudents.toLocaleString();
  if (dispStaff) dispStaff.textContent = totalStaff.toLocaleString();
  if (dispPop) dispPop.textContent = totalPop.toLocaleString();
}

function renderNewCampusBuildingRows() {
  const count = parseInt(document.getElementById('wizNumBuildings')?.value) || 1;
  const container = document.getElementById('wizBuildingsListPreview');
  if (!container) return;

  const types = ["Academic", "Hostel", "Admin", "Library", "Auditorium", "Laboratory", "Canteen", "Sports / Recreation"];
  container.innerHTML = '';

  for (let i = 1; i <= count; i++) {
    const row = document.createElement('div');
    row.className = 'p-2 bg-white rounded-lg border border-slate-200 grid grid-cols-12 gap-2 text-xs items-center';
    row.innerHTML = `
      <div class="col-span-2 font-bold text-slate-800">BLD-${String(i).padStart(2, '0')}</div>
      <div class="col-span-6"><input type="text" id="wiz_bld_name_${i}" value="Campus Block ${i}" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-xs font-semibold outline-none"></div>
      <div class="col-span-4">
        <select id="wiz_bld_type_${i}" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-xs outline-none">
          ${types.map(t => `<option value="${t}" ${i % types.length === types.indexOf(t) ? 'selected' : ''}>${t}</option>`).join('')}
        </select>
      </div>
    `;
    container.appendChild(row);
  }
}

async function handleCreateCampusSubmit(e) {
  e.preventDefault();

  const count = parseInt(document.getElementById('wizNumBuildings').value) || 1;
  const buildings = [];
  for (let i = 1; i <= count; i++) {
    buildings.push({
      building_code: `BLD-${String(i).padStart(2, '0')}`,
      name: document.getElementById(`wiz_bld_name_${i}`)?.value || `Campus Block ${i}`,
      building_type: document.getElementById(`wiz_bld_type_${i}`)?.value || "Academic",
      floors: 3,
      built_up_area: 0.0
    });
  }

  const payload = {
    organization_id: 1,
    name: document.getElementById('wizCampusName').value.trim(),
    campus_type: document.getElementById('wizCampusType').value,
    city: document.getElementById('wizCity').value.trim(),
    assessment_year: parseInt(document.getElementById('wizReportingYear').value) || 2025,
    operating_days_per_year: parseInt(document.getElementById('wizOperatingDays').value) || 280,
    area: parseFloat(document.getElementById('wizCampusArea').value) || 10,
    area_unit: document.getElementById('wizCampusAreaUnit').value,
    built_up_percentage: parseFloat(document.getElementById('wizBuiltUpPct').value) || 50,
    students_on_campus: parseInt(document.getElementById('wizPopStudentsOn').value) || 0,
    students_off_campus: parseInt(document.getElementById('wizPopStudentsOff').value) || 0,
    faculty_count: parseInt(document.getElementById('wizPopFaculty').value) || 0,
    non_teaching_count: parseInt(document.getElementById('wizPopNonTeaching').value) || 0,
    num_buildings: count,
    buildings: buildings,
    negative_activities: {
      solar_plant: document.getElementById('chkSolarPlant').checked,
      water_conservation: document.getElementById('chkWaterCons').checked,
      water_bodies: document.getElementById('chkWaterBodies').checked,
      animals: document.getElementById('chkAnimals').checked,
      gardening: document.getElementById('chkGardening').checked
    }
  };

  try {
    const res = await fetch('/api/campuses/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const newCampus = await res.json();

    // Create baseline assessment
    const asmRes = await fetch('/api/assessments/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        campus_id: newCampus.id,
        name: `Annual Carbon Assessment ${newCampus.assessment_year}`,
        reporting_year: newCampus.assessment_year
      })
    });
    const newAsm = await asmRes.json();

    closeNewCampusModal();
    currentCampusId = newCampus.id;
    currentAssessmentId = newAsm.id;

    await loadCampuses();
    document.getElementById('campusSelect').value = newCampus.id;
    await refreshAssessmentDashboard();

    showToast(`Campus '${newCampus.name}' created successfully with ${newCampus.buildings.length} buildings!`, 'success');
    switchTab('campus-data-entry');

  } catch (err) {
    console.error('Error creating campus:', err);
    showToast('Failed to create campus.', 'error');
  }
}

// --- Activity Submission Handlers (Campus-Level) ---
async function submitElectricityRecord(e) {
  e.preventDefault();
  const payload = {
    data_scope: "Whole Campus",
    energy_type: document.getElementById('elecSourceType').value,
    quantity: parseFloat(document.getElementById('elecQuantity').value),
    unit: document.getElementById('elecUnit').value,
    data_period: document.getElementById('elecPeriod').value,
    data_quality: document.getElementById('elecQuality').value,
    year: 2025
  };

  await fetch(`/api/activities/energy?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusElectricity').reset();
  showToast('Campus electricity record logged!', 'success');
  await triggerRecalculation();
}

async function submitFuelRecord(e) {
  e.preventDefault();
  const payload = {
    data_scope: "Whole Campus",
    energy_type: document.getElementById('fuelType').value,
    quantity: parseFloat(document.getElementById('fuelQuantity').value),
    unit: document.getElementById('fuelUnit').value,
    purpose: document.getElementById('fuelPurpose').value,
    data_quality: document.getElementById('fuelQuality').value,
    year: 2025
  };

  await fetch(`/api/activities/energy?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusFuel').reset();
  showToast('Campus fuel record logged!', 'success');
  await triggerRecalculation();
}

async function submitCampusWasteRecord(e) {
  e.preventDefault();
  const payload = {
    data_scope: "Whole Campus",
    waste_type: document.getElementById('cWasteType').value,
    quantity: parseFloat(document.getElementById('cWasteQty').value),
    unit: 'kg',
    disposal_method: document.getElementById('cWasteDisposal').value,
    data_period: document.getElementById('cWastePeriod').value,
    data_quality: document.getElementById('cWasteQuality').value,
    year: 2025
  };

  await fetch(`/api/activities/waste?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusWaste').reset();
  showToast('Solid waste record logged!', 'success');
  await triggerRecalculation();
}

async function submitCampusWaterRecord(e) {
  e.preventDefault();
  const payload = {
    data_scope: "Whole Campus",
    source: document.getElementById('cWaterSource').value,
    quantity: parseFloat(document.getElementById('cWaterQty').value),
    unit: 'kL',
    data_period: document.getElementById('cWaterPeriod').value,
    year: 2025
  };

  await fetch(`/api/activities/water?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusWater').reset();
  showToast('Water consumption record logged!', 'success');
  await triggerRecalculation();
}

async function submitCampusSTPRecord(e) {
  e.preventDefault();
  const payload = {
    facility_name: "Central Sewage Treatment Plant",
    treatment_type: document.getElementById('cStpMethod').value,
    treated_quantity: parseFloat(document.getElementById('cStpQty').value) || 0,
    wastewater_quantity: parseFloat(document.getElementById('cStpQty').value) || 0,
    reused_quantity: parseFloat(document.getElementById('cStpReused').value) || 0,
    electricity_kwh: parseFloat(document.getElementById('cStpElectricity').value) || 0,
    year: 2025
  };

  await fetch(`/api/activities/wastewater?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusSTP').reset();
  showToast('STP wastewater record logged!', 'success');
  await triggerRecalculation();
}

async function submitCampusFleetRecord(e) {
  e.preventDefault();
  const payload = {
    data_scope: "Whole Campus",
    record_type: "Fleet",
    mode: document.getElementById('cFleetCategory').value,
    vehicle_count: parseInt(document.getElementById('cFleetNumVehicles').value) || 1,
    fuel_type: document.getElementById('cFleetFuelType').value,
    fuel_quantity: parseFloat(document.getElementById('cFleetFuelQty').value) || 0,
    distance_km: parseFloat(document.getElementById('cFleetDistance').value) || 0,
    is_ev_in_grid_electricity: document.getElementById('cEvGridSafeguard').value === 'true',
    year: 2025
  };

  await fetch(`/api/activities/transport?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusFleet').reset();
  showToast('Fleet transport record logged!', 'success');
  await triggerRecalculation();
}

async function submitCampusCanteenRecord(e) {
  e.preventDefault();
  const bId = document.getElementById('cCanteenBuilding').value;
  const payload = {
    building_id: bId ? parseInt(bId) : null,
    canteen_name: document.getElementById('cCanteenName').value,
    operating_days: parseInt(document.getElementById('cCanteenDays').value) || 280,
    meals_served: (parseInt(document.getElementById('cCanteenMeals').value) || 0) * (parseInt(document.getElementById('cCanteenDays').value) || 280),
    lpg_kg: parseFloat(document.getElementById('cCanteenLpg').value) || 0,
    food_waste_kg: parseFloat(document.getElementById('cCanteenFoodWaste').value) || 0,
    year: 2025
  };

  await fetch(`/api/activities/food?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusCanteen').reset();
  showToast('Canteen / kitchen record logged!', 'success');
  await triggerRecalculation();
}

async function submitCampusIndustrialRecord(e) {
  e.preventDefault();
  const payload = {
    production_name: document.getElementById('cIndName').value,
    production_quantity: parseFloat(document.getElementById('cIndQty').value) || 0,
    process_emissions_tco2e: parseFloat(document.getElementById('cIndEmissions').value) || 0,
    refrigerant_type: document.getElementById('cIndRefType').value,
    refrigerant_leakage_kg: parseFloat(document.getElementById('cIndRefLeak').value) || 0,
    year: 2025
  };

  await fetch(`/api/activities/industrial?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusIndustry').reset();
  showToast('Industrial & refrigerant record logged!', 'success');
  await triggerRecalculation();
}

async function submitCampusSolarRecord(e) {
  e.preventDefault();
  const payload = {
    technology: document.getElementById('cSolarType').value,
    capacity_kw: parseFloat(document.getElementById('cSolarCapacity').value),
    generation_kwh: parseFloat(document.getElementById('cSolarGen').value),
    installation_location: document.getElementById('cSolarLoc').value,
    data_quality: document.getElementById('cSolarQuality').value,
    is_onsite_consumed: true,
    year: 2025
  };

  await fetch(`/api/activities/renewables?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusSolar').reset();
  showToast('Solar generation logged to negative footprint ledger!', 'success');
  await triggerRecalculation();
}

async function submitCampusWaterConsRecord(e) {
  e.preventDefault();
  const payload = {
    water_saved_kl: parseFloat(document.getElementById('cWcQty').value),
    method: document.getElementById('cWcMethod').value,
    data_quality: document.getElementById('cWcQuality').value,
    year: 2025
  };

  await fetch(`/api/activities/water-conservation?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusWaterCons').reset();
  showToast('Water conservation avoided emissions logged!', 'success');
  await triggerRecalculation();
}

async function submitCampusWaterBodyRecord(e) {
  e.preventDefault();
  const payload = {
    body_count: parseInt(document.getElementById('cWbCount').value) || 1,
    total_area_sqm: parseFloat(document.getElementById('cWbArea').value) || 0,
    body_type: document.getElementById('cWbType').value,
    year: 2025
  };

  await fetch(`/api/activities/water-bodies?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusWaterBodies').reset();
  showToast('Water body ecological carbon benefit recorded!', 'success');
  await triggerRecalculation();
}

async function submitCampusAnimalRecord(e) {
  e.preventDefault();
  const payload = {
    animal_type: document.getElementById('cAnType').value,
    animal_count: parseInt(document.getElementById('cAnCount').value) || 0,
    management_method: document.getElementById('cAnMethod').value,
    year: 2025
  };

  await fetch(`/api/activities/animals?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusAnimals').reset();
  showToast('Animal census record saved!', 'success');
  await triggerRecalculation();
}

async function submitCampusGreeneryRecord(e) {
  e.preventDefault();
  const payload = {
    green_area_sqm: parseFloat(document.getElementById('cGreenArea').value),
    tree_count: parseInt(document.getElementById('cGreenTrees').value),
    tree_species: document.getElementById('cGreenSpecies').value,
    year: 2025
  };

  await fetch(`/api/activities/green?assessment_id=${currentAssessmentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('formCampusGreenery').reset();
  showToast('Tree canopy & carbon sequestration recorded!', 'success');
  await triggerRecalculation();
}

// --- Activity Records List Rendering with Delete Actions ---
async function loadAllActivityLists() {
  if (!currentAssessmentId) return;

  // Electricity & Fuel
  const eRes = await fetch(`/api/activities/energy?assessment_id=${currentAssessmentId}`);
  const energy = await eRes.json();
  
  const eList = energy.filter(r => r.energy_type.includes('Electricity') || r.energy_type.includes('Grid'));
  const fList = energy.filter(r => !r.energy_type.includes('Electricity') && !r.energy_type.includes('Grid'));

  const eContainer = document.getElementById('electricityRecordsList');
  if (eContainer) {
    eContainer.innerHTML = eList.length === 0 ? '<p class="text-xs text-slate-400 p-2">No electricity records logged.</p>' : `
      <table class="w-full text-left text-xs text-slate-600 border border-slate-200 rounded-lg overflow-hidden">
        <thead class="bg-slate-100 font-bold uppercase"><tr><th class="p-2">Source</th><th class="p-2 text-right">Quantity</th><th class="p-2">Quality</th><th class="p-2 text-right">Action</th></tr></thead>
        <tbody class="divide-y divide-slate-100 bg-white">
          ${eList.map(r => `<tr>
            <td class="p-2 font-semibold text-slate-800">${r.energy_type}</td>
            <td class="p-2 text-right font-bold text-emerald-700">${r.quantity.toLocaleString()} ${r.unit}</td>
            <td class="p-2"><span class="bg-slate-100 px-1.5 py-0.5 rounded text-[10px]">${r.data_quality}</span></td>
            <td class="p-2 text-right"><button onclick="deleteActivityRecord('energy', ${r.id})" class="text-rose-500 hover:text-rose-700 p-1"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button></td>
          </tr>`).join('')}
        </tbody>
      </table>
    `;
  }

  const fContainer = document.getElementById('fuelRecordsList');
  if (fContainer) {
    fContainer.innerHTML = fList.length === 0 ? '<p class="text-xs text-slate-400 p-2">No fuel records logged.</p>' : `
      <table class="w-full text-left text-xs text-slate-600 border border-slate-200 rounded-lg overflow-hidden">
        <thead class="bg-slate-100 font-bold uppercase"><tr><th class="p-2">Fuel Type</th><th class="p-2">Purpose</th><th class="p-2 text-right">Quantity</th><th class="p-2 text-right">Action</th></tr></thead>
        <tbody class="divide-y divide-slate-100 bg-white">
          ${fList.map(r => `<tr>
            <td class="p-2 font-semibold text-slate-800">${r.energy_type}</td>
            <td class="p-2">${r.purpose || 'Operations'}</td>
            <td class="p-2 text-right font-bold">${r.quantity.toLocaleString()} ${r.unit}</td>
            <td class="p-2 text-right"><button onclick="deleteActivityRecord('energy', ${r.id})" class="text-rose-500 hover:text-rose-700 p-1"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button></td>
          </tr>`).join('')}
        </tbody>
      </table>
    `;
  }

  // Waste
  const wRes = await fetch(`/api/activities/waste?assessment_id=${currentAssessmentId}`);
  const waste = await wRes.json();
  const wContainer = document.getElementById('cWasteRecordsList');
  if (wContainer) {
    wContainer.innerHTML = waste.length === 0 ? '<p class="text-xs text-slate-400 p-2">No waste records logged.</p>' : `
      <table class="w-full text-left text-xs text-slate-600 border border-slate-200 rounded-lg overflow-hidden">
        <thead class="bg-slate-100 font-bold uppercase"><tr><th class="p-2">Stream</th><th class="p-2">Method</th><th class="p-2 text-right">Quantity</th><th class="p-2 text-right">Action</th></tr></thead>
        <tbody class="divide-y divide-slate-100 bg-white">
          ${waste.map(r => `<tr>
            <td class="p-2 font-semibold text-slate-800">${r.waste_type}</td>
            <td class="p-2"><span class="${r.disposal_method === 'Composting' || r.disposal_method === 'Recycling' ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'} px-1.5 py-0.5 rounded text-[10px] font-bold">${r.disposal_method}</span></td>
            <td class="p-2 text-right font-bold">${r.quantity.toLocaleString()} kg</td>
            <td class="p-2 text-right"><button onclick="deleteActivityRecord('waste', ${r.id})" class="text-rose-500 hover:text-rose-700 p-1"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button></td>
          </tr>`).join('')}
        </tbody>
      </table>
    `;
  }

  // Solar
  const sRes = await fetch(`/api/activities/renewables?assessment_id=${currentAssessmentId}`);
  const solar = await sRes.json();
  const sContainer = document.getElementById('cSolarRecordsList');
  if (sContainer) {
    sContainer.innerHTML = solar.length === 0 ? '<p class="text-xs text-slate-400 p-2">No solar records logged.</p>' : `
      <table class="w-full text-left text-xs text-slate-600 border border-slate-200 rounded-lg overflow-hidden">
        <thead class="bg-slate-100 font-bold uppercase"><tr><th class="p-2">Technology</th><th class="p-2">Capacity</th><th class="p-2 text-right">Annual Generation</th><th class="p-2 text-right">Action</th></tr></thead>
        <tbody class="divide-y divide-slate-100 bg-white">
          ${solar.map(r => `<tr>
            <td class="p-2 font-semibold text-slate-800">${r.technology}</td>
            <td class="p-2">${r.capacity_kw} kWp</td>
            <td class="p-2 text-right font-bold text-emerald-700">${r.generation_kwh.toLocaleString()} kWh</td>
            <td class="p-2 text-right"><button onclick="deleteActivityRecord('renewables', ${r.id})" class="text-rose-500 hover:text-rose-700 p-1"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button></td>
          </tr>`).join('')}
        </tbody>
      </table>
    `;
  }

  // Greenery
  const gRes = await fetch(`/api/activities/green?assessment_id=${currentAssessmentId}`);
  const green = await gRes.json();
  const gContainer = document.getElementById('cGreenRecordsList');
  if (gContainer) {
    gContainer.innerHTML = green.length === 0 ? '<p class="text-xs text-slate-400 p-2">No greenery records logged.</p>' : `
      <table class="w-full text-left text-xs text-slate-600 border border-slate-200 rounded-lg overflow-hidden">
        <thead class="bg-slate-100 font-bold uppercase"><tr><th class="p-2">Green Area</th><th class="p-2 text-right">Tree Census</th><th class="p-2">Species</th><th class="p-2 text-right">Action</th></tr></thead>
        <tbody class="divide-y divide-slate-100 bg-white">
          ${green.map(r => `<tr>
            <td class="p-2 font-semibold text-slate-800">${r.green_area_sqm.toLocaleString()} m²</td>
            <td class="p-2 text-right font-bold text-emerald-700">${r.tree_count.toLocaleString()} Trees</td>
            <td class="p-2 text-slate-500">${r.tree_species || 'Native canopy'}</td>
            <td class="p-2 text-right"><button onclick="deleteActivityRecord('green', ${r.id})" class="text-rose-500 hover:text-rose-700 p-1"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button></td>
          </tr>`).join('')}
        </tbody>
      </table>
    `;
  }

  lucide.createIcons();
}

async function deleteActivityRecord(type, id) {
  if (!confirm('Delete this record?')) return;
  try {
    await fetch(`/api/activities/${type}/${id}`, { method: 'DELETE' });
    showToast('Record deleted.', 'info');
    await triggerRecalculation();
  } catch (err) {
    console.error('Error deleting record:', err);
    showToast('Failed to delete record.', 'error');
  }
}

// --- Carbon Accounting Logs & Reductions Ledger ---
async function loadCarbonAccountingLogs() {
  if (!currentAssessmentId) return;

  const cRes = await fetch(`/api/carbon/calculations?assessment_id=${currentAssessmentId}`);
  const calcs = await cRes.json();
  const cBody = document.getElementById('calculationsTableBody');
  cBody.innerHTML = calcs.map(c => `
    <tr>
      <td class="p-2.5 font-bold ${c.scope === 'Scope 1' ? 'text-amber-600' : c.scope === 'Scope 2' ? 'text-indigo-600' : 'text-purple-600'}">${c.scope}</td>
      <td class="p-2.5 font-semibold text-slate-800">${c.category}</td>
      <td class="p-2.5">${c.activity}</td>
      <td class="p-2.5">${c.quantity.toLocaleString()} ${c.unit}</td>
      <td class="p-2.5 font-mono">${c.emission_factor} ${c.emission_factor_unit}</td>
      <td class="p-2.5 text-slate-500">${c.emission_factor_source || '-'}</td>
      <td class="p-2.5 text-right font-bold text-slate-900">${c.emissions_co2e.toFixed(4)}</td>
    </tr>
  `).join('');

  const rRes = await fetch(`/api/carbon/reductions?assessment_id=${currentAssessmentId}`);
  const reds = await rRes.json();
  const rBody = document.getElementById('reductionsTableBody');
  rBody.innerHTML = reds.map(r => `
    <tr>
      <td class="p-2.5 font-bold text-emerald-800">${r.category}</td>
      <td class="p-2.5 font-semibold text-slate-800">${r.activity}</td>
      <td class="p-2.5 text-slate-500">${r.methodology}</td>
      <td class="p-2.5"><span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold text-[10px]">${r.eligibility_status}</span></td>
      <td class="p-2.5 text-right font-bold text-emerald-700">-${r.reduction_co2e.toFixed(4)} tCO2e</td>
    </tr>
  `).join('');
}

// --- Building Analytics Table ---
async function loadBuildingAnalytics() {
  if (!currentAssessmentId) return;
  const res = await fetch(`/api/carbon/building-wise?assessment_id=${currentAssessmentId}`);
  const data = await res.json();
  const tbody = document.getElementById('bldAnalyticsTableBody');
  tbody.innerHTML = data.map(b => `
    <tr class="hover:bg-slate-50">
      <td class="p-3 font-bold text-slate-900">${b.building_code}</td>
      <td class="p-3 font-semibold text-slate-800">${b.name}</td>
      <td class="p-3"><span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[10px] font-semibold">${b.building_type}</span></td>
      <td class="p-3">${b.built_up_area_sqm.toLocaleString()} m²</td>
      <td class="p-3">${b.occupancy.toLocaleString()}</td>
      <td class="p-3 text-right font-bold text-rose-700">${b.gross_tco2e.toFixed(2)}</td>
      <td class="p-3 text-right font-bold text-emerald-600">-${b.reductions_tco2e.toFixed(2)}</td>
      <td class="p-3 text-right font-extrabold text-blue-700">${b.net_tco2e.toFixed(2)}</td>
      <td class="p-3 text-right">${b.co2e_per_person.toFixed(3)}</td>
      <td class="p-3 text-right font-mono">${(b.co2e_per_sqm * 1000).toFixed(1)}</td>
    </tr>
  `).join('');
}

// --- Dashboard & Analytical Charts ---
function renderDashboardCharts(summary) {
  const ctxWaterfall = document.getElementById('waterfallChart')?.getContext('2d');
  if (ctxWaterfall) {
    if (waterfallChartInstance) waterfallChartInstance.destroy();
    waterfallChartInstance = new Chart(ctxWaterfall, {
      type: 'bar',
      data: {
        labels: ['Positive / Gross', 'Negative / Avoided', 'Net Footprint'],
        datasets: [{
          data: [summary.gross_emissions, -summary.eligible_reductions, summary.net_footprint],
          backgroundColor: ['#f43f5e', '#10b981', '#3b82f6'],
          borderRadius: 8,
          barThickness: 45
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { title: { display: true, text: 'tCO2e' }, grid: { color: '#f1f5f9' } } }
      }
    });
  }

  const ctxScope = document.getElementById('scopeDonutChart')?.getContext('2d');
  if (ctxScope) {
    if (scopeDonutChartInstance) scopeDonutChartInstance.destroy();
    scopeDonutChartInstance = new Chart(ctxScope, {
      type: 'doughnut',
      data: {
        labels: ['Scope 1 (Direct)', 'Scope 2 (Electricity)', 'Scope 3 (Indirect)'],
        datasets: [{
          data: [summary.scope1, summary.scope2, summary.scope3],
          backgroundColor: ['#f59e0b', '#6366f1', '#a855f7'],
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } },
        cutout: '65%'
      }
    });
  }
}

async function renderDetailedCharts() {
  if (!currentAssessmentId) return;

  const ctxScopeTab = document.getElementById('scopeDonutChartTab')?.getContext('2d');
  if (ctxScopeTab && currentAssessmentData && currentAssessmentData.summary) {
    if (scopeDonutChartTabInstance) scopeDonutChartTabInstance.destroy();
    const s = currentAssessmentData.summary;
    scopeDonutChartTabInstance = new Chart(ctxScopeTab, {
      type: 'pie',
      data: {
        labels: ['Scope 1 (Direct)', 'Scope 2 (Electricity)', 'Scope 3 (Indirect)'],
        datasets: [{
          data: [s.scope1, s.scope2, s.scope3],
          backgroundColor: ['#f59e0b', '#6366f1', '#a855f7']
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  const bRes = await fetch(`/api/carbon/building-wise?assessment_id=${currentAssessmentId}`);
  const bData = await bRes.json();

  const ctxBld = document.getElementById('buildingBarChart')?.getContext('2d');
  if (ctxBld) {
    if (buildingBarChartInstance) buildingBarChartInstance.destroy();
    buildingBarChartInstance = new Chart(ctxBld, {
      type: 'bar',
      data: {
        labels: bData.slice(0, 10).map(b => b.building_code || b.name.substring(0, 10)),
        datasets: [
          { label: 'Gross (tCO2e)', data: bData.slice(0, 10).map(b => b.gross_tco2e), backgroundColor: '#f43f5e', borderRadius: 6 },
          { label: 'Net (tCO2e)', data: bData.slice(0, 10).map(b => b.net_tco2e), backgroundColor: '#3b82f6', borderRadius: 6 }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } } }
    });
  }
}

// --- Live What-If Decarbonization Simulator ---
async function runLiveSimulation() {
  if (!currentAssessmentId) return;

  const eff = parseFloat(document.getElementById('slider_energy_eff')?.value) || 0;
  const solar = parseFloat(document.getElementById('slider_solar_add')?.value) || 0;
  const ev = parseFloat(document.getElementById('slider_ev_trans')?.value) || 0;
  const waste = parseFloat(document.getElementById('slider_waste_div')?.value) || 0;
  const water = parseFloat(document.getElementById('slider_water_div')?.value) || 0;
  const trees = parseInt(document.getElementById('slider_trees_add')?.value) || 0;

  document.getElementById('val_energy_eff').textContent = `${eff}%`;
  document.getElementById('val_solar_add').textContent = `+${solar} kW`;
  document.getElementById('val_ev_trans').textContent = `${ev}%`;
  document.getElementById('val_waste_div').textContent = `${waste}%`;
  document.getElementById('val_water_div').textContent = `${water}%`;
  document.getElementById('val_trees_add').textContent = `+${trees} Trees`;

  const payload = {
    assessment_id: currentAssessmentId,
    energy_efficiency_pct: eff,
    solar_capacity_addition_kw: solar,
    ev_fleet_transition_pct: ev,
    fuel_reduction_pct: 10,
    waste_composting_recycling_pct: waste,
    water_conservation_pct: water,
    additional_trees_count: trees
  };

  try {
    const res = await fetch('/api/scenarios/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const sim = await res.json();

    document.getElementById('simPotentialSavings').textContent = sim.potential_savings_tco2e.toFixed(2);
    document.getElementById('simPotentialPct').textContent = `${sim.potential_reduction_pct.toFixed(1)}% Reduction from Baseline`;
    document.getElementById('simBaseGross').textContent = `${sim.baseline_gross_tco2e.toFixed(2)} tCO2e`;
    document.getElementById('simScenGross').textContent = `${sim.scenario_gross_tco2e.toFixed(2)} tCO2e`;
    document.getElementById('simScenRed').textContent = `-${sim.scenario_reduction_tco2e.toFixed(2)} tCO2e`;
    document.getElementById('simScenNet').textContent = `${sim.scenario_net_tco2e.toFixed(2)} tCO2e`;
  } catch (err) {
    console.error('Simulation error:', err);
  }
}

async function saveCurrentScenario() {
  const payload = {
    assessment_id: currentAssessmentId,
    name: "Target Net-Zero Pathway 2030",
    description: "Combined intervention with solar expansion, EV transit, and high-density Miyawaki forestry",
    energy_efficiency_pct: parseFloat(document.getElementById('slider_energy_eff').value),
    solar_capacity_addition_kw: parseFloat(document.getElementById('slider_solar_add').value),
    ev_fleet_transition_pct: parseFloat(document.getElementById('slider_ev_trans').value),
    waste_composting_recycling_pct: parseFloat(document.getElementById('slider_waste_div').value),
    water_conservation_pct: parseFloat(document.getElementById('slider_water_div').value),
    additional_trees_count: parseInt(document.getElementById('slider_trees_add').value)
  };

  await fetch('/api/scenarios/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  showToast('Scenario saved successfully to simulation records.', 'success');
}

// --- Recommendations ---
async function loadRecommendations() {
  if (!currentAssessmentId) return;
  const res = await fetch(`/api/recommendations/?assessment_id=${currentAssessmentId}`);
  const recs = await res.json();
  const container = document.getElementById('recommendationsList');
  container.innerHTML = recs.map(r => `
    <div class="glass-card rounded-xl p-5 border-l-4 ${r.priority === 'High' ? 'border-l-rose-500' : 'border-l-emerald-500'} flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[10px] font-bold uppercase">${r.category}</span>
          <span class="text-xs font-bold ${r.priority === 'High' ? 'text-rose-600' : 'text-emerald-700'}">${r.priority} Priority</span>
        </div>
        <h4 class="font-bold text-slate-900 text-sm">${r.title}</h4>
        <p class="text-xs text-slate-600 mt-2">${r.recommendation_text}</p>
      </div>
      <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        <span class="text-slate-400">${r.intervention_type}</span>
        <span class="font-bold text-emerald-700">~${r.estimated_reduction_pct}% Impact</span>
      </div>
    </div>
  `).join('');
}

// --- Benchmarks & Emission Factors ---
async function loadBenchmarks() {
  const res = await fetch('/api/benchmarks/campuses');
  const list = await res.json();
  const tbody = document.getElementById('benchmarkTableBody');
  tbody.innerHTML = list.map(c => `
    <tr>
      <td class="p-3 font-bold text-slate-900">${c.name}</td>
      <td class="p-3"><span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[10px]">${c.campus_type}</span></td>
      <td class="p-3">${c.population.toLocaleString()}</td>
      <td class="p-3">${c.area_acres} acres</td>
      <td class="p-3 text-right font-bold text-rose-700">${c.gross_tco2e.toFixed(2)}</td>
      <td class="p-3 text-right font-bold text-blue-700">${c.net_tco2e.toFixed(2)}</td>
      <td class="p-3 text-right font-bold">${c.tco2e_per_person.toFixed(3)}</td>
      <td class="p-3 text-right text-emerald-600 font-bold">${c.renewable_pct.toFixed(1)}%</td>
    </tr>
  `).join('');
}

async function loadEmissionFactors() {
  const res = await fetch('/api/factors/');
  const list = await res.json();
  const tbody = document.getElementById('factorsTableBody');
  tbody.innerHTML = list.map(ef => `
    <tr>
      <td class="p-2.5 font-bold text-slate-800">${ef.category}</td>
      <td class="p-2.5 font-semibold text-slate-700">${ef.activity}</td>
      <td class="p-2.5">${ef.unit}</td>
      <td class="p-2.5 font-mono font-bold text-emerald-700">${ef.factor}</td>
      <td class="p-2.5"><span class="bg-slate-100 px-1.5 py-0.5 rounded text-[10px] font-bold">${ef.scope}</span></td>
      <td class="p-2.5 text-slate-500">${ef.source}</td>
      <td class="p-2.5">${ef.reference_year}</td>
    </tr>
  `).join('');
}

// --- Trigger Recalculation ---
async function triggerRecalculation() {
  if (!currentAssessmentId) return;
  const res = await fetch(`/api/assessments/${currentAssessmentId}/calculate`, { method: 'POST' });
  const data = await res.json();
  await refreshAssessmentDashboard();
  showToast('Carbon accounting metrics & rankings recalculated!', 'success');
}

// --- Report Downloads ---
function downloadReport(format) {
  if (!currentAssessmentId) return;
  window.open(`/api/reports/${format}/${currentAssessmentId}`, '_blank');
}

function downloadTemplate(type) {
  window.open(`/api/exchange/template/${type}`, '_blank');
}

async function handleCsvUpload(e) {
  e.preventDefault();
  const type = document.getElementById('importModuleType').value;
  const fileInput = document.getElementById('csvFileInput');
  if (!fileInput.files[0]) return;

  const formData = new FormData();
  formData.append('assessment_id', currentAssessmentId);
  formData.append('campus_id', currentCampusId);
  formData.append('file', fileInput.files[0]);

  const res = await fetch(`/api/exchange/import/${type}`, {
    method: 'POST',
    body: formData
  });
  const data = await res.json();
  const resDiv = document.getElementById('importResult');
  if (data.success) {
    resDiv.innerHTML = `<span class="text-emerald-700 font-bold">Successfully imported ${data.imported_count} records!</span>`;
    showToast(`Imported ${data.imported_count} records successfully!`, 'success');
    await triggerRecalculation();
  } else {
    resDiv.innerHTML = `<span class="text-rose-700 font-bold">Errors in CSV: ${data.errors.join(', ')}</span>`;
    showToast('Errors occurred during CSV import.', 'error');
  }
}
