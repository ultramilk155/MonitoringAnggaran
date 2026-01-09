from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

def create_default_users():
    # Create Admin
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        
    # Create Viewer
    if not User.query.filter_by(username='viewer').first():
        viewer = User(username='viewer', password_hash=generate_password_hash('viewer123'), role='viewer')
        db.session.add(viewer)
        
    if not User.query.filter_by(username='superadmin').first():
        superadmin = User(username='superadmin', password_hash=generate_password_hash('super123'), role='super_admin')
        db.session.add(superadmin)
        
    db.session.commit()
if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist (for fresh install)
        # Note: In production with migrations, use 'flask db upgrade' instead of db.create_all()
        db.create_all()
        create_default_users()
    app.run(debug=True, port=9010)
