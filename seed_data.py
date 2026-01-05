from app import create_app
from app.models import db, BudgetLine, User, UserRole, Permission, RolePermission
from werkzeug.security import generate_password_hash

app = create_app()

# Default permissions to seed
DEFAULT_PERMISSIONS = [
    # User Management
    {'name': 'manage_users', 'description': 'Create, edit, delete users', 'category': 'users'},
    
    # Budget Management
    {'name': 'upload_prk', 'description': 'Upload PRK Excel files', 'category': 'budget'},
    {'name': 'delete_budget_line', 'description': 'Delete budget lines', 'category': 'budget'},
    {'name': 'reorder_budget_lines', 'description': 'Reorder budget lines', 'category': 'budget'},
    
    # Job Management
    {'name': 'add_job', 'description': 'Add new jobs', 'category': 'jobs'},
    {'name': 'edit_job', 'description': 'Edit existing jobs', 'category': 'jobs'},
    {'name': 'delete_job', 'description': 'Delete jobs', 'category': 'jobs'},
    {'name': 'add_progress', 'description': 'Add progress logs', 'category': 'jobs'},
    {'name': 'edit_progress', 'description': 'Edit progress logs', 'category': 'jobs'},
    {'name': 'update_job_status', 'description': 'Update job status', 'category': 'jobs'},
    
    # Reports
    {'name': 'export_data', 'description': 'Export data to Excel', 'category': 'reports'},
    {'name': 'view_monitoring', 'description': 'View monitoring dashboard', 'category': 'reports'},
]

# Default role permissions (what each role can do)
DEFAULT_ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        'add_job', 'edit_job', 'delete_job', 
        'add_progress', 'edit_progress', 'update_job_status',
        'reorder_budget_lines', 'export_data', 'view_monitoring'
    ],
    UserRole.VIEWER: [
        'view_monitoring', 'export_data'
    ]
}

