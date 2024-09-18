from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///real_estate.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads')
    )
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)
    migrate.init_app(app, db)

    # Serve favicon
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    with app.app_context():
        from .routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

        from .syndication import syndication as syndication_blueprint
        app.register_blueprint(syndication_blueprint, url_prefix='/syndication')
        
        # Create database tables
        db.create_all()
        
        # Ensure sample data is populated
        from .routes import populate_sample_data
        populate_sample_data()

    return app