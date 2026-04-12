"""RBAC decorators and helpers for route protection."""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User


def get_current_user():
    """Get the current authenticated user from JWT."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def require_roles(*allowed_roles):
    """Decorator: require the user to have at least one of the specified roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            user_roles = {r.name for r in user.roles}
            if not user_roles.intersection(set(allowed_roles)):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(resource, action):
    """Decorator: require the user to have a specific permission."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            if not user.has_permission(resource, action):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def log_audit(user_id, entity_type, entity_id, action, changes=None):
    """Create an audit log entry."""
    from models import AuditLog, db
    log = AuditLog(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changes=changes,
        ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.flush()


def create_notification(user_id, notif_type, title, body=None, ref_type=None, ref_id=None):
    """Create an in-app notification."""
    from models import Notification, db
    n = Notification(
        user_id=user_id,
        type=notif_type,
        title=title,
        body=body,
        reference_type=ref_type,
        reference_id=ref_id,
    )
    db.session.add(n)
    db.session.flush()
    return n
