from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
import os, uuid
from app import db, mail
from app.models import User
from app.forms import RegistrationForm, LoginForm, ProfileForm, ForgotPasswordForm, ResetPasswordForm

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('main.feed'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Check username uniqueness (excluding current user)
        existing = User.query.filter_by(username=form.username.data).first()
        if existing and existing.id != current_user.id:
            flash('Username already taken.', 'danger')
            return render_template('auth/profile.html', form=form, title='Profile')
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.role_title = form.role_title.data or 'Developer'
        current_user.github_url = form.github_url.data

        # Handle file upload only
        if form.avatar_upload.data:
            file = form.avatar_upload.data
            ext = file.filename.rsplit('.', 1)[-1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, secure_filename(filename)))
            current_user.avatar_url = url_for('static', filename=f'uploads/{filename}')

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html', form=form, title='My Profile')


@auth.route('/developer/<int:user_id>')
def developer(user_id):
    user = User.query.get_or_404(user_id)
    from app.models import Project
    projects = user.projects.order_by(Project.created_at.desc()).all()
    return render_template('auth/developer.html', user=user, projects=projects, title=user.username)


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            try:
                msg = Message('MzansiBuilds – Password Reset',
                              recipients=[user.email])
                msg.html = render_template('auth/reset_email.html',
                                           user=user, reset_url=reset_url)
                mail.send(msg)
            except Exception:
                pass  # Fail silently if SMTP is not configured
        flash('If that email exists, a reset link has been sent. Check your inbox.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form, title='Forgot Password')


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    from datetime import datetime
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        flash('Password has been reset! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, title='Reset Password')
