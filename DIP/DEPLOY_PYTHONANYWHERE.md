# COSME DIP Tracker — PythonAnywhere Deployment Guide

## Prerequisites
- A PythonAnywhere account (free or paid) at https://www.pythonanywhere.com
- Your project code (this repository)

---

## Step-by-Step Deployment

### 1. Upload Your Project

**Option A — Git (recommended):**
Open a **Bash console** on PythonAnywhere and run:
```bash
cd ~
git clone https://github.com/muiruri126-bot/COSME-Data-Analysis-Results-Dashboard.git DIP
```

**Option B — ZIP upload:**
1. Zip the entire `DIP` folder on your local machine.
2. Go to PythonAnywhere **Files** tab → upload the ZIP.
3. Open a Bash console and run:
   ```bash
   cd ~
   unzip DIP.zip -d DIP
   ```

### 2. Create a Virtual Environment

In the Bash console:
```bash
cd ~/DIP
mkvirtualenv --python=/usr/bin/python3.10 dipenv
workon dipenv
pip install -r backend/requirements.txt
```

> **Note:** If `psycopg2-binary` fails (not needed for SQLite), ignore it or remove it from requirements.txt.

### 3. Initialize the Database

```bash
cd ~/DIP/backend
python -c "
from app import create_app
from extensions import db
app = create_app('production')
with app.app_context():
    db.create_all()
    from seed import seed_all
    seed_all()
print('Database initialized and seeded!')
"
```

### 4. Configure the Web App

1. Go to the **Web** tab on PythonAnywhere.
2. Click **Add a new web app**.
3. Choose **Manual configuration** (not Flask — we'll set it up manually).
4. Select **Python 3.10**.

### 5. Set the WSGI File

1. On the **Web** tab, click the link to the WSGI configuration file  
   (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`).
2. **Delete all existing content** and replace with:

```python
import sys
import os

project_home = '/home/yourusername/DIP/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-random-secret-key-here'
os.environ['JWT_SECRET_KEY'] = 'your-jwt-secret-key-here'

from app import create_app
application = create_app('production')
```

> Replace `yourusername` with your actual PythonAnywhere username.  
> Replace the secret keys with strong random strings.

### 6. Set the Virtual Environment

On the **Web** tab, in the **Virtualenv** section, enter:
```
/home/yourusername/.virtualenvs/dipenv
```

### 7. Set the Source Code Directory

On the **Web** tab, set **Source code** to:
```
/home/yourusername/DIP/backend
```

### 8. Set the Working Directory

Set **Working directory** to:
```
/home/yourusername/DIP/backend
```

### 9. Static Files (Optional — for better performance)

On the **Web** tab, in the **Static files** section, add:

| URL          | Directory                               |
|--------------|-----------------------------------------|
| `/assets`    | `/home/yourusername/DIP/frontend/dist/assets` |

> This lets PythonAnywhere serve CSS/JS directly without going through Flask.

### 10. Reload the Web App

Click the green **Reload** button on the Web tab.

### 11. Visit Your Live Site!

Your app is now live at:
```
https://yourusername.pythonanywhere.com
```

---

## Default Admin Login

| Field    | Value                |
|----------|----------------------|
| Email    | admin@cosme-dip.org  |
| Password | Admin@2026!          |

---

## Updating the App

When you make changes:

```bash
# In PythonAnywhere Bash console
cd ~/DIP
git pull origin main

# Rebuild frontend (if frontend changed)
# NOTE: Free PythonAnywhere accounts may not have npm.
# Build locally, commit dist/, then pull.

# If backend changed:
workon dipenv
pip install -r backend/requirements.txt

# Then reload the web app from the Web tab
```

### Building Frontend Locally for Deployment

Since PythonAnywhere free tier may not have Node.js:

1. On your local machine:
   ```bash
   cd frontend
   npm run build
   ```
2. Commit the `frontend/dist/` folder to Git.
3. Push to GitHub, then pull on PythonAnywhere.

---

## Troubleshooting

- **500 errors**: Check the **Error log** on PythonAnywhere Web tab.
- **Module not found**: Ensure virtualenv is set correctly and dependencies installed.
- **Database issues**: Re-run the database initialization script from Step 3.
- **Static files not loading**: Verify the static file mapping in Step 9.
