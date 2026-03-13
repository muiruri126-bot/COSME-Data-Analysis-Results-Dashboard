// ─── COSME Y4 AWP Directory – Frontend ─────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);
let allActivities = [];
let currentFilters = {};

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadActivities();
    setupListeners();
});

// ─── Event Listeners ─────────────────────────────────────────
function setupListeners() {
    $('#btnAddNew').addEventListener('click', () => openModal());
    $('#btnReload').addEventListener('click', reloadFromExcel);
    $('#btnExport').addEventListener('click', exportCSV);

    let timer;
    $('#searchInput').addEventListener('input', (e) => {
        clearTimeout(timer);
        timer = setTimeout(() => { currentFilters.search = e.target.value; loadActivities(); }, 300);
    });
    $('#filterStrategy').addEventListener('change', (e) => { currentFilters.strategy_code = e.target.value; loadActivities(); });
    $('#filterStatus').addEventListener('change', (e) => { currentFilters.status = e.target.value; loadActivities(); });

    $('#modalClose').addEventListener('click', closeModal);
    $('#btnCancel').addEventListener('click', closeModal);
    $('#modalOverlay').addEventListener('click', (e) => { if (e.target === $('#modalOverlay')) closeModal(); });
    $('#historyClose').addEventListener('click', () => $('#historyOverlay').classList.remove('active'));
    $('#historyOverlay').addEventListener('click', (e) => { if (e.target === $('#historyOverlay')) $('#historyOverlay').classList.remove('active'); });
    $('#activityForm').addEventListener('submit', handleSubmit);

    // Module navigation
    $$('.module-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            $$('.module-tab').forEach(t => t.classList.remove('active'));
            $$('.module-panel').forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            const mod = tab.dataset.module;
            $(`#panel${mod.charAt(0).toUpperCase() + mod.slice(1)}`).classList.add('active');

            if (mod === 'workback' && !workbackLoaded) loadWorkback();
            if (mod === 'validation' && !validationLoaded) loadValidation();
        });
    });
}

// ─── API Helpers ─────────────────────────────────────────────
async function api(endpoint, opts = {}) {
    const res = await fetch(endpoint, {
        headers: { 'Content-Type': 'application/json' },
        ...opts,
        body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.error || res.statusText); }
    return res.json();
}

// ─── Load Stats ──────────────────────────────────────────────
async function loadStats() {
    try {
        const s = await api('/api/stats');
        $('#statTotal').textContent = s.totalActivities;
        const statusCount = (name) => (s.byStatus.find(x => x.status === name) || {}).count || 0;
        $('#statNotStarted').textContent = statusCount('Not Started');
        $('#statInProgress').textContent = statusCount('In Progress');
        $('#statCompleted').textContent = statusCount('Completed');

        // Build theme tabs
        const tabs = $('#themeTabs');
        tabs.innerHTML = '<button class="tab active" data-theme="">All Areas</button>';
        s.byThematicArea.forEach(t => {
            tabs.innerHTML += `<button class="tab" data-theme="${esc(t.thematic_area)}">${esc(t.thematic_area)} <small>(${t.count})</small></button>`;
        });
        tabs.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                currentFilters.thematic_area = tab.dataset.theme;
                loadActivities();
            });
        });
    } catch (e) { console.error(e); }
}

// ─── Load Activities ─────────────────────────────────────────
async function loadActivities() {
    try {
        const params = new URLSearchParams();
        Object.entries(currentFilters).forEach(([k, v]) => { if (v) params.set(k, v); });
        allActivities = await api(`/api/activities?${params}`);
        renderContent(allActivities);
    } catch (e) {
        $('#contentArea').innerHTML = `<div class="loading-msg" style="color:var(--danger)">Failed to load</div>`;
    }
}

