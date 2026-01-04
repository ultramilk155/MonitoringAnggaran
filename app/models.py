from app.extensions import db
from flask_login import UserMixin
import datetime

class BudgetLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(50), nullable=False)
    no_prk = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.String(255), nullable=False)
    tahun = db.Column(db.Integer, nullable=False, default=2026)
    
    # Pagu
    pagu_material = db.Column(db.Float, default=0)
    pagu_jasa = db.Column(db.Float, default=0)
    pagu_total = db.Column(db.Float, default=0)
    
    # Realisasi
    usulan_rab_rp = db.Column(db.Float, default=0)
    terkontrak_rp = db.Column(db.Float, default=0)
    terbayar_rp = db.Column(db.Float, default=0)
    ellipse_rp = db.Column(db.Float, default=0)
    order_index = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'kode': self.kode,
            'no_prk': self.no_prk,
            'deskripsi': self.deskripsi,
            'pagu_material': self.pagu_material,
            'pagu_jasa': self.pagu_jasa,
            'pagu_total': self.pagu_total,
            'usulan_rab_rp': self.usulan_rab_rp,
            'terkontrak_rp': self.terkontrak_rp,
            'terbayar_rp': self.terbayar_rp,
            'ellipse_rp': self.ellipse_rp,
            'jobs': [job.to_dict() for job in self.jobs]
        }

class JobDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget_line_id = db.Column(db.Integer, db.ForeignKey('budget_line.id'), nullable=False)
    
    nama_pekerjaan = db.Column(db.String(255), nullable=False)
    tanggal_tor = db.Column(db.String(50))
    tanggal_dibutuhkan = db.Column(db.String(50))
    no_vka = db.Column(db.String(100))
    coa = db.Column(db.String(100))
    
    rab_sebelum_ppn = db.Column(db.Float, default=0)
    est_sisa = db.Column(db.Float, default=0)
    terkontrak_rp = db.Column(db.Float, default=0)
    terbayar_rp = db.Column(db.Float, default=0)
    jenis_pengadaan = db.Column(db.String(50))
    status = db.Column(db.String(20), default='User') # User, Rendan, Lakdan
    pic = db.Column(db.String(50))
    
    # Relationship with BudgetLine
    budget_line = db.relationship('BudgetLine', backref=db.backref('jobs', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'budget_line_id': self.budget_line_id,
            'nama_pekerjaan': self.nama_pekerjaan,
            'tanggal_tor': self.tanggal_tor,
            'tanggal_dibutuhkan': self.tanggal_dibutuhkan,
            'no_vka': self.no_vka,
            'coa': self.coa,
            'rab_sebelum_ppn': self.rab_sebelum_ppn,
            'est_sisa': self.est_sisa,
            'terkontrak_rp': self.terkontrak_rp,
            'terbayar_rp': self.terbayar_rp,
            'jenis_pengadaan': self.jenis_pengadaan,
            'status': self.status,
            'pic': self.pic,
            'progress_logs': [log.to_dict() for log in self.progress_logs]
        }

class JobProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_detail.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    notes = db.Column(db.Text, nullable=False)
    progress_percent = db.Column(db.Integer, default=0)
    
    # Relationships
    job = db.relationship('JobDetail', backref=db.backref('progress_logs', lazy=True, order_by="desc(JobProgress.created_at)"))
    user = db.relationship('User', backref='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'user_name': self.user.username if self.user else 'Unknown',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'notes': self.notes,
            'progress_percent': self.progress_percent
        }

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer') # 'admin' or 'viewer'
