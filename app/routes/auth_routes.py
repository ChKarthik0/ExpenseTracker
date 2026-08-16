from flask import Blueprint, render_template, redirect, url_for, flash, request 
from flask_login import login_user, logout_user, login_required, current_user 
from werkzeug.security import generate_password_hash, check_password_hash 
from app import db 
from app.models.user import User 
from app.forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # ✅ Create username from email prefix if not explicitly provided
        email_lower = form.email.data.lower()
        username = email_lower.split('@')[0]  

        hashed_password = generate_password_hash(
            form.password.data, method='pbkdf2:sha256', salt_length=16
        )

        new_user = User(
            username=username,
            email=email_lower,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('✅ Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            flash(f'✅ Welcome back, {user.username}!', 'success')

            # ✅ Redirect to Home (Welcome page), NOT Dashboard
            return redirect(url_for('home.home'))

        else:
            flash('❌ Invalid email or password', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('✅ You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password', methods=['GET','POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email.lower()).first()

        if user:
            flash('🔗 Reset Link sent to your email (simulation).', 'info')
        else:
            flash('❌ No account found with that email.', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('index.html')
