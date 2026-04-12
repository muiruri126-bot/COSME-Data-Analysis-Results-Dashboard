"""COSME DIP Tracker — Flask Application Factory."""
import os
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv
from config import config
from extensions import db, jwt, mail, migrate, cors

load_dotenv()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    allowed_origins = [o.strip() for o in frontend_url.split(',') if o.strip()]
    cors.init_app(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # JWT blocklist check
    from routes.auth import is_token_revoked
    jwt.token_in_blocklist_loader(is_token_revoked)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization required'}), 401

    # Register blueprints
    from routes.auth import auth_bp
    from routes.framework import framework_bp
    from routes.tasks import tasks_bp
    from routes.gantt import gantt_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(framework_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(gantt_bp)
    app.register_blueprint(dashboard_bp)

    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'app': 'COSME DIP Tracker'}), 200

    # Serve React frontend in production
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'dist')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        # Don't serve frontend for API routes
        if path.startswith('api/') or path == 'health':
            return jsonify({'error': 'Not found'}), 404
        # Serve static assets if they exist
        full_path = os.path.join(frontend_dir, path)
        if path and os.path.isfile(full_path):
            return send_from_directory(frontend_dir, path)
        # Fallback to index.html for SPA routing
        index_path = os.path.join(frontend_dir, 'index.html')
        if os.path.isfile(index_path):
            return send_from_directory(frontend_dir, 'index.html')
        return jsonify({'message': 'COSME DIP Tracker API', 'version': '1.0.0'}), 200

    # Create upload dir
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # Error handlers
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app


app = create_app()


# CLI commands
@app.cli.command('seed')
def seed_command():
    """Seed the database with initial data."""
    from seed import seed_all
    seed_all()


@app.cli.command('init-db')
def init_db_command():
    """Create all tables and seed."""
    db.create_all()
    print("Tables created.")
    from seed import seed_all
    seed_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
