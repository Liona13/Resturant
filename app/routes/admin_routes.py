from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.role import Role
from app.forms.admin_forms import UserRoleForm
from app.decorators import admin_required

admin = Blueprint('admin', __name__)

@admin.route('/admin/users')
@login_required
@admin_required
def user_list():
    """Display list of users"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/users/<int:user_id>/role', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_role(user_id):
    """Edit a user's role"""
    user = User.query.get_or_404(user_id)
    form = UserRoleForm()
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if form.validate_on_submit():
        user.role_id = form.role.data
        try:
            db.session.commit()
            flash(f'Role updated for user {user.email}')
            return redirect(url_for('admin.user_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating role: {str(e)}')
    
    form.role.data = user.role_id
    return render_template('admin/edit_user_role.html', form=form, user=user)

@admin.route('/admin/roles')
@login_required
@admin_required
def role_list():
    """Display list of roles and their permissions"""
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles)
