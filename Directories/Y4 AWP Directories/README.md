# Y4 AWP Directory Dashboard

A web-based directory management system for the **COSME Annual Work Plan (AWP)**, with real-time synchronization from SharePoint Online.

## Features

- **Dashboard** – Overview cards showing total records, budget, expenditure, departments
- **Directory Table** – Searchable and filterable data table with all AWP records
- **Add/Edit Form** – Full CRUD form with staff details, activity info, budget tracking
- **SharePoint Sync** – Pull data from your SharePoint Excel file via Microsoft Graph API
- **Update History** – Track every field change with timestamps
- **CSV Export** – Download filtered data as CSV
- **Auto-sync** – Configurable automatic sync interval

## Quick Start

```bash
npm install
npm start
```

Open **http://localhost:3000** in your browser.

## SharePoint Integration Setup

To enable real-time sync from your SharePoint Excel file:

### 1. Register an Azure AD App

1. Go to [Azure Portal](https://portal.azure.com) → **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Name: `Y4 AWP Directory Sync`
4. Supported account types: **Single tenant**
5. Click **Register**

### 2. Configure API Permissions

1. Go to **API permissions** → **Add a permission**
2. Select **Microsoft Graph** → **Application permissions**
3. Add: `Sites.Read.All`, `Files.Read.All`
4. Click **Grant admin consent**

### 3. Create Client Secret

1. Go to **Certificates & secrets** → **New client secret**
2. Copy the secret value immediately

### 4. Update .env File

```env
AZURE_CLIENT_ID=your-app-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### 5. Restart the Server

```bash
npm start
```

Click **"Sync Now"** in the dashboard to pull data from SharePoint.

## Project Structure

```
├── server.js              # Express API server
├── database.js            # SQLite database layer
├── sharepoint-service.js  # Microsoft Graph API integration
├── .env                   # Configuration (Azure AD credentials)
├── public/
│   ├── index.html         # Dashboard UI
│   ├── styles.css         # Styling
│   └── app.js             # Frontend JavaScript
└── package.json
```

## API Endpoints

| Method | Endpoint                    | Description              |
|--------|-----------------------------|--------------------------|
| GET    | `/api/stats`                | Dashboard statistics     |
| GET    | `/api/records`              | List all records         |
| GET    | `/api/records/:id`          | Get single record        |
| POST   | `/api/records`              | Create new record        |
| PUT    | `/api/records/:id`          | Update record            |
| DELETE | `/api/records/:id`          | Delete record            |
| GET    | `/api/records/:id/history`  | Update history           |
| GET    | `/api/filters/:column`      | Distinct filter values   |
| POST   | `/api/sync`                 | Trigger SharePoint sync  |
| GET    | `/api/sync/log`             | Sync history log         |
