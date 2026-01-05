from functools import wraps
from flask import abort
from flask_login import current_user
from app.models import UserRole

def role_required(roles):
    """
    Decorator to restrict access to users with specific roles.
    :param roles: Single role or list of roles.
    """
    if not isinstance(roles, list):
        roles = [roles]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            
            if current_user.role not in roles:
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permission_name):
    """
    Decorator to restrict access based on dynamic permissions.
    :param permission_name: Name of the permission to check.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            
            if not current_user.has_permission(permission_name):
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

