"""Authentication routes: login, register, forgot/reset password, refresh, logout, me."""
import secrets
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from models import User, Role, db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# In-memory blocklist for revoked tokens (use Redis in production)
BLOCKLIST = set()


@auth_bp.post('/login')
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
    }), 200


@auth_bp.post('/register')
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    phone = (data.get('phone') or '').strip() or None

    if not full_name or not email or not password:
        return jsonify({'error': 'Full name, email, and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    user = User(
        email=email,
        full_name=full_name,
        phone=phone,
    )
    user.set_password(password)

    # Assign default Viewer role
    viewer_role = Role.query.filter_by(name='Viewer').first()
    if viewer_role:
        user.roles.append(viewer_role)

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
        'message': 'Account created successfully',
    }), 201


@auth_bp.post('/forgot-password')
def forgot_password():
    data = request.get_json()
    email = (data.get('email') or '').strip().lower() if data else ''
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Always return success to prevent email enumeration
    user = User.query.filter_by(email=email).first()
    if user and user.is_active:
        token = secrets.token_urlsafe(48)
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()

        # In production, send email with reset link here.
        # For dev, log the token for manual use.
        from flask import current_app
        current_app.logger.info(f'Password reset token for {email}: {token}')

    return jsonify({
        'message': 'If an account with that email exists, a password reset link has been sent.',
    }), 200


@auth_bp.post('/reset-password')
def reset_password():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    token = (data.get('token') or '').strip()
    new_password = data.get('password') or ''

    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({'error': 'Invalid or expired reset token'}), 400

    if user.reset_token_expires and user.reset_token_expires < datetime.now(timezone.utc):
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        return jsonify({'error': 'Reset token has expired. Please request a new one.'}), 400

    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.session.commit()

    return jsonify({'message': 'Password has been reset successfully. You can now log in.'}), 200


@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401

    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200


@auth_bp.post('/logout')
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    BLOCKLIST.add(jti)
    return jsonify({'message': 'Logged out'}), 200


@auth_bp.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200


def is_token_revoked(jwt_header, jwt_payload):
    """Check if token is in blocklist."""
    return jwt_payload.get('jti') in BLOCKLIST
