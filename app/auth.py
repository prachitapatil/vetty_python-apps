from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
from .cred import username_1, password_1

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login to get JWT token.
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: admin
    responses:
      200:
        description: Successfully generated token
        schema:
          type: object
          properties:
            token:
              type: string
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == username_1 and password == password_1:
        token = jwt.encode({
            "user": username,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }, "your-jwt-secret", algorithm="HS256")

        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401

