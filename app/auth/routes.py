from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.models import User, Role


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Contact an administrator.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form, title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        customer_role = Role.query.filter_by(name='Customer').first()
        if customer_role is None:
            flash('System not ready. Please contact administrator.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            role_id=customer_role.id,
            organization_id=None
        )
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You are registered as a Customer. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, title='Register')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.current_password.data):
            current_user.password = form.new_password.data
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('auth/change_password.html', form=form, title='Change Password')
