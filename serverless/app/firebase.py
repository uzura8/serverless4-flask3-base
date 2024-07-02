import os
from functools import wraps
from flask import request
import firebase_admin
from firebase_admin import credentials, auth
import traceback

firebase_admin.initialize_app()


def check_user_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'}, 400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
            request.user = user
        except Exception as e:
            print(traceback.format_exc())
            return {'message': 'Invalid token provided.'}, 401
        return f(*args, **kwargs)
    return wrap