// ─── Render Grouped Content ─────────────────────────────────
function renderContent(activities) {
    const area = $('#contentArea');
    if (activities.length === 0) {
        area.innerHTML = '<div class="loading-msg">No activities found</div>';
        return;
    }

    // Group: thematic_area → sub_theme → strategy_code
    const groups = {};
    activities.forEach(a => {
        const theme = a.thematic_area;
        const sub = a.sub_theme || '';
        const strat = a.strategy_code;
        const key = `${theme}||${sub}||${strat}`;
        if (!groups[key]) {
            groups[key] = {
                thematic_area: theme,
                sub_theme: sub,
                strategy_code: strat,
                strategy_description: a.strategy_description,
                strategic_issues: a.strategic_issues,
                activities: []
            };
        }
        groups[key].activities.push(a);
    });

    let html = '';
    let lastTheme = '';
    let lastSub = '';

    Object.values(groups).forEach(g => {
        // Show thematic area header when it changes
        if (g.thematic_area !== lastTheme) {
            if (lastTheme) html += '<div style="height:20px"></div>';
            html += `<h2 style="font-size:1rem;color:var(--primary);padding:8px 0;border-bottom:2px solid var(--primary);margin-bottom:8px;">
                ${esc(g.thematic_area)}</h2>`;
            lastTheme = g.thematic_area;
            lastSub = '';

            // Show strategic issues
            try {
                const issues = JSON.parse(g.strategic_issues);
                if (issues.length > 0) {
                    html += `<div class="issues-panel"><h4>Strategic Issues Identified</h4><ol>`;
                    issues.forEach(i => { html += `<li>${esc(i.issue)}</li>`; });
                    html += `</ol></div>`;
                }
            } catch (e) {}
        }

        // Sub-theme divider
        if (g.sub_theme && g.sub_theme !== lastSub) {
            html += `<div class="sub-theme-divider">${esc(g.sub_theme)}</div>`;
            lastSub = g.sub_theme;
        }

        // Strategy group card
        html += `<div class="strategy-group">
            <div class="strategy-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <div class="strategy-code">${esc(g.strategy_code)}</div>
                <div class="strategy-title">
                    <strong>Strategy ${esc(g.strategy_code)}: ${esc(g.strategy_description || 'Implementation Strategy')}</strong>
                    <div class="theme-label">${esc(g.thematic_area)}${g.sub_theme ? ' / ' + esc(g.sub_theme) : ''}</div>
                </div>
                <span class="strategy-count">${g.activities.length} activities</span>
                <span class="strategy-chevron">&#9660;</span>
            </div>
            <div class="activity-list">`;

        g.activities.forEach(a => {
            html += `<div class="activity-row">
                <div class="activity-num">${a.activity_number}</div>
                <div class="activity-desc">
                    ${esc(a.activity_description)}
                    ${a.resources_required ? `<div class="resources">${esc(a.resources_required)}</div>` : ''}
                    ${a.technical_notes ? `<div class="tech-notes">${esc(a.technical_notes)}</div>` : ''}
                </div>
                <div>${a.responsible_person ? esc(a.responsible_person) : '<span style="color:var(--text-light);font-size:0.75rem">Unassigned</span>'}</div>
                <div>${statusBadge(a.status)}</div>
                <div class="activity-actions">
                    <button class="btn btn-sm btn-outline" onclick="editActivity(${a.id})">Track/Update</button>
                    <button class="btn btn-sm btn-outline" onclick="viewHistory(${a.id})">History</button>
                </div>
            </div>`;
        });

        html += `</div></div>`;
    });

    area.innerHTML = html;
}

// ─── Modal ───────────────────────────────────────────────────
function openModal(activity = null) {
    const form = $('#activityForm');
    form.reset();
    $('#frmId').value = '';

    if (activity) {
        // Edit mode: show editable activity fields, pre-filled
        $('#modalTitle').textContent = 'Edit Activity';
        $('#frmId').value = activity.id;
        $('#newActivityFields').style.display = 'block';
        // Fill activity fields
        $('#frmThematic').value = activity.thematic_area || '';
        $('#frmSubTheme').value = activity.sub_theme || '';
        $('#frmStrategyCode').value = activity.strategy_code || 'A';
        $('#frmStrategyDesc').value = activity.strategy_description || '';
        $('#frmActivityDesc').value = activity.activity_description || '';
        $('#frmResources').value = activity.resources_required || '';
        $('#frmTechNotes').value = activity.technical_notes || '';
        // Fill tracking fields
        $('#frmStatus').value = activity.status || 'Not Started';
        $('#frmResponsible').value = activity.responsible_person || '';
        $('#frmTargetDate').value = activity.target_date || '';
        $('#frmCompletionDate').value = activity.completion_date || '';
        $('#frmProgressNotes').value = activity.progress_notes || '';
    } else {
        // New mode: show new-activity fields, hide readonly
        $('#modalTitle').textContent = 'Add New Activity';
        $('#newActivityFields').style.display = 'block';
    }

    $('#modalOverlay').classList.add('active');
}

function closeModal() { $('#modalOverlay').classList.remove('active'); }

async function editActivity(id) {
    try {
        const a = await api(`/api/activities/${id}`);
        openModal(a);
    } catch (e) { toast('Failed to load activity', 'error'); }
}

