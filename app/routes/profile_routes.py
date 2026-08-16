from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import User
from app.forms import UpdateProfileForm, ChangePasswordForm
import os
from datetime import datetime

# Use 'dashboard' so url_for('dashboard.profile') works
dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if request.method == 'POST':
        if 'update_profile' in request.form and profile_form.validate_on_submit():
            current_user.name = profile_form.name.data
            current_user.email = profile_form.email.data

            # Handle avatar upload
            if profile_form.avatar.data:
                avatar = profile_form.avatar.data
                filename = f"user_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{avatar.filename.split('.')[-1]}"
                avatar_path = os.path.join('app', 'static', 'uploads', 'avatars', filename)
                avatar.save(avatar_path)
                current_user.avatar = filename

            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('dashboard.profile'))

        if 'change_password' in request.form and password_form.validate_on_submit():
            if not current_user.check_password(password_form.current_password.data):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('dashboard.profile'))

            current_user.password_hash = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash('Your password has been changed!', 'success')
            return redirect(url_for('dashboard.profile'))

    return render_template('profile.html', profile_form=profile_form, password_form=password_form)