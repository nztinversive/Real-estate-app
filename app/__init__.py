from flask import Flask
from .extensions import db
import os

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    
    # Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize extensions
    db.init_app(app)

    # Import and register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Print the UPLOAD_FOLDER path for debugging
    print(f"UPLOAD_FOLDER set to: {app.config['UPLOAD_FOLDER']}")

    return app