async function handleSubmit(e) {
    e.preventDefault();
    const id = $('#frmId').value;

    if (id) {
        // Update all fields
        const data = {
            thematic_area: $('#frmThematic').value,
            sub_theme: $('#frmSubTheme').value,
            strategy_code: $('#frmStrategyCode').value,
            strategy_description: $('#frmStrategyDesc').value,
            activity_description: $('#frmActivityDesc').value,
            resources_required: $('#frmResources').value,
            technical_notes: $('#frmTechNotes').value,
            status: $('#frmStatus').value,
            responsible_person: $('#frmResponsible').value,
            target_date: $('#frmTargetDate').value,
            completion_date: $('#frmCompletionDate').value,
            progress_notes: $('#frmProgressNotes').value,
        };
        try {
            await api(`/api/activities/${id}`, { method: 'PUT', body: data });
            toast('Activity updated', 'success');
            closeModal(); loadActivities(); loadStats();
        } catch (e) { toast(e.message, 'error'); }
    } else {
        // Create new
        const data = {
            thematic_area: $('#frmThematic').value,
            sub_theme: $('#frmSubTheme').value,
            strategy_code: $('#frmStrategyCode').value,
            strategy_description: $('#frmStrategyDesc').value,
            activity_description: $('#frmActivityDesc').value,
            resources_required: $('#frmResources').value,
            technical_notes: $('#frmTechNotes').value,
            status: $('#frmStatus').value,
            responsible_person: $('#frmResponsible').value,
            target_date: $('#frmTargetDate').value,
            completion_date: $('#frmCompletionDate').value,
            progress_notes: $('#frmProgressNotes').value,
        };
        if (!data.activity_description) { toast('Activity description is required', 'error'); return; }
        try {
            await api('/api/activities', { method: 'POST', body: data });
            toast('Activity created', 'success');
            closeModal(); loadActivities(); loadStats();
        } catch (e) { toast(e.message, 'error'); }
    }
}

// ─── History ─────────────────────────────────────────────────
async function viewHistory(id) {
    try {
        const history = await api(`/api/activities/${id}/history`);
        const body = $('#historyBody');
        if (history.length === 0) {
            body.innerHTML = '<p style="text-align:center;color:var(--text-light);padding:20px">No updates recorded yet</p>';
        } else {
            body.innerHTML = `<ul class="history-list">${history.map(h => `
                <li class="history-item">
                    <span class="history-field">${esc(h.field_changed)}</span>:
                    <span class="history-old">${esc(h.old_value)}</span> &rarr;
                    <span class="history-new">${esc(h.new_value)}</span>
                    <span class="history-time">${new Date(h.changed_at).toLocaleString()}</span>
                </li>`).join('')}</ul>`;
        }
        $('#historyOverlay').classList.add('active');
    } catch (e) { toast('Failed to load history', 'error'); }
}

// ─── Reload from Excel ───────────────────────────────────────
async function reloadFromExcel() {
    const btn = $('#btnReload');
    btn.disabled = true;
    btn.innerHTML = 'Reloading...';
    try {
        const r = await api('/api/reload', { method: 'POST' });
        toast(r.message, 'success');
        loadActivities();
        loadStats();
    } catch (e) { toast('Reload failed: ' + e.message, 'error'); }
    finally {
        btn.disabled = false;
        btn.innerHTML = 'Reload Excel';
    }
}

