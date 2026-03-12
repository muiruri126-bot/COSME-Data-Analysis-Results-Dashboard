const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const DirectoryDB = require('./database');
const SharePointService = require('./sharepoint-service');

const app = express();
const db = new DirectoryDB();
const sharepoint = new SharePointService();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ─── API Routes ──────────────────────────────────────────────

// Get dashboard stats
app.get('/api/stats', (req, res) => {
    try {
        const stats = db.getDashboardStats();
        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get all records with optional filters
app.get('/api/records', (req, res) => {
    try {
        const filters = {
            search: req.query.search,
            department: req.query.department,
            status: req.query.status,
            duty_station: req.query.duty_station,
        };
        const records = db.getAllRecords(filters);
        res.json(records);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get a single record
app.get('/api/records/:id', (req, res) => {
    try {
        const record = db.getRecordById(parseInt(req.params.id, 10));
        if (!record) return res.status(404).json({ error: 'Record not found' });
        res.json(record);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create a new record
app.post('/api/records', (req, res) => {
    try {
        if (!req.body.staff_name) {
            return res.status(400).json({ error: 'Staff name is required' });
        }
        const record = db.createRecord(req.body);
        res.status(201).json(record);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update a record
app.put('/api/records/:id', (req, res) => {
    try {
        const updated = db.updateRecord(parseInt(req.params.id, 10), req.body);
        if (!updated) return res.status(404).json({ error: 'Record not found' });
        res.json(updated);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Delete a record
app.delete('/api/records/:id', (req, res) => {
    try {
        db.deleteRecord(parseInt(req.params.id, 10));
        res.json({ message: 'Record deleted' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get distinct filter values
app.get('/api/filters/:column', (req, res) => {
    try {
        const values = db.getDistinctValues(req.params.column);
        res.json(values);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get update history for a record
app.get('/api/records/:id/history', (req, res) => {
    try {
        const history = db.getUpdateHistory(parseInt(req.params.id, 10));
        res.json(history);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get sync logs
app.get('/api/sync/log', (req, res) => {
    try {
        const logs = db.getSyncLog();
        res.json(logs);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Trigger manual SharePoint sync
app.post('/api/sync', async (req, res) => {
    try {
        console.log('[Sync] Manual sync triggered...');
        const data = await sharepoint.fetchExcelData();
        let totalSynced = 0;

        for (const [sheetName, rows] of Object.entries(data)) {
            console.log(`[Sync] Processing sheet: ${sheetName} (${rows.length} rows)`);
            const count = db.bulkUpsertFromSharePoint(rows);
            totalSynced += count;
        }

        res.json({ message: `Synced ${totalSynced} records from SharePoint`, count: totalSynced });
    } catch (error) {
        console.error('[Sync] Error:', error.message);
        res.status(500).json({
            error: 'SharePoint sync failed',
            details: error.message,
            hint: 'Ensure Azure AD credentials are configured in .env file'
        });
    }
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ─── Auto-sync scheduler ────────────────────────────────────
const syncInterval = (parseInt(process.env.SYNC_INTERVAL_MINUTES, 10) || 5) * 60 * 1000;

async function autoSync() {
    try {
        console.log('[AutoSync] Starting scheduled sync...');
        const data = await sharepoint.fetchExcelData();
        let totalSynced = 0;
        for (const [sheetName, rows] of Object.entries(data)) {
            totalSynced += db.bulkUpsertFromSharePoint(rows);
        }
        console.log(`[AutoSync] Completed: ${totalSynced} records synced`);
    } catch (error) {
        console.log('[AutoSync] Skipped - SharePoint not configured or unreachable');
    }
}

// Start auto-sync after initial delay
setTimeout(() => {
    autoSync();
    setInterval(autoSync, syncInterval);
}, 10000);

// ─── Start server ────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`\n╔══════════════════════════════════════════════╗`);
    console.log(`║  Y4 AWP Directory Dashboard                  ║`);
    console.log(`║  Running at: http://localhost:${PORT}            ║`);
    console.log(`║  Auto-sync every ${process.env.SYNC_INTERVAL_MINUTES || 5} minutes               ║`);
    console.log(`╚══════════════════════════════════════════════╝\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    db.close();
    process.exit(0);
});
