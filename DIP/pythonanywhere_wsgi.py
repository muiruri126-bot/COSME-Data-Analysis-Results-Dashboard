"""
PythonAnywhere WSGI Configuration for COSME DIP Tracker.

Copy the contents of this file into your PythonAnywhere WSGI configuration file
(found at /var/www/cosme_pythonanywhere_com_wsgi.py).
"""
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/cosme/DIP/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'cosme-dip-prod-secret-2026-xK9mP3qR'
os.environ['JWT_SECRET_KEY'] = 'cosme-jwt-prod-secret-2026-vN7wL2yT'

# Import the Flask app
from app import create_app

application = create_app('production')
