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
# Render automatically sets DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is missing — Add it in Render Dashboard!")

# Fix for SQLAlchemy + Render format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Prevent PostgreSQL timeouts
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 180,
}

# --------------------------
# SECURITY CONFIG
# --------------------------
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")

# Allow frontend to access backend
CORS(app)

# --------------------------
# EXTENSIONS INIT
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
    return "Emmanuel's Banking API is LIVE (Render Deployment Successful)"

# --------------------------
# LOCAL ONLY
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
