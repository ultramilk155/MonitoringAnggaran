from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import BudgetLine, JobDetail, User, UserRole, Permission, RolePermission, Role
from app.decorators import role_required, permission_required
import pandas as pd
import datetime
from io import BytesIO

bp = Blueprint('admin', __name__)

@bp.route('/users')
@login_required
@permission_required('manage_users')
def list_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@bp.route('/users/add', methods=['POST'])
@login_required
@permission_required('manage_users')
def add_user():
        
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
@permission_required('manage_users')
def edit_user(id):
        
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
@permission_required('manage_users')
def delete_user(id):
        
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
@permission_required('upload_prk')
def upload_prk():
    
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
@permission_required('upload_prk')
def download_template():
        
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
@permission_required('delete_budget_line')
def delete_bulk_budget_lines():
    
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
@permission_required('delete_budget_line')
def delete_budget_line(id):
    
    bl = BudgetLine.query.get_or_404(id)
    JobDetail.query.filter_by(budget_line_id=id).delete()
    
    db.session.delete(bl)
    db.session.commit()
    flash('Budget Line deleted')
    return redirect(url_for('main.index'))

@bp.route('/reorder_budget_lines', methods=['POST'])
@login_required
@permission_required('reorder_budget_lines')
def reorder_budget_lines():
        
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

# ==================== PERMISSION MANAGEMENT ====================

@bp.route('/permissions')
@bp.route('/permissions/<selected_role>')
@login_required
@role_required(UserRole.SUPER_ADMIN)
def manage_permissions(selected_role=None):
    """Display permission matrix with sidebar layout."""
    # Get all roles from database
    db_roles = Role.query.all()
    
    # If no roles in DB, seed defaults
    if not db_roles:
        for role_name in UserRole.default_roles():
            role = Role(name=role_name, is_system=True, 
                       description='System role' if role_name == UserRole.SUPER_ADMIN else '')
            db.session.add(role)
        db.session.commit()
        db_roles = Role.query.all()
    
    # Sort by hierarchy: super_admin > admin > viewer > custom roles
    role_order = {UserRole.SUPER_ADMIN: 0, UserRole.ADMIN: 1, UserRole.VIEWER: 2}
    db_roles = sorted(db_roles, key=lambda r: role_order.get(r.name, 99))
    
    # Select first role if none specified
    if not selected_role:
        selected_role = db_roles[0].name if db_roles else UserRole.SUPER_ADMIN
    
    # Get permissions grouped by category
    permissions = Permission.query.order_by(Permission.category, Permission.name).all()
    categories = {}
    for perm in permissions:
        if perm.category not in categories:
            categories[perm.category] = []
        # Check if this role has the permission
        is_allowed = False
        if selected_role == UserRole.SUPER_ADMIN:
            is_allowed = True  # Super admin has all
        else:
            rp = RolePermission.query.filter_by(role=selected_role, permission_id=perm.id).first()
            is_allowed = rp.is_allowed if rp else False
        categories[perm.category].append({
            'permission': perm,
            'is_allowed': is_allowed
        })
    
    return render_template('manage_permissions.html',
                          roles=db_roles,
                          selected_role=selected_role,
                          categories=categories,
                          is_super_admin=(selected_role == UserRole.SUPER_ADMIN))

@bp.route('/permissions/update/<role_name>', methods=['POST'])
@login_required
@role_required(UserRole.SUPER_ADMIN)
def update_role_permissions(role_name):
    """Update permissions for a specific role."""
    if role_name == UserRole.SUPER_ADMIN:
        flash('Super Admin permissions cannot be modified.', 'warning')
        return redirect(url_for('admin.manage_permissions', selected_role=role_name))
    
    try:
        permissions = Permission.query.all()
        for perm in permissions:
            checkbox_name = f"perm_{perm.id}"
            is_allowed = checkbox_name in request.form
            
            role_perm = RolePermission.query.filter_by(role=role_name, permission_id=perm.id).first()
            if role_perm:
                role_perm.is_allowed = is_allowed
            else:
                role_perm = RolePermission(role=role_name, permission_id=perm.id, is_allowed=is_allowed)
                db.session.add(role_perm)
        
        db.session.commit()
        flash(f'Permissions for "{role_name}" updated!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_permissions', selected_role=role_name))

@bp.route('/roles/add', methods=['POST'])
@login_required
@role_required(UserRole.SUPER_ADMIN)
def add_role():
    """Add a new custom role."""
    name = request.form.get('name', '').strip().lower().replace(' ', '_')
    description = request.form.get('description', '')
    
    if not name:
        flash('Role name is required', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    if Role.query.filter_by(name=name).first():
        flash('Role already exists', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    role = Role(name=name, description=description, is_system=False)
    db.session.add(role)
    db.session.commit()
    
    flash(f'Role "{name}" created!', 'success')
    return redirect(url_for('admin.manage_permissions', selected_role=name))

@bp.route('/roles/delete/<int:id>', methods=['POST'])
@login_required
@role_required(UserRole.SUPER_ADMIN)
def delete_role(id):
    """Delete a custom role."""
    role = Role.query.get_or_404(id)
    
    if role.is_system:
        flash('Cannot delete system roles', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    # Check if any users have this role
    users_with_role = User.query.filter_by(role=role.name).count()
    if users_with_role > 0:
        flash(f'Cannot delete: {users_with_role} user(s) have this role', 'danger')
        return redirect(url_for('admin.manage_permissions', selected_role=role.name))
    
    # Delete role permissions
    RolePermission.query.filter_by(role=role.name).delete()
    db.session.delete(role)
    db.session.commit()
    
    flash(f'Role "{role.name}" deleted!', 'success')
    return redirect(url_for('admin.manage_permissions'))

@bp.route('/permissions/add', methods=['POST'])
@login_required
@role_required(UserRole.SUPER_ADMIN)
def add_permission():
    """Add a new permission."""
    name = request.form.get('name', '').strip().lower().replace(' ', '_')
    description = request.form.get('description', '')
    category = request.form.get('category', 'general')
    
    if not name:
        flash('Permission name is required', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    if Permission.query.filter_by(name=name).first():
        flash('Permission already exists', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    perm = Permission(name=name, description=description, category=category)
    db.session.add(perm)
    db.session.commit()
    
    flash(f'Permission "{name}" added!', 'success')
    return redirect(url_for('admin.manage_permissions'))

@bp.route('/permissions/delete/<int:id>', methods=['POST'])
@login_required
@role_required(UserRole.SUPER_ADMIN)
def delete_permission(id):
    """Delete a permission."""
    perm = Permission.query.get_or_404(id)
    RolePermission.query.filter_by(permission_id=id).delete()
    db.session.delete(perm)
    db.session.commit()
    
    flash(f'Permission "{perm.name}" deleted!', 'success')
    return redirect(url_for('admin.manage_permissions'))

