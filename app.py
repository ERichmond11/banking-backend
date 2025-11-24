from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models.user import db, bcrypt
from models.transaction import Transaction
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# --------------------------
# DATABASE CONFIG
# --------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is missing — Add it in Render Dashboard!")

# Render PostgreSQL fix: Convert postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Prevent idle connections from crashing on Render
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# --------------------------
# SECURITY CONFIG
# --------------------------

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")

# Allow frontend to connect
CORS(app)

# --------------------------
# INIT EXTENSIONS
# --------------------------

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# --------------------------
# BLUEPRINTS
# --------------------------

from routes.auth_routes import auth_blueprint
from routes.account_routes import account_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(account_blueprint)

# --------------------------
# ROOT ENDPOINT
# --------------------------

@app.route("/")
def home():
    return "Emmanuel's Banking API is LIVE 🚀"

# --------------------------
# LOCAL DEVELOPMENT
# --------------------------

# --------------------------
# TEMPORARY: Initialize DB tables ONCE
# --------------------------
@app.route('/init-db')
def init_db():
    with app.app_context():
        db.create_all()
    return "Database tables created successfully!"


if __name__ == "__main__":
    # Allows running locally using local MySQL if you want
    print("Running in LOCAL mode — using Render DB unless overridden...")
    app.run(debug=True, port=5000)
