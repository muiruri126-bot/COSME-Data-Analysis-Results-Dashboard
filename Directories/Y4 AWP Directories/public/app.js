// ─── Y4 AWP Directory Dashboard – Frontend App ─────────────
const API = '';

// ─── State ───────────────────────────────────────────────────
let allRecords = [];
let currentFilters = {};

// ─── DOM Elements ────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const tableBody = $('#tableBody');
const modalOverlay = $('#modalOverlay');
const historyOverlay = $('#historyOverlay');
const recordForm = $('#recordForm');

// ─── Initialize ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    loadRecords();
    loadFilterOptions();
    setupEventListeners();
});

// ─── Event Listeners ─────────────────────────────────────────
function setupEventListeners() {
    // Add new record
    $('#btnAddNew').addEventListener('click', () => openModal());

    // Sync from SharePoint
    $('#btnSync').addEventListener('click', syncFromSharePoint);

    // Search
    let searchTimer;
    $('#searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            currentFilters.search = e.target.value;
            loadRecords();
        }, 300);
    });

    // Filters
    $('#filterDepartment').addEventListener('change', (e) => {
        currentFilters.department = e.target.value;
        loadRecords();
    });
    $('#filterStatus').addEventListener('change', (e) => {
        currentFilters.status = e.target.value;
        loadRecords();
    });
    $('#filterStation').addEventListener('change', (e) => {
        currentFilters.duty_station = e.target.value;
        loadRecords();
    });

    // Export CSV
    $('#btnExport').addEventListener('click', exportToCSV);

    // Modal controls
    $('#modalClose').addEventListener('click', closeModal);
    $('#btnCancel').addEventListener('click', closeModal);
    $('#historyClose').addEventListener('click', () => historyOverlay.classList.remove('active'));
    modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) closeModal(); });
    historyOverlay.addEventListener('click', (e) => { if (e.target === historyOverlay) historyOverlay.classList.remove('active'); });

    // Form submit
    recordForm.addEventListener('submit', handleFormSubmit);

    // Auto-calculate balance
    const budgetFields = ['annual_budget', 'spent_to_date'];
    budgetFields.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', calculateBalance);
    });
}

// ─── API Functions ───────────────────────────────────────────
async function apiGet(endpoint) {
    const res = await fetch(`${API}${endpoint}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
}

async function apiPost(endpoint, data) {
    const res = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || res.statusText);
    }
    return res.json();
}

async function apiPut(endpoint, data) {
    const res = await fetch(`${API}${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || res.statusText);
    }
    return res.json();
}

