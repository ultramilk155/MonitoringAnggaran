from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from models import db, BudgetLine, JobDetail, User, JobProgress
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.secret_key = 'supersecretkey' # Change this in production

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.template_filter('ribuan')
def format_ribuan(value):
    if value is None:
        return "0"
    return "{:,.0f}".format(value).replace(',', '.')

@app.route('/')
@login_required
def index():
    # Year Filter Logic
    current_year = datetime.datetime.now().year
    selected_year = session.get('year', current_year)
    
    kode_filter = request.args.get('kode')
    
    query = BudgetLine.query.filter_by(tahun=selected_year).order_by(BudgetLine.order_index.asc())
    
    if kode_filter:
        query = query.filter_by(kode=kode_filter)
        
    items = query.all()
    
    # Get Unique Codes for the selected year
    unique_codes = sorted({item.kode for item in BudgetLine.query.filter_by(tahun=selected_year).with_entities(BudgetLine.kode).distinct()})
    
    # Data for Chart
    chart_labels = []
    chart_pagu = []
    chart_pagu = []
    chart_ellipse = []
    chart_sisa = []
    chart_percent = []
    
    for code in unique_codes:
        # Filter out Test/System codes
        if 'TEST' in code.upper():
            continue
            
        code_items = BudgetLine.query.filter_by(kode=code, tahun=selected_year).all()
        total_pagu = sum(i.pagu_total for i in code_items)
        total_ellipse = sum(i.ellipse_rp for i in code_items)
        
        if total_pagu > 0:
            percent = (total_ellipse / total_pagu) * 100
        else:
            percent = 0
            
        sisa = total_pagu - total_ellipse
            
        chart_labels.append(f"Kode {code}")
        chart_pagu.append(total_pagu)
        chart_ellipse.append(total_ellipse)
        chart_sisa.append(sisa)
        chart_percent.append(round(percent, 2))

    total_pagu_material = sum(item.pagu_material for item in items)
    total_pagu_jasa = sum(item.pagu_jasa for item in items)
    total_pagu_total = sum(item.pagu_total for item in items)
    total_all_ellipse = sum(item.ellipse_rp for item in items)
    
    return render_template('index.html', 
                           items=items, 
                           unique_codes=unique_codes, 
                           kode_filter=kode_filter,
                           total_pagu_material=total_pagu_material,
                           total_pagu_jasa=total_pagu_jasa,
                           total_pagu_total=total_pagu_total,
                           chart_labels=chart_labels,
                           chart_pagu=chart_pagu,
                           chart_ellipse=chart_ellipse,
                           chart_sisa=chart_sisa,
                           chart_percent=chart_percent,
                           total_all_ellipse=total_all_ellipse,
                           selected_year=selected_year)

@app.route('/set_year/<int:year>')
def set_year(year):
    session['year'] = year
    return redirect(request.referrer or url_for('index'))

@app.route('/detail/<kode>')
def detail(kode):
    items = BudgetLine.query.filter_by(kode=kode).all()
    
    total_pagu_material = sum(item.pagu_material for item in items)
    total_pagu_jasa = sum(item.pagu_jasa for item in items)
    total_pagu_total = sum(item.pagu_total for item in items)
    
    return render_template('detail.html', 
                           items=items, 
                           kode=kode,
                           total_pagu_material=total_pagu_material,
                           total_pagu_jasa=total_pagu_jasa,
                           total_pagu_total=total_pagu_total)


