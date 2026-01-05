import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey-dev-fallback'
    
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Ensure instance folder exists
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    # Database URL handling
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('mysql://'):
        database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
        
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///' + os.path.join(INSTANCE_PATH, 'budget.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

