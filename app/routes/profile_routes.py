from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.forms.profile_forms import ProfileForm, ChangePasswordForm
from werkzeug.security import generate_password_hash, check_password_hash

profile = Blueprint('profile', __name__)

@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    """View and edit user profile"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.restaurant_name = form.restaurant_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
    
    return render_template('profile/view.html', form=form)

@profile.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.password_hash = generate_password_hash(form.new_password.data)
            
            try:
                db.session.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for('profile.view_profile'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error changing password: {str(e)}', 'error')
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('profile/change_password.html', form=form)

@profile.route('/profile/settings')
@login_required
def settings():
    """View and edit user settings"""
    return render_template('profile/settings.html')