@app.route('/add_job/<int:budget_line_id>', methods=['POST'])
@login_required
def add_job(budget_line_id):
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
        
    budget_line = BudgetLine.query.get_or_404(budget_line_id)
    
    nama_pekerjaan = request.form.get('nama_pekerjaan')
    tanggal_tor = request.form.get('tanggal_tor')
    tanggal_dibutuhkan = request.form.get('tanggal_dibutuhkan')
    no_vka = request.form.get('no_vka')
    coa = request.form.get('coa')
    
    rab_sebelum_ppn = request.form.get('rab_sebelum_ppn', type=float, default=0)
    est_sisa = request.form.get('est_sisa', type=float, default=0)
    
    # New Fields
    terkontrak_rp = request.form.get('terkontrak_rp', type=float, default=0)
    terbayar_rp = request.form.get('terbayar_rp', type=float, default=0)
    
    jenis_pengadaan = request.form.get('jenis_pengadaan')
    pic = request.form.get('pic')
    
    new_job = JobDetail(
        budget_line_id=budget_line.id,
        nama_pekerjaan=nama_pekerjaan,
        tanggal_tor=tanggal_tor,
        tanggal_dibutuhkan=tanggal_dibutuhkan,
        no_vka=no_vka,
        coa=coa,
        rab_sebelum_ppn=rab_sebelum_ppn,
        est_sisa=est_sisa,
        terkontrak_rp=terkontrak_rp,
        terbayar_rp=terbayar_rp,
        jenis_pengadaan=jenis_pengadaan,
        pic=pic
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    # Update Totals
    update_budget_line_totals(budget_line)
    
    return redirect(url_for('detail', kode=budget_line.kode))

def update_budget_line_totals(budget_line):
    """
    Recalculates totals for a BudgetLine based on its Jobs.
    """
    total_usulan_rab = 0
    total_terkontrak = 0
    total_terbayar = 0
    
    for job in budget_line.jobs:
        total_usulan_rab += job.rab_sebelum_ppn if job.rab_sebelum_ppn else 0
        total_terkontrak += job.terkontrak_rp if job.terkontrak_rp else 0
        total_terbayar += job.terbayar_rp if job.terbayar_rp else 0
        
    budget_line.usulan_rab_rp = total_usulan_rab
    budget_line.terkontrak_rp = total_terkontrak
    budget_line.terbayar_rp = total_terbayar
    
    db.session.commit()



@app.route('/add_progress/<int:job_id>', methods=['POST'])
@login_required
def add_progress(job_id):
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
        
    job = JobDetail.query.get_or_404(job_id)
    
    notes = request.form.get('notes')
    progress_percent = request.form.get('progress_percent', type=int)
    
    new_log = JobProgress(
        job_id=job.id,
        user_id=current_user.id,
        notes=notes,
        progress_percent=progress_percent
    )
    
    db.session.add(new_log)
    db.session.commit()
    
    redirect_to = request.args.get('redirect')
    if redirect_to == 'monitoring':
        return redirect(url_for('monitoring'))
        
    return redirect(url_for('detail', kode=job.budget_line.kode))

@app.route('/edit_progress/<int:log_id>', methods=['POST'])
@login_required
def edit_progress(log_id):
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
        
    log = JobProgress.query.get_or_404(log_id)
    
    log.notes = request.form.get('notes')
    log.progress_percent = request.form.get('progress_percent', type=int)
    
    db.session.commit()
    
    redirect_to = request.args.get('redirect')
    if redirect_to == 'monitoring':
        return redirect(url_for('monitoring'))
    
    return redirect(url_for('detail', kode=log.job.budget_line.kode))



@app.route('/update_job_status/<int:job_id>', methods=['POST'])
@login_required
def update_job_status(job_id):
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
        
    job = JobDetail.query.get_or_404(job_id)
    new_status = request.form.get('status')
    
    if new_status:
        job.status = new_status.strip()
        db.session.commit()
    
    redirect_to = request.args.get('redirect')
    if redirect_to == 'monitoring':
        tab = request.args.get('tab')
        if tab:
            return redirect(url_for('monitoring', tab=tab))
        return redirect(url_for('monitoring'))
        
    return redirect(url_for('detail', kode=job.budget_line.kode))

@app.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
        
    job = JobDetail.query.get_or_404(job_id)
    budget_line = job.budget_line
    
    db.session.delete(job)
    db.session.commit()
    
    update_budget_line_totals(budget_line)
    
    return redirect(url_for('detail', kode=budget_line.kode))

@app.route('/upload_prk', methods=['POST'])
@login_required
def upload_prk():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            filename = secure_filename(file.filename)
            df = pd.read_excel(file)
            
            # Expected columns: Kode, No PRK, Deskripsi, Pagu Material, Pagu Jasa
            # Normalize Headers? Let's assume user provides correct format or we map it
            # Simple mapping strategy:
            # Get year from form or default to current session year or system year
            current_year = datetime.datetime.now().year
            upload_year = request.form.get('tahun', type=int) or session.get('year', current_year)
            
            df.columns = [c.lower().strip() for c in df.columns]
            
            count = 0
            for _, row in df.iterrows():
                # Flexible column options
                kode = row.get('kode')
                no_prk = row.get('no prk') or row.get('nomor prk')
                deskripsi = row.get('deskripsi')
                pagu_mat = row.get('pagu material') or 0
                pagu_jasa = row.get('pagu jasa') or 0
                
                if kode and no_prk:
                    # Check if exists, update or create. IMPORTANT: Include YEAR in check
                    bl = BudgetLine.query.filter_by(kode=kode, no_prk=no_prk, tahun=upload_year).first()
                    if not bl:
                        bl = BudgetLine(kode=kode, no_prk=no_prk, tahun=upload_year)
                        db.session.add(bl)
                    
                    bl.deskripsi = deskripsi
                    bl.pagu_material = float(pagu_mat)
                    bl.pagu_jasa = float(pagu_jasa)
                    bl.pagu_total = bl.pagu_material + bl.pagu_jasa
                    count += 1
            
            db.session.commit()
            flash(f'Successfully imported {count} items!')
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            
    return redirect(url_for('index'))

@app.route('/download_template')
@login_required
def download_template():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
        
    # Create a dummy dataframe for the template
    data = {
        'Kode': ['A.1', 'B.2'],
        'No PRK': ['PRK-001', 'PRK-002'],
        'Deskripsi': ['Contoh Pengadaan A', 'Contoh Jasa B'],
        'Pagu Material': [1000000, 0],
        'Pagu Jasa': [0, 5000000]
    }
    df = pd.DataFrame(data)
    
    # Save to a temporary buffer
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    from flask import send_file
    return send_file(output, download_name="template_upload_prk.xlsx", as_attachment=True)

    from flask import send_file
    return send_file(output, download_name="template_upload_prk.xlsx", as_attachment=True)

@app.route('/delete_bulk_budget_lines', methods=['POST'])
@login_required
def delete_bulk_budget_lines():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
    
    ids = request.form.getlist('ids')
    if not ids:
        flash('No items selected', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Delete jobs first for all selected budget lines
        JobDetail.query.filter(JobDetail.budget_line_id.in_(ids)).delete(synchronize_session=False)
        
        # Delete budget lines
        BudgetLine.query.filter(BudgetLine.id.in_(ids)).delete(synchronize_session=False)
        
        db.session.commit()
        flash(f'Successfully deleted {len(ids)} items.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting items: {str(e)}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/delete_budget_line/<int:id>', methods=['POST'])
@login_required
def delete_budget_line(id):
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
    
    bl = BudgetLine.query.get_or_404(id)
    
    # Optional: Delete associated jobs first? 
    # Cascade delete should be handled by DB or manually if not set
    # Let's delete jobs manually to be safe
    JobDetail.query.filter_by(budget_line_id=id).delete()
    
    db.session.delete(bl)
    db.session.commit()
    flash('Budget Line deleted')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

import os
import datetime
import pandas as pd
from werkzeug.utils import secure_filename

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

def update_db_schema():
    with app.app_context():
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('job_detail')]
        
        if 'status' not in columns:
            print("Adding status column to job_detail...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE job_detail ADD COLUMN status TEXT DEFAULT 'User'"))
                conn.commit()
                
        if 'pic' not in columns:
            print("Adding pic column to job_detail...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE job_detail ADD COLUMN pic TEXT"))
                conn.commit()

        columns_budget = [col['name'] for col in inspector.get_columns('budget_line')]
        if 'tahun' not in columns_budget:
            print("Adding tahun column to budget_line...")
            with db.engine.connect() as conn:
                conn.execute(db.text(f"ALTER TABLE budget_line ADD COLUMN tahun INTEGER DEFAULT 2026"))
                conn.commit()

        if 'order_index' not in columns_budget:
            print("Adding order_index column to budget_line...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE budget_line ADD COLUMN order_index INTEGER DEFAULT 0"))
                conn.commit()

