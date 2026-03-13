const Database = require('better-sqlite3');
const path = require('path');

class DirectoryDB {
    constructor() {
        this.db = new Database(path.join(__dirname, 'directory.db'));
        this.initialize();
    }

    initialize() {
        this.db.pragma('journal_mode = WAL');

        this.db.exec(`
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thematic_area TEXT NOT NULL,
                sub_theme TEXT DEFAULT '',
                strategy_code TEXT NOT NULL,
                strategy_description TEXT DEFAULT '',
                activity_number INTEGER,
                activity_description TEXT NOT NULL,
                resources_required TEXT DEFAULT '',
                technical_notes TEXT DEFAULT '',
                strategic_issues TEXT DEFAULT '[]',
                status TEXT DEFAULT 'Not Started',
                progress_notes TEXT DEFAULT '',
                responsible_person TEXT DEFAULT '',
                target_date TEXT DEFAULT '',
                completion_date TEXT DEFAULT '',
                last_updated TEXT DEFAULT (datetime('now')),
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS update_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER,
                field_changed TEXT,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT DEFAULT 'user',
                changed_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (activity_id) REFERENCES activities(id)
            );

            CREATE TABLE IF NOT EXISTS validation_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sheet_name TEXT NOT NULL,
                outcome_code TEXT NOT NULL,
                outcome_description TEXT DEFAULT '',
                type TEXT NOT NULL,
                code TEXT DEFAULT '',
                description TEXT DEFAULT '',
                indicator_text TEXT DEFAULT '',
                pip_narrative TEXT DEFAULT '',
                target TEXT DEFAULT '',
                y3_narrative TEXT DEFAULT '',
                status TEXT DEFAULT '',
                adjustments TEXT DEFAULT '',
                y4_plan TEXT DEFAULT '',
                sustainability TEXT DEFAULT '',
                responsible TEXT DEFAULT '',
                quarter TEXT DEFAULT '',
                outcome_ref TEXT DEFAULT '',
                output_ref TEXT DEFAULT '',
                indicator_ref TEXT DEFAULT '',
                sort_order INTEGER DEFAULT 0,
                last_updated TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS workback_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section_name TEXT NOT NULL,
                task_name TEXT NOT NULL,
                marked_weeks TEXT DEFAULT '[]',
                row_index INTEGER DEFAULT 0,
                section_order INTEGER DEFAULT 0,
                task_order INTEGER DEFAULT 0,
                last_updated TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS workback_meta (
                id INTEGER PRIMARY KEY DEFAULT 1,
                months TEXT DEFAULT '[]',
                weeks TEXT DEFAULT '[]'
            );
        `);
    }

    getAllActivities(filters = {}) {
        let query = 'SELECT * FROM activities WHERE 1=1';
        const params = [];

        if (filters.search) {
            query += ` AND (activity_description LIKE ? OR strategy_description LIKE ? OR resources_required LIKE ? OR technical_notes LIKE ?)`;
            const s = `%${filters.search}%`;
            params.push(s, s, s, s);
        }
        if (filters.thematic_area) {
            query += ' AND thematic_area = ?';
            params.push(filters.thematic_area);
        }
        if (filters.sub_theme) {
            query += ' AND sub_theme = ?';
            params.push(filters.sub_theme);
        }
        if (filters.strategy_code) {
            query += ' AND strategy_code = ?';
            params.push(filters.strategy_code);
        }
        if (filters.status) {
            query += ' AND status = ?';
            params.push(filters.status);
        }

        query += ' ORDER BY thematic_area, sub_theme, strategy_code, activity_number';
        return this.db.prepare(query).all(...params);
    }

    getActivityById(id) {
        return this.db.prepare('SELECT * FROM activities WHERE id = ?').get(id);
    }