async function apiDelete(endpoint) {
    const res = await fetch(`${API}${endpoint}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
}

// ─── Dashboard Stats ────────────────────────────────────────
async function loadDashboard() {
    try {
        const stats = await apiGet('/api/stats');
        $('#statTotal').textContent = stats.totalRecords;
        $('#statActive').textContent = stats.activeRecords;
        $('#statBudget').textContent = formatCurrency(stats.totalBudget);
        $('#statSpent').textContent = formatCurrency(stats.totalSpent);
        $('#statDepts').textContent = stats.departments;
        $('#statLastSync').textContent = stats.lastSync
            ? new Date(stats.lastSync.sync_time).toLocaleString()
            : 'Never';
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// ─── Load Records ────────────────────────────────────────────
async function loadRecords() {
    try {
        const params = new URLSearchParams();
        Object.entries(currentFilters).forEach(([k, v]) => {
            if (v) params.set(k, v);
        });
        const url = `/api/records${params.toString() ? '?' + params : ''}`;
        allRecords = await apiGet(url);
        renderTable(allRecords);
    } catch (error) {
        console.error('Failed to load records:', error);
        tableBody.innerHTML = `<tr><td colspan="12" class="loading-row" style="color:var(--danger)">
            <i class="fas fa-exclamation-triangle"></i> Failed to load records</td></tr>`;
    }
}

// ─── Render Table ────────────────────────────────────────────
function renderTable(records) {
    if (records.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="12" class="loading-row">
            <i class="fas fa-inbox"></i> No records found. Click "New Record" to add one, or "Sync Now" to pull from SharePoint.</td></tr>`;
        return;
    }

    tableBody.innerHTML = records.map((r, i) => `
        <tr>
            <td>${i + 1}</td>
            <td><strong>${escapeHtml(r.staff_name)}</strong></td>
            <td>${escapeHtml(r.designation)}</td>
            <td>${escapeHtml(r.department)}</td>
            <td>${escapeHtml(r.duty_station)}</td>
            <td>${escapeHtml(r.project_code)}</td>
            <td title="${escapeHtml(r.activity_description)}">${truncate(r.activity_description, 30)}</td>
            <td>${formatCurrency(r.annual_budget)}</td>
            <td>${formatCurrency(r.spent_to_date)}</td>
            <td>${formatCurrency(r.balance)}</td>
            <td>${statusBadge(r.status)}</td>
            <td>
                <div class="action-group">
                    <button class="btn btn-sm btn-outline btn-icon" onclick="editRecord(${r.id})" title="Edit">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button class="btn btn-sm btn-outline btn-icon" onclick="viewHistory(${r.id})" title="History">
                        <i class="fas fa-history"></i>
                    </button>
                    <button class="btn btn-sm btn-danger btn-icon" onclick="deleteRecord(${r.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// ─── Filter Options ──────────────────────────────────────────
async function loadFilterOptions() {
    try {
        const [departments, stations] = await Promise.all([
            apiGet('/api/filters/department'),
            apiGet('/api/filters/duty_station'),
        ]);
        populateSelect('#filterDepartment', departments, 'All Departments');
        populateSelect('#filterStation', stations, 'All Duty Stations');
    } catch (error) {
        console.error('Failed to load filters:', error);
    }
}

function populateSelect(selector, values, defaultText) {
    const sel = $(selector);
    sel.innerHTML = `<option value="">${defaultText}</option>`;
    values.forEach(v => {
        sel.innerHTML += `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`;
    });
}

// ─── Modal Operations ────────────────────────────────────────
function openModal(record = null) {
    recordForm.reset();
    $('#recordId').value = '';

    if (record) {
        $('#modalTitle').innerHTML = '<i class="fas fa-edit"></i> Edit Record';
        $('#recordId').value = record.id;
        // Populate form fields
        const fields = [
            'staff_name', 'designation', 'department', 'duty_station', 'phone', 'email',
            'project_code', 'activity_code', 'activity_description', 'budget_line',
            'annual_budget', 'q1_budget', 'q2_budget', 'q3_budget', 'q4_budget',
            'spent_to_date', 'balance', 'status', 'partner_organization',
            'implementation_area', 'target_beneficiaries', 'achieved_beneficiaries', 'remarks'
        ];
        fields.forEach(f => {
            const el = document.getElementById(f);
            if (el && record[f] !== undefined) el.value = record[f];
        });
    } else {
        $('#modalTitle').innerHTML = '<i class="fas fa-plus-circle"></i> Add New Record';
    }

    modalOverlay.classList.add('active');
    document.getElementById('staff_name').focus();
}

function closeModal() {
    modalOverlay.classList.remove('active');
}

async function editRecord(id) {
    try {
        const record = await apiGet(`/api/records/${id}`);
        openModal(record);
    } catch (error) {
        showToast('Failed to load record', 'error');
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(recordForm);
    const data = Object.fromEntries(formData.entries());
    const id = $('#recordId').value;

    // Convert numeric fields
    ['annual_budget', 'q1_budget', 'q2_budget', 'q3_budget', 'q4_budget',
     'spent_to_date', 'balance', 'target_beneficiaries', 'achieved_beneficiaries'
    ].forEach(f => {
        if (data[f]) data[f] = parseFloat(data[f]);
    });

    try {
        if (id) {
            await apiPut(`/api/records/${id}`, data);
            showToast('Record updated successfully', 'success');
        } else {
            await apiPost('/api/records', data);
            showToast('Record created successfully', 'success');
        }
        closeModal();
        loadRecords();
        loadDashboard();
        loadFilterOptions();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ─── Delete ──────────────────────────────────────────────────
async function deleteRecord(id) {
    if (!confirm('Are you sure you want to delete this record?')) return;
    try {
        await apiDelete(`/api/records/${id}`);
        showToast('Record deleted', 'success');
        loadRecords();
        loadDashboard();
    } catch (error) {
        showToast('Failed to delete record', 'error');
    }
}

// ─── History ─────────────────────────────────────────────────
async function viewHistory(id) {
    try {
        const history = await apiGet(`/api/records/${id}/history`);
        const body = $('#historyBody');

        if (history.length === 0) {
            body.innerHTML = '<p style="color:var(--text-light); text-align:center; padding:20px;">No update history yet</p>';
        } else {
            body.innerHTML = `<ul class="history-list">${history.map(h => `
                <li class="history-item">
                    <span class="history-field">${escapeHtml(h.field_changed)}</span>:
                    <span class="history-old">${escapeHtml(h.old_value)}</span> →
                    <span class="history-new">${escapeHtml(h.new_value)}</span>
                    <span class="history-time">${new Date(h.changed_at).toLocaleString()} by ${escapeHtml(h.changed_by)}</span>
                </li>
            `).join('')}</ul>`;
        }

        historyOverlay.classList.add('active');
    } catch (error) {
        showToast('Failed to load history', 'error');
    }
}

// ─── SharePoint Sync ─────────────────────────────────────────
async function syncFromSharePoint() {
    const btn = $('#btnSync');
    const syncStatus = $('#syncStatus');
    const syncText = $('#syncText');

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Syncing...';
    syncStatus.className = 'sync-status syncing';
    syncText.textContent = 'Syncing...';

    try {
        const result = await apiPost('/api/sync', {});
        showToast(result.message, 'success');
        syncStatus.className = 'sync-status synced';
        syncText.textContent = 'Synced';
        loadRecords();
        loadDashboard();
        loadFilterOptions();
    } catch (error) {
        syncStatus.className = 'sync-status error';
        syncText.textContent = 'Sync failed';
        showToast('SharePoint sync failed. Check Azure AD configuration in .env file.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Sync Now';
    }
}

// ─── CSV Export ──────────────────────────────────────────────
function exportToCSV() {
    if (allRecords.length === 0) {
        showToast('No records to export', 'error');
        return;
    }

    const headers = [
        'Staff Name', 'Designation', 'Department', 'Duty Station', 'Phone', 'Email',
        'Project Code', 'Activity Code', 'Activity Description', 'Budget Line',
        'Annual Budget', 'Q1 Budget', 'Q2 Budget', 'Q3 Budget', 'Q4 Budget',
        'Spent to Date', 'Balance', 'Status', 'Partner Organization',
        'Implementation Area', 'Target Beneficiaries', 'Achieved Beneficiaries', 'Remarks'
    ];

    const keys = [
        'staff_name', 'designation', 'department', 'duty_station', 'phone', 'email',
        'project_code', 'activity_code', 'activity_description', 'budget_line',
        'annual_budget', 'q1_budget', 'q2_budget', 'q3_budget', 'q4_budget',
        'spent_to_date', 'balance', 'status', 'partner_organization',
        'implementation_area', 'target_beneficiaries', 'achieved_beneficiaries', 'remarks'
    ];

    let csv = headers.join(',') + '\n';
    allRecords.forEach(r => {
        csv += keys.map(k => `"${String(r[k] || '').replace(/"/g, '""')}"`).join(',') + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Y4_AWP_Directory_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('CSV exported successfully', 'success');
}

// ─── Calculate Balance ───────────────────────────────────────
function calculateBalance() {
    const budget = parseFloat(document.getElementById('annual_budget').value) || 0;
    const spent = parseFloat(document.getElementById('spent_to_date').value) || 0;
    document.getElementById('balance').value = (budget - spent).toFixed(2);
}

// ─── Utilities ───────────────────────────────────────────────
function formatCurrency(val) {
    const num = parseFloat(val) || 0;
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toLocaleString();
}

function statusBadge(status) {
    const classes = {
        'Active': 'badge-active',
        'Completed': 'badge-completed',
        'On Hold': 'badge-hold',
        'Cancelled': 'badge-cancelled',
    };
    return `<span class="badge ${classes[status] || 'badge-active'}">${escapeHtml(status)}</span>`;
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

function truncate(str, len) {
    if (!str) return '';
    str = String(str);
    return str.length > len ? escapeHtml(str.substring(0, len)) + '...' : escapeHtml(str);
}

function showToast(message, type = '') {
    const toast = $('#toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => { toast.className = 'toast'; }, 4000);
}