@app.route('/monitoring')
@login_required
def monitoring():
    current_year = datetime.datetime.now().year
    selected_year = session.get('year', current_year)

    # Get all budget lines for selected year
    budget_lines = BudgetLine.query.filter_by(tahun=selected_year).all()
    
    # Calculate counts dynamically
    unique_codes = sorted({item.kode for item in budget_lines})
    
    # PIC Filter
    selected_pic = request.args.get('pic', '')
    selected_status = request.args.get('status', '') # Status Filter
    
    # Summary Totals (Focus on Procurement Phase)
    total_summary = {
        'User': 0,
        'Rendan': 0,
        'Lakdan': 0
    }
    value_summary = {
        'User': 0,
        'Rendan': 0,
        'Lakdan': 0
    }
    
    # Get all distinct PICs
    all_jobs = JobDetail.query.all()
    unique_pics = sorted({j.pic for j in all_jobs if j.pic})
    
    procurement_jobs = []
    execution_jobs = []
    
    procurement_statuses = ['User', 'Rendan', 'Lakdan']
    
    for code in unique_codes:
        items = BudgetLine.query.filter_by(kode=code).all()
        for item in items:
            jobs = item.jobs
            
            for j in jobs:
                status = j.status or 'User'
                
                # Apply PIC Filter ONLY to 'User' status
                # If status is Rendan/Lakdan/etc, show ALL jobs regardless of PIC filter
                if selected_pic and status == 'User' and j.pic != selected_pic:
                    continue
                
                # Update Summary (based on PIC filter only, so cards remain useful)
                if status in procurement_statuses:
                    # We need to respect the filter logic for the counts too.
                    # If we filtered out this job above, we wouldn't reach here.
                    # BUT, since we changed the logic, we need to decide:
                    # Do the cards show "All Rendan" or "My Rendan"?
                    # User request: "PIC filter only active on user part".
                    # This implies for Rendan/Lakdan we see EVERYTHING.
                    if status in total_summary:
                        total_summary[status] += 1
                        value_summary[status] += (j.rab_sebelum_ppn or 0)
                
                # Apply Status Filter
                if selected_status and status != selected_status:
                    continue

                # Get latest log
                latest_log = j.progress_logs[0] if j.progress_logs else None
                latest_note = latest_log.notes if latest_log else '-'
                
                # Create Job Dict
                job_data = {
                    'kode': item.kode,
                    'no_prk': item.no_prk,
                    'deskripsi': item.deskripsi,
                    'job_name': j.nama_pekerjaan,
                    'job_status': status,
                    'job_pic': j.pic or '-',
                    'job_id': j.id, # Useful for linking
                    'job_rab': j.rab_sebelum_ppn,
                    'job_terkontrak': j.terkontrak_rp,
                    'job_terbayar': j.terbayar_rp,
                    'latest_note': latest_note
                }
                
                if status in procurement_statuses:
                    procurement_jobs.append(job_data)
                else:
                    # Everything else goes to execution (Status filter also applies here if relevant)
                    execution_jobs.append(job_data)
            
    return render_template('monitoring.html', 
                           total_summary=total_summary, 
                           value_summary=value_summary,
                           procurement_jobs=procurement_jobs,
                           execution_jobs=execution_jobs,
                           unique_pics=unique_pics,
                           selected_pic=selected_pic,
                           selected_status=selected_status,
                           selected_year=selected_year)

