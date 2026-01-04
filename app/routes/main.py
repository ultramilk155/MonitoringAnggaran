from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models import BudgetLine, JobDetail, JobProgress, User
import datetime
import pandas as pd
from io import BytesIO

bp = Blueprint('main', __name__)

@bp.route('/')
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

@bp.route('/set_year/<int:year>')
def set_year(year):
    session['year'] = year
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/detail/<kode>')
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

@bp.route('/add_job/<int:budget_line_id>', methods=['POST'])
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
    
    return redirect(url_for('main.detail', kode=budget_line.kode))

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

@bp.route('/add_progress/<int:job_id>', methods=['POST'])
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
        return redirect(url_for('main.monitoring'))
        
    return redirect(url_for('main.detail', kode=job.budget_line.kode))

@bp.route('/edit_progress/<int:log_id>', methods=['POST'])
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
        return redirect(url_for('main.monitoring'))
    
    return redirect(url_for('main.detail', kode=log.job.budget_line.kode))

@bp.route('/update_job_status/<int:job_id>', methods=['POST'])
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
            return redirect(url_for('main.monitoring', tab=tab))
        return redirect(url_for('main.monitoring'))
        
    return redirect(url_for('main.detail', kode=job.budget_line.kode))

@bp.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
        
    job = JobDetail.query.get_or_404(job_id)
    budget_line = job.budget_line
    
    db.session.delete(job)
    db.session.commit()
    
    update_budget_line_totals(budget_line)
    
    return redirect(url_for('main.detail', kode=budget_line.kode))

@bp.route('/monitoring')
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
                if selected_pic and status == 'User' and j.pic != selected_pic:
                    continue
                
                # Update Summary
                if status in procurement_statuses:
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
                    'job_id': j.id,
                    'job_rab': j.rab_sebelum_ppn,
                    'job_terkontrak': j.terkontrak_rp,
                    'job_terbayar': j.terbayar_rp,
                    'latest_note': latest_note
                }
                
                if status in procurement_statuses:
                    procurement_jobs.append(job_data)
                else:
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

@bp.route('/edit_job/<int:job_id>', methods=['POST'])
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
    
    return redirect(url_for('main.detail', kode=job.budget_line.kode))

@bp.route('/export_excel')
@login_required
def export_excel():
    current_year = datetime.datetime.now().year
    selected_year = session.get('year', current_year)

    # Query all Budget Lines for selected year
    budget_lines = BudgetLine.query.filter_by(tahun=selected_year).all()
    
    data = []
    
    for bl in budget_lines:
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
    
    df = pd.DataFrame(data)
    
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

@bp.route('/get_job_logs/<int:job_id>')
@login_required
def get_job_logs(job_id):
    logs = JobProgress.query.filter_by(job_id=job_id).order_by(JobProgress.created_at.desc()).all()
    
    logs_data = []
    for log in logs:
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
