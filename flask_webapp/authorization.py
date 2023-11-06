from functools import wraps
from flask import g, redirect, url_for, session

def login_required(allowed_roles=None):
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            if allowed_roles is None:
                # No specific roles required, allow access
                return func(*args, **kwargs)
            
            user_role = session.get('user_role')
            if user_role in allowed_roles:
                # User has an allowed role, allow access
                return func(*args, **kwargs)
            else:
                return redirect(url_for('unauthorized'))
        return wrapped_function
    return decorator