@app.route('/edit_job/<int:job_id>', methods=['POST'])
@login_required
def edit_job(job_id):
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
    
    job = JobDetail.query.get_or_404(job_id)
    
    job.nama_pekerjaan = request.form.get('nama_pekerjaan')
    job.tanggal_tor = request.form.get('tanggal_tor')
    job.tanggal_dibutuhkan = request.form.get('tanggal_dibutuhkan')
    job.no_vka = request.form.get('no_vka')
    job.coa = request.form.get('coa')
    job.rab_sebelum_ppn = request.form.get('rab_sebelum_ppn', type=float, default=0)
    job.est_sisa = request.form.get('est_sisa', type=float, default=0)
    job.terkontrak_rp = request.form.get('terkontrak_rp', type=float, default=0)
    job.terbayar_rp = request.form.get('terbayar_rp', type=float, default=0)
    job.jenis_pengadaan = request.form.get('jenis_pengadaan')
    job.status = request.form.get('status')
    job.pic = request.form.get('pic')
    
    db.session.commit()
    
    update_budget_line_totals(job.budget_line)
    
    return redirect(url_for('detail', kode=job.budget_line.kode))

@app.route('/export_excel')
@login_required
def export_excel():
    current_year = datetime.datetime.now().year
    selected_year = session.get('year', current_year)

    # Query all Budget Lines for selected year
    budget_lines = BudgetLine.query.filter_by(tahun=selected_year).all()
    
    data = []
    
    for bl in budget_lines:
        # Base info for the budget line
        base_info = {
            'Kode Anggaran': bl.kode,
            'No PRK': bl.no_prk,
            'Deskripsi PRK': bl.deskripsi,
            'Pagu Material': bl.pagu_material,
            'Pagu Jasa': bl.pagu_jasa,
            'Pagu Total': bl.pagu_total,
            'Realisasi Ellipse': bl.ellipse_rp
        }
        
        if not bl.jobs:
            # If no jobs, add row with empty job details
            row = base_info.copy()
            row.update({
                'Nama Pekerjaan': '-',
                'Status': '-',
                'PIC': '-',
                'Tanggal TOR': '-',
                'Tanggal Dibutuhkan': '-',
                'No VKA': '-',
                'COA': '-',
                'RAB (Seb. PPN)': 0,
                'Terkontrak': 0,
                'Terbayar': 0,
                'Jenis Pengadaan': '-',
                'Est. Sisa': 0
            })
            data.append(row)
        else:
            for job in bl.jobs:
                row = base_info.copy()
                row.update({
                    'Nama Pekerjaan': job.nama_pekerjaan,
                    'Status': job.status or 'User',
                    'PIC': job.pic or '-',
                    'Tanggal TOR': job.tanggal_tor,
                    'Tanggal Dibutuhkan': job.tanggal_dibutuhkan,
                    'No VKA': job.no_vka,
                    'COA': job.coa,
                    'RAB (Seb. PPN)': job.rab_sebelum_ppn,
                    'Terkontrak': job.terkontrak_rp,
                    'Terbayar': job.terbayar_rp,
                    'Jenis Pengadaan': job.jenis_pengadaan,
                    'Est. Sisa': job.est_sisa
                })
                data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Export to BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Monitoring')
    
    output.seek(0)
    
    filename = f"Data_Monitoring_Anggaran_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        download_name=filename,
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/get_job_logs/<int:job_id>')
@login_required
def get_job_logs(job_id):
    logs = JobProgress.query.filter_by(job_id=job_id).order_by(JobProgress.created_at.desc()).all()
    
    logs_data = []
    for log in logs:
        # Get user name
        user = User.query.get(log.user_id)
        user_name = user.username if user else "Unknown"
        
        logs_data.append({
            'id': log.id,
            'notes': log.notes,
            'created_at': log.created_at.strftime('%d %b %Y %H:%M'),
            'user_name': user_name,
            'user_id': log.user_id
        })
        
    return jsonify(logs_data)

