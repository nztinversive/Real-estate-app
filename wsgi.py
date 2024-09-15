from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    print("Current working directory:", os.getcwd())
    print("FLASK_APP:", os.environ.get('FLASK_APP'))
    print("App instance path:", app.instance_path)
    print("SQLAlchemy database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True)