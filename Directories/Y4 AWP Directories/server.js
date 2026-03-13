const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const DirectoryDB = require('./database');
const { parseExcel } = require('./excel-parser');
const { parseWorkbackSchedule } = require('./workback-parser');
const { parseActivityValidation } = require('./validation-parser');

const app = express();
const db = new DirectoryDB();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ─── Load Excel data on startup ──────────────────────────────
function loadExcelData() {
    try {
        const records = parseExcel();
        const count = db.bulkInsert(records);
        console.log(`[Data] Loaded ${count} activities from COSME Y4 Detailed Activities.xlsx`);
        return count;
    } catch (error) {
        console.error('[Data] Failed to load Excel:', error.message);
        return 0;
    }
}

loadExcelData();

// ─── API Routes ──────────────────────────────────────────────

// Dashboard stats
app.get('/api/stats', (req, res) => {
    try {
        res.json(db.getDashboardStats());
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get all activities (with optional filters)
app.get('/api/activities', (req, res) => {
    try {
        const filters = {
            search: req.query.search,
            thematic_area: req.query.thematic_area,
            sub_theme: req.query.sub_theme,
            strategy_code: req.query.strategy_code,
            status: req.query.status,
        };
        res.json(db.getAllActivities(filters));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get single activity
app.get('/api/activities/:id', (req, res) => {
    try {
        const record = db.getActivityById(parseInt(req.params.id, 10));
        if (!record) return res.status(404).json({ error: 'Activity not found' });
        res.json(record);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create new activity
app.post('/api/activities', (req, res) => {
    try {
        if (!req.body.activity_description || !req.body.thematic_area) {
            return res.status(400).json({ error: 'Activity description and thematic area are required' });
        }
        res.status(201).json(db.createActivity(req.body));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update activity
app.put('/api/activities/:id', (req, res) => {
    try {
        const updated = db.updateActivity(parseInt(req.params.id, 10), req.body);
        if (!updated) return res.status(404).json({ error: 'Activity not found' });
        res.json(updated);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Delete activity
app.delete('/api/activities/:id', (req, res) => {
    try {
        db.deleteActivity(parseInt(req.params.id, 10));
        res.json({ message: 'Activity deleted' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get filter options
app.get('/api/filters/:column', (req, res) => {
    try {
        res.json(db.getDistinctValues(req.params.column));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get update history
app.get('/api/activities/:id/history', (req, res) => {
    try {
        res.json(db.getUpdateHistory(parseInt(req.params.id, 10)));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Re-sync from Excel file
app.post('/api/reload', (req, res) => {
    try {
        const count = loadExcelData();
        res.json({ message: `Reloaded ${count} activities from Excel`, count });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ─── Workback Schedule API ───────────────────────────────────
app.get('/api/workback', (req, res) => {
    try {
        const schedule = parseWorkbackSchedule();
        res.json(schedule);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ─── Activity Validation API ─────────────────────────────────
app.get('/api/validation', (req, res) => {
    try {
        const outcomes = parseActivityValidation();
        res.json(outcomes);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Serve main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ─── Start server ────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`\n╔══════════════════════════════════════════════════════╗`);
    console.log(`║  COSME Y4 AWP Detailed Activities Directory          ║`);
    console.log(`║  Running at: http://localhost:${PORT}                    ║`);
    console.log(`╚══════════════════════════════════════════════════════╝\n`);
});

process.on('SIGINT', () => { db.close(); process.exit(0); });
