from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm, ProfileForm

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
        current_user.github_url = form.github_url.data
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html', form=form, title='My Profile')


@auth.route('/developer/<int:user_id>')
def developer(user_id):
    user = User.query.get_or_404(user_id)
    projects = user.projects.order_by('created_at desc').all()
    return render_template('auth/developer.html', user=user, projects=projects, title=user.username)
