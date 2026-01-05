from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import BudgetLine, JobDetail, User
import pandas as pd
import datetime
from io import BytesIO

bp = Blueprint('admin', __name__)

@bp.route('/users')
@login_required
def list_users():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@bp.route('/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
        
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'danger')
        return redirect(url_for('admin.list_users'))
        
    new_user = User(username=username, password_hash=generate_password_hash(password), role=role)
    db.session.add(new_user)
    db.session.commit()
    flash('User added successfully', 'success')
    return redirect(url_for('admin.list_users'))

@bp.route('/users/edit/<int:id>', methods=['POST'])
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
    return redirect(url_for('admin.list_users'))

@bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
        
    user = User.query.get_or_404(id)
    if user.username == 'superadmin':
        flash('Cannot delete main superadmin', 'error')
        return redirect(url_for('admin.list_users'))
        
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.list_users'))

@bp.route('/upload_prk', methods=['POST'])
@login_required
def upload_prk():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('main.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('main.index'))
    
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            # Secure filename is good practice
            filename = secure_filename(file.filename)
            df = pd.read_excel(file)
            
            current_year = datetime.datetime.now().year
            upload_year = request.form.get('tahun', type=int) or session.get('year', current_year)
            
            df.columns = [c.lower().strip() for c in df.columns]
            
            count = 0
            for _, row in df.iterrows():
                kode = row.get('kode')
                no_prk = row.get('no prk') or row.get('nomor prk')
                deskripsi = row.get('deskripsi')
                pagu_mat = row.get('pagu material') or 0
                pagu_jasa = row.get('pagu jasa') or 0
                
                if kode and no_prk:
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
            
    return redirect(url_for('main.index'))

@bp.route('/download_template')
@login_required
def download_template():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
        
    data = {
        'Kode': ['A.1', 'B.2'],
        'No PRK': ['PRK-001', 'PRK-002'],
        'Deskripsi': ['Contoh Pengadaan A', 'Contoh Jasa B'],
        'Pagu Material': [1000000, 0],
        'Pagu Jasa': [0, 5000000]
    }
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    return send_file(output, download_name="template_upload_prk.xlsx", as_attachment=True)

@bp.route('/delete_bulk_budget_lines', methods=['POST'])
@login_required
def delete_bulk_budget_lines():
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
    
    ids = request.form.getlist('ids')
    if not ids:
        flash('No items selected', 'warning')
        return redirect(url_for('main.index'))
    
    try:
        JobDetail.query.filter(JobDetail.budget_line_id.in_(ids)).delete(synchronize_session=False)
        BudgetLine.query.filter(BudgetLine.id.in_(ids)).delete(synchronize_session=False)
        
        db.session.commit()
        flash(f'Successfully deleted {len(ids)} items.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting items: {str(e)}', 'danger')
        
    return redirect(url_for('main.index'))

@bp.route('/delete_budget_line/<int:id>', methods=['POST'])
@login_required
def delete_budget_line(id):
    if current_user.role != 'super_admin':
        return "Unauthorized", 403
    
    bl = BudgetLine.query.get_or_404(id)
    JobDetail.query.filter_by(budget_line_id=id).delete()
    
    db.session.delete(bl)
    db.session.commit()
    flash('Budget Line deleted')
    return redirect(url_for('main.index'))

@bp.route('/reorder_budget_lines', methods=['POST'])
@login_required
def reorder_budget_lines():
    if current_user.role not in ['admin', 'super_admin']:
        return "Unauthorized", 403
        
    order_data = request.json.get('order', [])
    
    try:
        if not order_data:
             return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        for index, item_id in enumerate(order_data):
            db.session.execute(
                db.update(BudgetLine).where(BudgetLine.id == item_id).values(order_index=index)
            )
            
        db.session.commit()
        return jsonify({'status': 'success'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/check-ellipse')
@login_required
def check_ellipse():
    from app.services.ellipse import ellipse_service
    success, message = ellipse_service.check_connection()
    return jsonify({
        'status': 'connected' if success else 'disconnected',
        'message': message
    })
