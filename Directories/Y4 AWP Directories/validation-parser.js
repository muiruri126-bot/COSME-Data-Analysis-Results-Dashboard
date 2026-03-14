// ─── Activity Validation Parser ──────────────────────────────
const XLSX = require('xlsx');
const path = require('path');

function parseActivityValidation() {
    const filePath = path.join(__dirname, 'COSME Y4 AWP Activity Validation.xlsx');
    const wb = XLSX.readFile(filePath);
    const outcomes = [];

    wb.SheetNames.forEach(sheetName => {
        const ws = wb.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });

        // Extract outcome code from sheet name (e.g., "1100", "1200", "1300")
        const codeMatch = sheetName.match(/(\d{4})/);
        const outcomeCode = codeMatch ? codeMatch[1] : sheetName;

        const activities = [];
        let currentOutcome = '';
        let currentOutput = '';
        let currentIndicator = '';

        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            const col0 = String(row[0] || '').trim();
            const col1 = String(row[1] || '').trim();

            if (!col0 && !col1) continue;

            // Detect hierarchy level by code pattern
            const codePattern = col0.match(/^(\d{4})\b/);
            if (codePattern) {
                const code = codePattern[1];
                const level = code.length === 4 ? (
                    code.endsWith('00') ? 'outcome' :
                    code.endsWith('0') ? 'output' : 'indicator'
                ) : 'activity';

                if (level === 'outcome') {
                    currentOutcome = col0;
                    continue;
                }
                if (level === 'output') {
                    currentOutput = col0;
                    continue;
                }
                if (level === 'indicator') {
                    currentIndicator = col0;
                    activities.push({
                        type: 'indicator',
                        code: code,
                        description: col0,
                        indicator_text: '',
                        target: '',
                        outcome: currentOutcome,
                        output: currentOutput,
                        status: '',
                        adjustments: '',
                        y4_plan: '',
                        sustainability: '',
                        responsible: '',
                        quarter: ''
                    });
                    continue;
                }
            }

            // Activity rows — have code like "1111.1", "1211.3" etc.
            const activityCode = col0.match(/^(\d{4}\.\d+)/);
            if (activityCode || (col0 && !col0.match(/^\d{4}\b/) && col1)) {
                activities.push({
                    type: 'activity',
                    code: activityCode ? activityCode[1] : '',
                    description: col0,
                    pip_narrative: '',
                    target: '',
                    status: '',
                    adjustments: '',
                    y4_plan: '',
                    sustainability: '',
                    responsible: '',
                    quarter: '',
                    outcome: currentOutcome,
                    output: currentOutput,
                    indicator: currentIndicator
                });
            }

            // Indicator rows that appear without col0 (continuation)
            if (!col0 && col1 && col1.match(/^\d{4}[a-z]/)) {
                activities.push({
                    type: 'indicator',
                    code: '',
                    description: '',
                    indicator_text: '',
                    target: '',
                    outcome: currentOutcome,
                    output: currentOutput,
                    status: '',
                    adjustments: '',
                    y4_plan: '',
                    sustainability: '',
                    responsible: '',
                    quarter: ''
                });
            }
        }

        outcomes.push({
            sheetName,
            outcomeCode,
            outcomeDescription: currentOutcome || sheetName,
            activities
        });
    });

    return outcomes;
}

module.exports = { parseActivityValidation };
