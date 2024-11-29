from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.role import Role
from app.models.audit_log import AuditLog
from app.forms.staff_forms import StaffForm
from app.decorators import permission_required, manager_required
from datetime import datetime

staff = Blueprint('staff', __name__)

@staff.route('/staff')
@login_required
@permission_required('manage_staff')
def staff_list():
    """List all staff members"""
    staff_members = User.query.filter_by(restaurant_name=current_user.restaurant_name).all()
    
    # Get recent audit logs if user has permission
    recent_logs = None
    if current_user.has_permission('view_audit_logs'):
        recent_logs = AuditLog.query.filter_by(
            restaurant_name=current_user.restaurant_name
        ).filter(
            AuditLog.action.in_(['create_staff', 'edit_staff', 'toggle_staff_status'])
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(10).all()
    
    return render_template('staff/list.html', 
                         staff_members=staff_members,
                         recent_logs=recent_logs)

@staff.route('/staff/add', methods=['GET', 'POST'])
@login_required
@permission_required('manage_staff')
def create_staff():
    """Create a new staff account"""
    form = StaffForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            restaurant_name=current_user.restaurant_name,
            role_id=form.role.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Log staff creation
            AuditLog.log_action(
                user=current_user,
                action='create_staff',
                details={
                    'staff_name': user.name,
                    'staff_email': user.email,
                    'role_id': user.role_id
                },
                ip_address=request.remote_addr,
                target_type='user',
                target_id=user.id
            )
            
            flash('Staff member created successfully!', 'success')
            return redirect(url_for('staff.staff_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating staff member: {str(e)}', 'error')
    
    return render_template('staff/add_edit.html', form=form, title='Add Staff Member')

@staff.route('/staff/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_staff')
def edit_staff(id):
    """Edit a staff member's details"""
    user = User.query.get_or_404(id)
    if user.restaurant_name != current_user.restaurant_name:
        flash('You can only edit staff members from your restaurant.', 'error')
        return redirect(url_for('staff.staff_list'))
    
    form = StaffForm(obj=user)
    if form.validate_on_submit():
        try:
            # Store old values for audit log
            old_values = {
                'name': user.name,
                'email': user.email,
                'role_id': user.role_id
            }
            
            # Update user details
            user.name = form.name.data
            user.email = form.email.data
            user.role_id = form.role.data
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            
            # Log staff update
            AuditLog.log_action(
                user=current_user,
                action='edit_staff',
                details={
                    'old_values': old_values,
                    'new_values': {
                        'name': user.name,
                        'email': user.email,
                        'role_id': user.role_id
                    },
                    'password_changed': bool(form.password.data)
                },
                ip_address=request.remote_addr,
                target_type='user',
                target_id=user.id
            )
            
            flash('Staff member updated successfully!', 'success')
            return redirect(url_for('staff.staff_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating staff member: {str(e)}', 'error')
    
    return render_template('staff/add_edit.html', form=form, title='Edit Staff Member')

@staff.route('/staff/toggle/<int:id>', methods=['POST'])
@login_required
@permission_required('manage_staff')
def toggle_staff_status(id):
    """Toggle staff member's active status"""
    user = User.query.get_or_404(id)
    if user.restaurant_name != current_user.restaurant_name:
        flash('You can only manage staff members from your restaurant.', 'error')
        return redirect(url_for('staff.staff_list'))
    
    try:
        old_status = user.is_active
        user.is_active = not old_status
        db.session.commit()
        
        # Log status change
        AuditLog.log_action(
            user=current_user,
            action='toggle_staff_status',
            details={
                'staff_id': user.id,
                'staff_email': user.email,
                'old_status': old_status,
                'new_status': user.is_active
            },
            ip_address=request.remote_addr,
            target_type='user',
            target_id=user.id
        )
        
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'Staff member {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling staff status: {str(e)}', 'error')
    
    return redirect(url_for('staff.staff_list'))

@staff.route('/audit-logs')
@login_required
@permission_required('view_audit_logs')
def audit_logs():
    """View audit logs with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('LOGS_PER_PAGE', 20)
        
        # Base query
        query = AuditLog.query.filter_by(restaurant_name=current_user.restaurant_name)
        
        # Apply filters
        action = request.args.get('action')
        if action:
            query = query.filter(AuditLog.action == action)
        
        # Date filters with error handling
        try:
            start_date = request.args.get('start_date')
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(AuditLog.timestamp >= start_date)
            
            end_date = request.args.get('end_date')
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # Add one day to include the entire end date
                end_date = end_date.replace(hour=23, minute=59, second=59)
                query = query.filter(AuditLog.timestamp <= end_date)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
        
        # Target type filter
        target_type = request.args.get('target_type')
        if target_type:
            query = query.filter(AuditLog.target_type == target_type)
        
        # Get distinct target types for filter dropdown
        target_types = db.session.query(AuditLog.target_type).distinct().all()
        target_types = [t[0] for t in target_types if t[0]]  # Remove None values
        
        # Get distinct actions for filter dropdown
        actions = db.session.query(AuditLog.action).distinct().all()
        actions = [a[0] for a in actions]
        
        # Order by most recent first
        query = query.order_by(AuditLog.timestamp.desc())
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page)
        logs = pagination.items
        
        return render_template('staff/audit_logs.html', 
                             logs=logs, 
                             pagination=pagination,
                             target_types=target_types,
                             actions=actions,
                             current_filters={
                                 'action': action,
                                 'start_date': request.args.get('start_date'),
                                 'end_date': request.args.get('end_date'),
                                 'target_type': target_type
                             })
    
    except Exception as e:
        flash(f'Error retrieving audit logs: {str(e)}', 'error')
        return redirect(url_for('staff.staff_list'))