def seed():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # 1. Create Users
        print("Seeding Users...")
        if not User.query.first():
            users = [
                User(username='superadmin', password_hash=generate_password_hash('password123'), role=UserRole.SUPER_ADMIN),
                User(username='admin', password_hash=generate_password_hash('password123'), role=UserRole.ADMIN),
                User(username='viewer', password_hash=generate_password_hash('password123'), role=UserRole.VIEWER)
            ]
            db.session.add_all(users)
            db.session.commit()
            print("Users created: superadmin, admin, viewer (password: password123)")
        else:
            print("Users already exist.")
        
        # 2. Create Permissions
        print("Seeding Permissions...")
        if not Permission.query.first():
            for perm_data in DEFAULT_PERMISSIONS:
                perm = Permission(**perm_data)
                db.session.add(perm)
            db.session.commit()
            print(f"Created {len(DEFAULT_PERMISSIONS)} permissions.")
            
            # Create RolePermissions
            for role, allowed_perms in DEFAULT_ROLE_PERMISSIONS.items():
                for perm_name in allowed_perms:
                    perm = Permission.query.filter_by(name=perm_name).first()
                    if perm:
                        rp = RolePermission(role=role, permission_id=perm.id, is_allowed=True)
                        db.session.add(rp)
            db.session.commit()
            print("Role permissions configured.")
        else:
            print("Permissions already exist.")

        # 3. Create Budget Lines
        print("Seeding Budget Lines...")
        if BudgetLine.query.first():
            print("Budget data already seeded.")
            return

        data = [
            # Kode 10
            {"kode": "10", "no_prk": "PL262G0101", "deskripsi": "Pengelolaan Operasi Pembangkit PLTD Panangkalaan dan PLTD Barabai", "pagu_material": 0, "pagu_jasa": 3706770000, "pagu_total": 3706770000},
            {"kode": "10", "no_prk": "PL262G0102", "deskripsi": "Operasi dan Pemeliharaan Pembangkit UP Kalselteng", "pagu_material": 0, "pagu_jasa": 46785923000, "pagu_total": 46785923000},
            {"kode": "10", "no_prk": "PL262G0103", "deskripsi": "Reimbursement Jasa O&M UP Kalselteng", "pagu_material": 2896746000, "pagu_jasa": 0, "pagu_total": 2896746000},
            {"kode": "10", "no_prk": "PL262G0104", "deskripsi": "Pengujian Heat Rate dan Sertifikasi Pembangkit (SLO)", "pagu_material": 0, "pagu_jasa": 1294050000, "pagu_total": 1294050000},
            
            # Kode 18
            {"kode": "18", "no_prk": "PL262I0101", "deskripsi": "Sarana Penunjang Kegiatan K3", "pagu_material": 1373580000, "pagu_jasa": 499184000, "pagu_total": 1872764000},
            {"kode": "18", "no_prk": "PL262I0102", "deskripsi": "Peralatan dan Revitalisasi Kesiapan FPS PLTMG/D", "pagu_material": 623623000, "pagu_jasa": 753768000, "pagu_total": 1377391000},
            {"kode": "18", "no_prk": "PL262I0103", "deskripsi": "MOU Polda Kalteng", "pagu_material": 0, "pagu_jasa": 362148000, "pagu_total": 362148000},
            {"kode": "18", "no_prk": "PL262I0104", "deskripsi": "Sarana Prasarana Keamanan", "pagu_material": 256131000, "pagu_jasa": 218003000, "pagu_total": 474134000},
            {"kode": "18", "no_prk": "PL262I0201", "deskripsi": "Sertifikasi Peralatan dan Personil", "pagu_material": 0, "pagu_jasa": 607656000, "pagu_total": 607656000},

            # Kode 19
            {"kode": "19", "no_prk": "PL262J0101", "deskripsi": "Pemantauan dan Pengelolaan Lingkungan Hidup UP Kalselteng", "pagu_material": 0, "pagu_jasa": 1776267000, "pagu_total": 1776267000},
            {"kode": "19", "no_prk": "PL262J0102", "deskripsi": "Pengelolaan Limbah B3 Pembangkit UP Kalselteng", "pagu_material": 0, "pagu_jasa": 849594000, "pagu_total": 849594000},
            {"kode": "19", "no_prk": "PL262J0201", "deskripsi": "Pemenuhan PROPER 2025", "pagu_material": 0, "pagu_jasa": 404923000, "pagu_total": 404923000},

            # Kode 20, 22, 21
            {"kode": "20", "no_prk": "PL262K0101", "deskripsi": "Spare Part Material dan Consumable Kegiatan PM", "pagu_material": 13284203000, "pagu_jasa": 0, "pagu_total": 13284203000},
            {"kode": "22", "no_prk": "PL262M0102", "deskripsi": "Pemeliharaan Korektif Pembangkit", "pagu_material": 5742908000, "pagu_jasa": 0, "pagu_total": 5742908000},
            {"kode": "21", "no_prk": "PL262L0301", "deskripsi": "Pekerjaan Predictive Maintenance", "pagu_material": 1529639000, "pagu_jasa": 0, "pagu_total": 1529639000},
            
            # Kode 60
            {"kode": "60", "no_prk": "PL262P0101", "deskripsi": "Penerapan Totem di Kantor UP Kalselteng", "pagu_material": 0, "pagu_jasa": 50000000, "pagu_total": 50000000},
            {"kode": "60", "no_prk": "PL262P0102", "deskripsi": "Pengadaan dan Pemeliharaan Support Equipment (Faskung)", "pagu_material": 0, "pagu_jasa": 244438000, "pagu_total": 244438000},
            {"kode": "60", "no_prk": "PL262P0103", "deskripsi": "Pemeliharaan Fasilitas Kerja UP Kalselteng", "pagu_material": 143890000, "pagu_jasa": 118344000, "pagu_total": 262234000},
            {"kode": "60", "no_prk": "PL262P0201", "deskripsi": "Pemeliharaan sarana Gedung UP dan UL", "pagu_material": 78928000, "pagu_jasa": 618750000, "pagu_total": 697678000},
            {"kode": "60", "no_prk": "PL262P0601", "deskripsi": "Akomodasi Siaga Pembangkit", "pagu_material": 0, "pagu_jasa": 70074000, "pagu_total": 70074000},
            {"kode": "60", "no_prk": "PL262P0602", "deskripsi": "Alih Daya Pemeliharaan Gedung UP Kalselteng", "pagu_material": 0, "pagu_jasa": 1073667000, "pagu_total": 1073667000},
            {"kode": "60", "no_prk": "PL262P0603", "deskripsi": "Alih Daya Pemeliharaan Gedung UP PLTD", "pagu_material": 0, "pagu_jasa": 1941842000, "pagu_total": 1941842000},
            {"kode": "60", "no_prk": "PL262P0604", "deskripsi": "Jasa Pengelolaan Kendaraan dan Pengemudi UP Kalselteng", "pagu_material": 0, "pagu_jasa": 917962000, "pagu_total": 917962000},
            {"kode": "60", "no_prk": "PL262P0605", "deskripsi": "Kegiatan pendukung Business Support", "pagu_material": 0, "pagu_jasa": 262384000, "pagu_total": 262384000},
            {"kode": "60", "no_prk": "PL262P0606", "deskripsi": "Pengembangan Manajemen", "pagu_material": 0, "pagu_jasa": 500000000, "pagu_total": 500000000},
        ]
        
        for item in data:
            db.session.add(BudgetLine(**item))
        
        db.session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    seed()