@app.route('/users')
@login_required
def list_users():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
        
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'danger')
        return redirect(url_for('list_users'))
        
    new_user = User(username=username, password_hash=generate_password_hash(password), role=role)
    db.session.add(new_user)
    db.session.commit()
    flash('User added successfully', 'success')
    return redirect(url_for('list_users'))

@app.route('/users/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
        
    user = User.query.get_or_404(id)
    user.role = request.form.get('role')
    
    password = request.form.get('password')
    if password:
        user.password_hash = generate_password_hash(password)
        
    db.session.commit()
    flash('User updated successfully', 'success')
    return redirect(url_for('list_users'))

@app.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
        
    user = User.query.get_or_404(id)
    if user.username == 'superadmin': # Prevent deleting main superadmin if desired
        flash('Cannot delete main superadmin', 'error')
        return redirect(url_for('list_users'))
        
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('list_users'))

@app.route('/reorder_budget_lines', methods=['POST'])
@login_required
def reorder_budget_lines():
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
        
    order_data = request.json.get('order', [])
    
    # order_data should be a list of IDs in the new order
    # e.g. [3, 1, 2, 5, 4]
    
    try:
        if not order_data:
             return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        for index, item_id in enumerate(order_data):
            # Optimally we would do a bulk update, but loop is fine for small datasets
            db.session.execute(
                db.update(BudgetLine).where(BudgetLine.id == item_id).values(order_index=index)
            )
            
        db.session.commit()
        return jsonify({'status': 'success'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        # Create default users
        create_default_users()
        # Verify schema
        update_db_schema()
        
    app.run(host='0.0.0.0', port=9000, debug=True)
