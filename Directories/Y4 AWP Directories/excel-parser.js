const XLSX = require('xlsx');
const path = require('path');

const EXCEL_FILE = path.join(__dirname, 'COSME Y4 Detailed Activities.xlsx');

function parseExcel() {
    const wb = XLSX.readFile(EXCEL_FILE);
    const allData = [];

    for (const sheetName of wb.SheetNames) {
        const ws = wb.Sheets[sheetName];
        const range = XLSX.utils.decode_range(ws['!ref']);
        const cell = (r, c) => {
            const addr = XLSX.utils.encode_cell({ r, c });
            const v = ws[addr];
            return v && v.v !== undefined ? String(v.v).trim() : '';
        };

        let currentTheme = sheetName;
        let currentStrategy = '';
        let currentStrategyTheme = '';
        let strategicIssues = [];
        let inStrategicIssues = false;
        let inActivities = false;

        for (let r = range.s.r; r <= range.e.r; r++) {
            const colB = cell(r, 1); // B
            const colC = cell(r, 2); // C
            const colE = cell(r, 4); // E
            const colK = cell(r, 10); // K
            const colL = cell(r, 11); // L
            const colM = cell(r, 12); // M
            const colR = cell(r, 17); // R

            // Detect top-level theme headers (e.g., SEAWEED, FORESTRY, EBA, GRAPP, etc.)
            if (colB && !colC && !colE && !colL && !colR) {
                const upper = colB.toUpperCase();
                if (['SEAWEED', 'FORESTRY', 'EBA', 'GRAPP', 'HOUSEHOLD ACTION PLANS',
                    'SCHOOLS', 'REGENERATIVE AGRO', 'VSLA'].includes(upper) ||
                    upper.startsWith('HOUSEHOLD')) {
                    currentTheme = colB;
                    inStrategicIssues = false;
                    inActivities = false;
                    strategicIssues = [];
                    continue;
                }
            }

            // Strategic Issues section
            if (colB === 'Strategic Issues identified' || colB === 'Strategic Issues identified ') {
                inStrategicIssues = true;
                inActivities = false;
                strategicIssues = [];
                continue;
            }

            // Capture strategic issues numbered 1-8
            if (inStrategicIssues && /^\d+$/.test(colB) && colC) {
                strategicIssues.push({ number: parseInt(colB), issue: colC, points: colM || '' });
                continue;
            }

            // Detect strategy headers (A, B, C, D, E.)
            if (/^[A-E]\.?$/.test(colB) && colC.startsWith('Implementation Strategy')) {
                currentStrategy = colB.replace('.', '');
                currentStrategyTheme = colE || '';
                inStrategicIssues = false;
                inActivities = false;
                continue;
            }

            // Detect activities header row
            if (colB === 'Activities') {
                inActivities = true;
                continue;
            }

            // Parse activity rows (numbered 1-10)
            if (inActivities && /^\d+$/.test(colB)) {
                const activityText = colC;
                if (!activityText) continue; // skip empty numbered rows

                allData.push({
                    thematic_area: sheetName,
                    sub_theme: currentTheme !== sheetName ? currentTheme : '',
                    strategy_code: currentStrategy,
                    strategy_description: currentStrategyTheme,
                    activity_number: parseInt(colB),
                    activity_description: activityText,
                    resources_required: colL || '',
                    technical_notes: colR || '',
                    strategic_issues: JSON.stringify(strategicIssues),
                    status: 'Not Started',
                    progress_notes: '',
                    responsible_person: '',
                    target_date: '',
                    completion_date: '',
                });
            }
        }
    }

    return allData;
}

module.exports = { parseExcel, EXCEL_FILE };
