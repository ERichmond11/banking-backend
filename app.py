from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models.user import db, bcrypt
from models.transaction import Transaction

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Render provides DATABASE_URL automatically
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")

# Prevent PostgreSQL SSL errors on Render
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

CORS(app)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Import blueprints after creating app
from routes.auth_routes import auth_blueprint
from routes.account_routes import account_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(account_blueprint)


@app.route('/')
def home():
    return "Emmanuel's Banking API is live!"


if __name__ == '__main__':
    app.run(debug=True)
