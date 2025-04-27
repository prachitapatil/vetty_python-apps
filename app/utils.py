from functools import wraps
from flask import request, redirect, url_for
import jwt
from .config import SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        
        if not token:
            return redirect(url_for('main.login_page'))
        
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return f(*args, **kwargs)
        except jwt.InvalidTokenError:
            return redirect(url_for('main.login_page'))
            
    return decorated
