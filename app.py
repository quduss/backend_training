from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
from sqlalchemy.sql import func
from marshmallow import Schema, fields, ValidationError


load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at
        }

class UserSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(required=True)

# Global error handler for IntegrityError
@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    response = {"error": "User with this email already exists"}
    return jsonify(response), 400

# Global error handler for 404 errors
@app.errorhandler(404)
def resource_not_found(error):
    response = {"error": "Resource not found"}
    return jsonify(response), 404

# Global error handler for 500 errors
@app.errorhandler(500)
def internal_server_error(error):
    response = {"error": "An unexpected error occurred"}
    return jsonify(response), 500

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # Validate input
    schema = UserSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    #if not data or not data.get("username") or not data.get("email"):
        #return jsonify({"error": "Username and email are required"}), 400

    new_user = User(username=validated_data['username'], email=validated_data['email'])
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        # Log unexpected exceptions and raise them for the 500 handler
        app.logger.error(f"Unexpected error: {str(e)}")
        raise e

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        data = request.get_json()
        user.email = data.get('email', user.email)
        db.session.commit()
        return jsonify(user.to_dict()), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"error": "User not found"}), 404

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