    createActivity(record) {
        const stmt = this.db.prepare(`
            INSERT INTO activities 
            (thematic_area, sub_theme, strategy_code, strategy_description,
             activity_number, activity_description, resources_required, technical_notes,
             strategic_issues, status, progress_notes, responsible_person, target_date, completion_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);
        const result = stmt.run(
            record.thematic_area, record.sub_theme || '', record.strategy_code,
            record.strategy_description || '', record.activity_number || 0,
            record.activity_description, record.resources_required || '',
            record.technical_notes || '', record.strategic_issues || '[]',
            record.status || 'Not Started', record.progress_notes || '',
            record.responsible_person || '', record.target_date || '',
            record.completion_date || ''
        );
        return { id: result.lastInsertRowid, ...record };
    }

    updateActivity(id, updates) {
        const existing = this.getActivityById(id);
        if (!existing) return null;

        const logStmt = this.db.prepare(`
            INSERT INTO update_history (activity_id, field_changed, old_value, new_value, changed_by)
            VALUES (?, ?, ?, ?, ?)
        `);

        for (const [key, value] of Object.entries(updates)) {
            if (key === 'id') continue;
            if (existing[key] !== undefined && String(existing[key]) !== String(value)) {
                logStmt.run(id, key, String(existing[key]), String(value), 'user');
            }
        }

        const fields = Object.keys(updates).filter(k => k !== 'id').map(k => `${k} = ?`);
        fields.push("last_updated = datetime('now')");
        const values = Object.keys(updates).filter(k => k !== 'id').map(k => updates[k]);
        values.push(id);

        this.db.prepare(`UPDATE activities SET ${fields.join(', ')} WHERE id = ?`).run(...values);
        return this.getActivityById(id);
    }

    deleteActivity(id) {
        return this.db.prepare('DELETE FROM activities WHERE id = ?').run(id);
    }

    bulkInsert(records) {
        const insert = this.db.transaction((rows) => {
            this.db.prepare('DELETE FROM activities').run();
            let count = 0;
            for (const row of rows) {
                this.createActivity(row);
                count++;
            }
            return count;
        });
        return insert(records);
    }

    getDistinctValues(column) {
        const allowed = ['thematic_area', 'sub_theme', 'strategy_code', 'status', 'responsible_person'];
        if (!allowed.includes(column)) return [];
        return this.db.prepare(
            `SELECT DISTINCT ${column} as value FROM activities WHERE ${column} != '' ORDER BY ${column}`
        ).all().map(r => r.value);
    }

    getUpdateHistory(activityId) {
        return this.db.prepare(
            'SELECT * FROM update_history WHERE activity_id = ? ORDER BY changed_at DESC'
        ).all(activityId);
    }

    getDashboardStats() {
        const stats = {};
        stats.totalActivities = this.db.prepare('SELECT COUNT(*) as count FROM activities').get().count;
        stats.byThematicArea = this.db.prepare(
            `SELECT thematic_area, COUNT(*) as count FROM activities GROUP BY thematic_area ORDER BY thematic_area`
        ).all();
        stats.byStatus = this.db.prepare(
            `SELECT status, COUNT(*) as count FROM activities GROUP BY status ORDER BY count DESC`
        ).all();
        stats.byStrategy = this.db.prepare(
            `SELECT thematic_area, strategy_code, strategy_description, COUNT(*) as count 
             FROM activities GROUP BY thematic_area, strategy_code ORDER BY thematic_area, strategy_code`
        ).all();
        stats.bySubTheme = this.db.prepare(
            `SELECT sub_theme, COUNT(*) as count FROM activities WHERE sub_theme != '' GROUP BY sub_theme`
        ).all();
        return stats;
    }

    // ─── Validation Methods ──────────────────────────────────
    bulkInsertValidation(outcomes) {
        const insert = this.db.transaction((data) => {
            this.db.prepare('DELETE FROM validation_items').run();
            const stmt = this.db.prepare(`
                INSERT INTO validation_items 
                (sheet_name, outcome_code, outcome_description, type, code, description, indicator_text,
                 pip_narrative, target, y3_narrative, status, adjustments, y4_plan,
                 sustainability, responsible, quarter, outcome_ref, output_ref, indicator_ref, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);
            let order = 0;
            for (const outcome of data) {
                for (const a of outcome.activities) {
                    stmt.run(
                        outcome.sheetName, outcome.outcomeCode, outcome.outcomeDescription || '',
                        a.type, a.code || '', a.description || '', a.indicator_text || '',
                        a.pip_narrative || '', a.target || '', a.y3_narrative || '',
                        a.status || '', a.adjustments || '', a.y4_plan || '',
                        a.sustainability || '', a.responsible || '', a.quarter || '',
                        a.outcome || '', a.output || '', a.indicator || '', order++
                    );
                }
            }
            return order;
        });
        return insert(outcomes);
    }

    getAllValidation() {
        const rows = this.db.prepare(
            'SELECT * FROM validation_items ORDER BY sort_order'
        ).all();
        const outcomeMap = new Map();
        for (const row of rows) {
            if (!outcomeMap.has(row.outcome_code)) {
                outcomeMap.set(row.outcome_code, {
                    sheetName: row.sheet_name,
                    outcomeCode: row.outcome_code,
                    outcomeDescription: row.outcome_description || row.sheet_name,
                    activities: []
                });
            }
            outcomeMap.get(row.outcome_code).activities.push(row);
        }
        return Array.from(outcomeMap.values());
    }

    updateValidationItem(id, updates) {
        const existing = this.db.prepare('SELECT * FROM validation_items WHERE id = ?').get(id);
        if (!existing) return null;
        const allowed = ['status', 'adjustments', 'y4_plan', 'sustainability', 'responsible', 'quarter', 'target'];
        const safe = {};
        for (const key of allowed) {
            if (updates[key] !== undefined) safe[key] = updates[key];
        }
        if (Object.keys(safe).length === 0) return existing;
        const fields = Object.keys(safe).map(k => `${k} = ?`);
        fields.push("last_updated = datetime('now')");
        const values = Object.keys(safe).map(k => safe[k]);
        values.push(id);
        this.db.prepare(`UPDATE validation_items SET ${fields.join(', ')} WHERE id = ?`).run(...values);
        return this.db.prepare('SELECT * FROM validation_items WHERE id = ?').get(id);
    }

    // ─── Workback Methods ────────────────────────────────────
    bulkInsertWorkback(data) {
        this.db.transaction(() => {
            this.db.prepare('DELETE FROM workback_tasks').run();
            this.db.prepare('DELETE FROM workback_meta').run();
            this.db.prepare(
                'INSERT INTO workback_meta (id, months, weeks) VALUES (1, ?, ?)'
            ).run(JSON.stringify(data.months), JSON.stringify(data.weeks));
            const stmt = this.db.prepare(`
                INSERT INTO workback_tasks (section_name, task_name, marked_weeks, row_index, section_order, task_order)
                VALUES (?, ?, ?, ?, ?, ?)
            `);
            let sectionOrder = 0;
            for (const section of data.sections) {
                let taskOrder = 0;
                for (const task of section.tasks) {
                    stmt.run(section.name, task.name, JSON.stringify(task.markedWeeks), task.rowIndex, sectionOrder, taskOrder++);
                }
                sectionOrder++;
            }
        })();
    }

    getWorkbackData() {
        const meta = this.db.prepare('SELECT * FROM workback_meta WHERE id = 1').get();
        if (!meta) return null;
        const tasks = this.db.prepare('SELECT * FROM workback_tasks ORDER BY section_order, task_order').all();
        const sections = [];
        let currentSection = null;
        for (const t of tasks) {
            if (!currentSection || currentSection.name !== t.section_name) {
                currentSection = { name: t.section_name, tasks: [] };
                sections.push(currentSection);
            }
            currentSection.tasks.push({
                id: t.id, name: t.task_name,
                markedWeeks: JSON.parse(t.marked_weeks), rowIndex: t.row_index
            });
        }
        return { months: JSON.parse(meta.months), weeks: JSON.parse(meta.weeks), sections };
    }

    toggleWorkbackCell(taskId, col) {
        const task = this.db.prepare('SELECT * FROM workback_tasks WHERE id = ?').get(taskId);
        if (!task) return null;
        const weeks = JSON.parse(task.marked_weeks);
        const existingIdx = weeks.findIndex(w => w.col === col);
        if (existingIdx >= 0) {
            weeks.splice(existingIdx, 1);
            this.db.prepare("UPDATE workback_tasks SET marked_weeks = ?, last_updated = datetime('now') WHERE id = ?")
                .run(JSON.stringify(weeks), taskId);
            return { id: taskId, marked: false };
        }
        const meta = this.db.prepare('SELECT weeks FROM workback_meta WHERE id = 1').get();
        const allWeeks = JSON.parse(meta.weeks);
        const weekInfo = allWeeks.find(w => w.col === col);
        if (weekInfo) weeks.push({ weekNum: weekInfo.weekNum, monthLabel: weekInfo.monthLabel, col });
        this.db.prepare("UPDATE workback_tasks SET marked_weeks = ?, last_updated = datetime('now') WHERE id = ?")
            .run(JSON.stringify(weeks), taskId);
        return { id: taskId, marked: true };
    }

    close() {
        this.db.close();
    }
}

module.exports = DirectoryDB;
