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

        // Row 0 is header: columns map to specific fields
        // Col 0: Activity code/description
        // Col 1: PIP Narrative & Targets
        // Col 2: (target values)
        // Col 3: Y3 AWP Narrative
        // Col 4: Status
        // Col 5: Required Programming Adjustments
        // Col 6: What will be carried out in Y4?
        // Col 7: Sustainability measures
        // Col 8: Who will carry this out?
        // Col 9-10: Which quarter(s)?

        const activities = [];
        let currentOutcome = '';
        let currentOutput = '';
        let currentIndicator = '';

        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            const col0 = String(row[0] || '').trim();
            const col1 = String(row[1] || '').trim();
            const col2 = String(row[2] || '').trim();
            const col3 = String(row[3] || '').trim();
            const col4 = String(row[4] || '').trim();
            const col5 = String(row[5] || '').trim();
            const col6 = String(row[6] || '').trim();
            const col7 = String(row[7] || '').trim();
            const col8 = String(row[8] || '').trim();
            const col9 = String(row[9] || '').trim();

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
                    // Indicators have targets in col1/col2, store them
                    activities.push({
                        type: 'indicator',
                        code: code,
                        description: col0,
                        indicator_text: col1,
                        target: col2,
                        outcome: currentOutcome,
                        output: currentOutput,
                        status: '',
                        y3_narrative: '',
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
                    pip_narrative: col1,
                    target: col2,
                    y3_narrative: col3,
                    status: col4,
                    adjustments: col5,
                    y4_plan: col6,
                    sustainability: col7,
                    responsible: col8,
                    quarter: col9,
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
                    indicator_text: col1,
                    target: col2,
                    outcome: currentOutcome,
                    output: currentOutput,
                    status: '',
                    y3_narrative: '',
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
