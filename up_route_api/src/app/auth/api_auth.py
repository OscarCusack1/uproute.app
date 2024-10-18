import sqlite3
import os
import binascii
from functools import wraps
from flask import request, jsonify
from sqlalchemy import text

from ..extensions import db

def generate_api_key():
    return binascii.hexlify(os.urandom(24)).decode()

def create_api_key(email: str):
    api_key = generate_api_key()
    print(f'GENERATED API: {api_key}')
    try:
        with db.engine.connect() as connection:
            print("CONNECTED")
            result = connection.execute(text("SELECT * FROM accounts_customuser WHERE email = :email"), {"email": email})
            user = result.fetchone()
            if user is not None:
                print(user)
                result = connection.execute(text("UPDATE accounts_customuser SET api_key = :api_key WHERE email = :email"), {"api_key": api_key, "email": email})
                connection.commit()
                return {"message": f"New API key generated for user: {email}" ,"api_key": api_key}, 200
            else:
                print(f"USER {email} DOES NOT EXIST")
                return {"message": "User not found"}, 404
    except Exception as e:
        return {"message": str(e)}, 500

def require_api_key(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if 'x-api-key' not in request.headers:
            return jsonify({"message": "API key is missing"}), 401
        api_key = request.headers['x-api-key']
        print(api_key)
        try:
            with db.engine.connect() as connection:
            
                result = connection.execute(text("SELECT * FROM accounts_customuser WHERE api_key = :api_key"), {"api_key": api_key})
                user = result.fetchone()
                if user is None:
                    return jsonify({"message": "Invalid API key"}), 403
                print(user)
                return await f(*args, **kwargs)
        except Exception as e:
            return jsonify({"message": str(e)}), 500

        # conn = sqlite3.connect('database.db')
        # cursor = conn.cursor()
        # cursor.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
        # user = cursor.fetchone()
        # conn.close()
        # if user is None:
        #     return jsonify({"message": "Invalid API key"}), 403
        # return await f(*args, **kwargs)
    return decorated_function