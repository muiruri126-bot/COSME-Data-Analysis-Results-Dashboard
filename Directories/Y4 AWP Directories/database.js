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
            CREATE TABLE IF NOT EXISTS directory_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_name TEXT NOT NULL,
                designation TEXT DEFAULT '',
                department TEXT DEFAULT '',
                duty_station TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                project_code TEXT DEFAULT '',
                activity_code TEXT DEFAULT '',
                activity_description TEXT DEFAULT '',
                budget_line TEXT DEFAULT '',
                annual_budget REAL DEFAULT 0,
                q1_budget REAL DEFAULT 0,
                q2_budget REAL DEFAULT 0,
                q3_budget REAL DEFAULT 0,
                q4_budget REAL DEFAULT 0,
                spent_to_date REAL DEFAULT 0,
                balance REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                partner_organization TEXT DEFAULT '',
                implementation_area TEXT DEFAULT '',
                target_beneficiaries INTEGER DEFAULT 0,
                achieved_beneficiaries INTEGER DEFAULT 0,
                remarks TEXT DEFAULT '',
                last_updated TEXT DEFAULT (datetime('now')),
                synced_from_sharepoint INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_time TEXT DEFAULT (datetime('now')),
                records_synced INTEGER DEFAULT 0,
                status TEXT DEFAULT 'success',
                error_message TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS update_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER,
                field_changed TEXT,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT DEFAULT 'system',
                changed_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (record_id) REFERENCES directory_records(id)
            );
        `);
    }

    getAllRecords(filters = {}) {
        let query = 'SELECT * FROM directory_records WHERE 1=1';
        const params = [];

        if (filters.search) {
            query += ` AND (staff_name LIKE ? OR department LIKE ? OR activity_description LIKE ? OR project_code LIKE ?)`;
            const searchTerm = `%${filters.search}%`;
            params.push(searchTerm, searchTerm, searchTerm, searchTerm);
        }
        if (filters.department) {
            query += ' AND department = ?';
            params.push(filters.department);
        }
        if (filters.status) {
            query += ' AND status = ?';
            params.push(filters.status);
        }
        if (filters.duty_station) {
            query += ' AND duty_station = ?';
            params.push(filters.duty_station);
        }

        query += ' ORDER BY last_updated DESC';
        return this.db.prepare(query).all(...params);
    }

    getRecordById(id) {
        return this.db.prepare('SELECT * FROM directory_records WHERE id = ?').get(id);
    }

    createRecord(record) {
        const stmt = this.db.prepare(`
            INSERT INTO directory_records 
            (staff_name, designation, department, duty_station, phone, email,
             project_code, activity_code, activity_description, budget_line,
             annual_budget, q1_budget, q2_budget, q3_budget, q4_budget,
             spent_to_date, balance, status, partner_organization,
             implementation_area, target_beneficiaries, achieved_beneficiaries, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        const result = stmt.run(
            record.staff_name, record.designation, record.department,
            record.duty_station, record.phone, record.email,
            record.project_code, record.activity_code, record.activity_description,
            record.budget_line, record.annual_budget || 0,
            record.q1_budget || 0, record.q2_budget || 0,
            record.q3_budget || 0, record.q4_budget || 0,
            record.spent_to_date || 0, record.balance || 0,
            record.status || 'Active', record.partner_organization,
            record.implementation_area, record.target_beneficiaries || 0,
            record.achieved_beneficiaries || 0, record.remarks
        );

        return { id: result.lastInsertRowid, ...record };
    }

    updateRecord(id, updates) {
        const existing = this.getRecordById(id);
        if (!existing) return null;

        // Log changes
        const logStmt = this.db.prepare(`
            INSERT INTO update_history (record_id, field_changed, old_value, new_value, changed_by)
            VALUES (?, ?, ?, ?, ?)
        `);

        for (const [key, value] of Object.entries(updates)) {
            if (existing[key] !== undefined && String(existing[key]) !== String(value)) {
                logStmt.run(id, key, String(existing[key]), String(value), 'user');
            }
        }

        const fields = Object.keys(updates)
            .filter(k => k !== 'id')
            .map(k => `${k} = ?`);
        fields.push("last_updated = datetime('now')");

        const values = Object.keys(updates)
            .filter(k => k !== 'id')
            .map(k => updates[k]);
        values.push(id);

        const stmt = this.db.prepare(
            `UPDATE directory_records SET ${fields.join(', ')} WHERE id = ?`
        );
        stmt.run(...values);

        return this.getRecordById(id);
    }

    deleteRecord(id) {
        return this.db.prepare('DELETE FROM directory_records WHERE id = ?').run(id);
    }

    bulkUpsertFromSharePoint(records) {
        const upsert = this.db.transaction((rows) => {
            let count = 0;
            for (const row of rows) {
                const mapped = this.mapSharePointRow(row);
                if (!mapped.staff_name && !mapped.activity_code) continue;

                // Check if record exists by matching key fields
                const existing = this.db.prepare(
                    `SELECT id FROM directory_records 
                     WHERE staff_name = ? AND activity_code = ? AND synced_from_sharepoint = 1`
                ).get(mapped.staff_name, mapped.activity_code);

                if (existing) {
                    mapped.id = existing.id;
                    this.updateRecord(existing.id, { ...mapped, synced_from_sharepoint: 1 });
                } else {
                    this.createRecord({ ...mapped, synced_from_sharepoint: 1 });
                }
                count++;
            }

            this.db.prepare(`
                INSERT INTO sync_log (records_synced, status)
                VALUES (?, 'success')
            `).run(count);

            return count;
        });

        return upsert(records);
    }

    mapSharePointRow(row) {
        // Map common Excel column names to our schema
        const mapping = {
            staff_name: row['Staff Name'] || row['Name'] || row['staff_name'] || row['Employee'] || '',
            designation: row['Designation'] || row['Title'] || row['Position'] || row['designation'] || '',
            department: row['Department'] || row['Unit'] || row['department'] || '',
            duty_station: row['Duty Station'] || row['Location'] || row['Station'] || row['duty_station'] || '',
            phone: row['Phone'] || row['Contact'] || row['Tel'] || row['phone'] || '',
            email: row['Email'] || row['E-mail'] || row['email'] || '',
            project_code: row['Project Code'] || row['Project'] || row['project_code'] || '',
            activity_code: row['Activity Code'] || row['Act Code'] || row['activity_code'] || '',
            activity_description: row['Activity Description'] || row['Activity'] || row['Description'] || row['activity_description'] || '',
            budget_line: row['Budget Line'] || row['BL'] || row['budget_line'] || '',
            annual_budget: parseFloat(row['Annual Budget'] || row['Budget'] || row['annual_budget'] || 0),
            q1_budget: parseFloat(row['Q1'] || row['Q1 Budget'] || row['q1_budget'] || 0),
            q2_budget: parseFloat(row['Q2'] || row['Q2 Budget'] || row['q2_budget'] || 0),
            q3_budget: parseFloat(row['Q3'] || row['Q3 Budget'] || row['q3_budget'] || 0),
            q4_budget: parseFloat(row['Q4'] || row['Q4 Budget'] || row['q4_budget'] || 0),
            spent_to_date: parseFloat(row['Spent'] || row['Spent to Date'] || row['Expenditure'] || row['spent_to_date'] || 0),
            balance: parseFloat(row['Balance'] || row['Remaining'] || row['balance'] || 0),
            status: row['Status'] || row['status'] || 'Active',
            partner_organization: row['Partner'] || row['Partner Organization'] || row['IP'] || row['partner_organization'] || '',
            implementation_area: row['Area'] || row['Implementation Area'] || row['Location'] || row['implementation_area'] || '',
            target_beneficiaries: parseInt(row['Target'] || row['Target Beneficiaries'] || row['target_beneficiaries'] || 0),
            achieved_beneficiaries: parseInt(row['Achieved'] || row['Achieved Beneficiaries'] || row['achieved_beneficiaries'] || 0),
            remarks: row['Remarks'] || row['Notes'] || row['Comments'] || row['remarks'] || '',
        };

        return mapping;
    }

    getDistinctValues(column) {
        const allowed = ['department', 'duty_station', 'status', 'project_code', 'partner_organization'];
        if (!allowed.includes(column)) return [];
        return this.db.prepare(
            `SELECT DISTINCT ${column} as value FROM directory_records WHERE ${column} != '' ORDER BY ${column}`
        ).all().map(r => r.value);
    }

    getSyncLog() {
        return this.db.prepare('SELECT * FROM sync_log ORDER BY sync_time DESC LIMIT 20').all();
    }

    getUpdateHistory(recordId) {
        return this.db.prepare(
            'SELECT * FROM update_history WHERE record_id = ? ORDER BY changed_at DESC'
        ).all(recordId);
    }

    getDashboardStats() {
        const stats = {};
        stats.totalRecords = this.db.prepare('SELECT COUNT(*) as count FROM directory_records').get().count;
        stats.activeRecords = this.db.prepare("SELECT COUNT(*) as count FROM directory_records WHERE status = 'Active'").get().count;
        stats.totalBudget = this.db.prepare('SELECT COALESCE(SUM(annual_budget), 0) as total FROM directory_records').get().total;
        stats.totalSpent = this.db.prepare('SELECT COALESCE(SUM(spent_to_date), 0) as total FROM directory_records').get().total;
        stats.totalBalance = this.db.prepare('SELECT COALESCE(SUM(balance), 0) as total FROM directory_records').get().total;
        stats.departments = this.db.prepare("SELECT COUNT(DISTINCT department) as count FROM directory_records WHERE department != ''").get().count;
        stats.lastSync = this.db.prepare('SELECT sync_time FROM sync_log ORDER BY sync_time DESC LIMIT 1').get();
        stats.byDepartment = this.db.prepare(
            `SELECT department, COUNT(*) as count, SUM(annual_budget) as budget 
             FROM directory_records WHERE department != '' GROUP BY department ORDER BY count DESC`
        ).all();
        stats.byStatus = this.db.prepare(
            `SELECT status, COUNT(*) as count FROM directory_records GROUP BY status`
        ).all();
        return stats;
    }

    close() {
        this.db.close();
    }
}

module.exports = DirectoryDB;