// ─── CSV Export ──────────────────────────────────────────────
function exportCSV() {
    if (!allActivities.length) { toast('No data to export', 'error'); return; }
    const headers = ['Thematic Area', 'Sub-theme', 'Strategy', 'Strategy Description', '#',
        'Activity', 'Resources Required', 'Technical Notes', 'Status', 'Responsible', 'Target Date',
        'Completion Date', 'Progress Notes'];
    const keys = ['thematic_area', 'sub_theme', 'strategy_code', 'strategy_description', 'activity_number',
        'activity_description', 'resources_required', 'technical_notes', 'status', 'responsible_person',
        'target_date', 'completion_date', 'progress_notes'];
    let csv = headers.join(',') + '\n';
    allActivities.forEach(r => {
        csv += keys.map(k => `"${String(r[k] || '').replace(/"/g, '""')}"`).join(',') + '\n';
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `COSME_Y4_Activities_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    toast('CSV exported', 'success');
}

// ─── Utilities ───────────────────────────────────────────────
function statusBadge(status) {
    const cls = { 'Not Started': 'badge-not-started', 'In Progress': 'badge-in-progress',
        'Completed': 'badge-completed', 'On Hold': 'badge-on-hold' };
    return `<span class="badge ${cls[status] || 'badge-not-started'}">${esc(status)}</span>`;
}

function esc(s) {
    if (!s) return '';
    const d = document.createElement('div');
    d.textContent = String(s);
    return d.innerHTML;
}

function toast(msg, type = '') {
    const t = $('#toast');
    t.textContent = msg;
    t.className = `toast show ${type}`;
    setTimeout(() => { t.className = 'toast'; }, 4000);
}

// ─── MODULE 2: Workback Schedule ─────────────────────────────
let workbackLoaded = false;

async function loadWorkback() {
    try {
        const data = await api('/api/workback');
        workbackLoaded = true;
        renderWorkback(data);
    } catch (e) {
        $('#workbackContent').innerHTML = `<div class="loading-msg" style="color:var(--danger)">Failed to load workback schedule</div>`;
    }
}

function renderWorkback(data) {
    const { months, weeks, sections } = data;
    const totalWeeks = weeks.length;

    let html = '<div class="gantt-wrapper"><table class="gantt-table"><thead>';

    // Month header row
    html += '<tr><th class="gantt-task-header">Task</th>';
    months.forEach(m => {
        const span = weeks.filter(w => w.monthLabel === m.label).length;
        if (span > 0) html += `<th colspan="${span}" class="gantt-month">${esc(m.label)}</th>`;
    });
    html += '</tr>';

    // Week number row
    html += '<tr><th class="gantt-task-header"></th>';
    weeks.forEach(w => {
        html += `<th class="gantt-week">W${w.weekNum}</th>`;
    });
    html += '</tr></thead><tbody>';

    // Render sections and tasks
    sections.forEach(section => {
        html += `<tr class="gantt-section-row"><td colspan="${totalWeeks + 1}" class="gantt-section-label">${esc(section.name)}</td></tr>`;

        section.tasks.forEach(task => {
            html += `<tr class="gantt-task-row"><td class="gantt-task-name">${esc(task.name)}</td>`;
            weeks.forEach(w => {
                const marked = task.markedWeeks.some(mw => mw.col === w.col);
                html += `<td class="gantt-cell${marked ? ' gantt-marked' : ''}"></td>`;
            });
            html += '</tr>';
        });
    });

    html += '</tbody></table></div>';
    $('#workbackContent').innerHTML = html;
}

// ─── MODULE 3: Activity Validation ───────────────────────────
let validationLoaded = false;
let validationData = [];

async function loadValidation() {
    try {
        validationData = await api('/api/validation');
        validationLoaded = true;

        // Build outcome tabs
        const tabs = $('#validationTabs');
        tabs.innerHTML = '';
        validationData.forEach((outcome, i) => {
            tabs.innerHTML += `<button class="tab${i === 0 ? ' active' : ''}" data-vidx="${i}">${esc(outcome.outcomeCode)}</button>`;
        });
        tabs.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                renderValidation(parseInt(tab.dataset.vidx));
            });
        });

        if (validationData.length > 0) renderValidation(0);
    } catch (e) {
        $('#validationContent').innerHTML = `<div class="loading-msg" style="color:var(--danger)">Failed to load validation data</div>`;
    }
}

function renderValidation(idx) {
    const outcome = validationData[idx];
    if (!outcome) return;

    let html = `<div class="validation-list">`;

    outcome.activities.forEach(a => {
        if (a.type === 'indicator') {
            html += `<div class="val-card val-indicator">
                <div class="val-code">${esc(a.code || '')}</div>
                <div class="val-body">
                    <div class="val-desc">${esc(a.description || a.indicator_text)}</div>
                    ${a.target ? `<div class="val-meta"><strong>Target:</strong> ${esc(a.target)}</div>` : ''}
                    ${a.indicator_text && a.description ? `<div class="val-meta"><strong>Indicator:</strong> ${esc(a.indicator_text)}</div>` : ''}
                </div>
            </div>`;
            return;
        }

        const statusClass = a.status === 'Complete' ? 'badge-completed' :
            a.status === 'Ongoing' ? 'badge-in-progress' :
            a.status === 'Not Started' ? 'badge-not-started' : 'badge-not-started';

        html += `<div class="val-card val-activity">
            <div class="val-code">${esc(a.code || '')}</div>
            <div class="val-body">
                <div class="val-desc">${esc(a.description)}</div>
                ${a.status ? `<span class="badge ${statusClass}">${esc(a.status)}</span>` : ''}
                ${a.pip_narrative ? `<details class="val-details"><summary>PIP Narrative</summary><p>${esc(a.pip_narrative)}</p></details>` : ''}
                ${a.y3_narrative ? `<details class="val-details"><summary>Y3 AWP Narrative</summary><p>${esc(a.y3_narrative)}</p></details>` : ''}
                ${a.adjustments ? `<details class="val-details"><summary>Programming Adjustments</summary><p>${esc(a.adjustments)}</p></details>` : ''}
                ${a.y4_plan ? `<details class="val-details"><summary>Y4 Plan</summary><p>${esc(a.y4_plan)}</p></details>` : ''}
                ${a.sustainability ? `<details class="val-details"><summary>Sustainability Measures</summary><p>${esc(a.sustainability)}</p></details>` : ''}
                <div class="val-footer">
                    ${a.responsible ? `<span class="val-meta"><strong>Responsible:</strong> ${esc(a.responsible)}</span>` : ''}
                    ${a.quarter ? `<span class="val-meta"><strong>Quarter:</strong> ${esc(a.quarter)}</span>` : ''}
                </div>
            </div>
        </div>`;
    });

    html += '</div>';
    $('#validationContent').innerHTML = html;
}
