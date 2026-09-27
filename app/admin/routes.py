from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.admin import admin_bp
from app.admin.forms import UserForm, OrganizationForm, RoleForm, SystemSettingsForm
from app.decorators import role_required, admin_required
from app.models import User, Role, Organization


@admin_bp.route('/')
@login_required
@admin_required
def index():
    stats = {
        'users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'organizations': Organization.query.count(),
        'roles': Role.query.count(),
    }
    return render_template('admin/index.html', title='Admin Dashboard', stats=stats)


# -------------------- Users --------------------
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/users.html', title='Manage Users',
                           users=pagination.items, pagination=pagination)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            role_id=form.role.data,
            organization_id=form.organization.data if form.organization.data != 0 else None,
            is_active=form.is_active.data
        )
        if form.password.data:
            user.password = form.password.data
        else:
            user.password = 'ChangeMe123!'  # temporary password
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.name} created successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', form=form, title='Create User')


@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(user=user, obj=user)
    if form.validate_on_submit():
        user.name = form.name.data.strip()
        user.email = form.email.data.lower().strip()
        user.role_id = form.role.data
        user.organization_id = form.organization.data if form.organization.data != 0 else None
        user.is_active = form.is_active.data
        if form.password.data:
            user.password = form.password.data
        db.session.commit()
        flash(f'User {user.name} updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)


@admin_bp.route('/users/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.name} has been {status}.', 'success')
    return redirect(url_for('admin.users'))


# -------------------- Organizations --------------------
@admin_bp.route('/organizations')
@login_required
@admin_required
def organizations():
    page = request.args.get('page', 1, type=int)
    pagination = Organization.query.order_by(Organization.name).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/organizations.html', title='Manage Organizations',
                           organizations=pagination.items, pagination=pagination)


@admin_bp.route('/organizations/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_organization():
    form = OrganizationForm()
    if form.validate_on_submit():
        org = Organization(
            name=form.name.data.strip(),
            type=form.type.data,
            registration_no=form.registration_no.data or None,
            contact_email=form.contact_email.data or None,
            contact_phone=form.contact_phone.data or None,
            address=form.address.data or None,
            country=form.country.data or None,
            is_verified=form.is_verified.data,
            is_active=form.is_active.data
        )
        db.session.add(org)
        db.session.commit()
        flash(f'Organization "{org.name}" created successfully.', 'success')
        return redirect(url_for('admin.organizations'))
    return render_template('admin/organization_form.html', form=form, title='Create Organization')


@admin_bp.route('/organizations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_organization(id):
    org = Organization.query.get_or_404(id)
    form = OrganizationForm(obj=org)
    if form.validate_on_submit():
        org.name = form.name.data.strip()
        org.type = form.type.data
        org.registration_no = form.registration_no.data or None
        org.contact_email = form.contact_email.data or None
        org.contact_phone = form.contact_phone.data or None
        org.address = form.address.data or None
        org.country = form.country.data or None
        org.is_verified = form.is_verified.data
        org.is_active = form.is_active.data
        db.session.commit()
        flash(f'Organization "{org.name}" updated successfully.', 'success')
        return redirect(url_for('admin.organizations'))
    return render_template('admin/organization_form.html', form=form, title='Edit Organization', org=org)


# -------------------- Roles --------------------
@admin_bp.route('/roles')
@login_required
@admin_required
def roles():
    roles_list = Role.query.order_by(Role.name).all()
    return render_template('admin/roles.html', title='Manage Roles', roles=roles_list)


@admin_bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_role():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(
            name=form.name.data.strip(),
            description=form.description.data,
            is_default=form.is_default.data
        )
        db.session.add(role)
        db.session.commit()
        flash(f'Role "{role.name}" created.', 'success')
        return redirect(url_for('admin.roles'))
    return render_template('admin/role_form.html', form=form, title='Create Role')


@admin_bp.route('/roles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(id):
    role = Role.query.get_or_404(id)
    form = RoleForm(role=role, obj=role)
    if form.validate_on_submit():
        role.name = form.name.data.strip()
        role.description = form.description.data
        role.is_default = form.is_default.data
        db.session.commit()
        flash(f'Role "{role.name}" updated.', 'success')
        return redirect(url_for('admin.roles'))
    return render_template('admin/role_form.html', form=form, title='Edit Role', role=role)


# -------------------- System Settings (placeholder) --------------------
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    form = SystemSettingsForm()
    if form.validate_on_submit():
        # In a real app these would be stored in DB or config
        flash('System settings saved (demo – values not persisted yet).', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html', form=form, title='System Settings')