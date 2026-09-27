from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.main import main_bp
from app.models import (
    User, Role, Organization, Product, Certificate, ComplianceRule,
    SupplyChainEvent, AuditLog
)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='TracePass – Digital Product Passport')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_orgs': Organization.query.count(),
        'total_products': Product.query.count(),
        'published': Product.query.filter_by(status='published').count(),
        'pending_review': Product.query.filter_by(compliance_status='under_review').count(),
        'certificates': Certificate.query.count(),
        'expired_certs': sum(1 for c in Certificate.query.all() if c.is_expired),
        'events': SupplyChainEvent.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
    }

    role_counts = {r.name: r.users.count() for r in Role.query.all()}
    status_counts = {
        'draft': Product.query.filter_by(status='draft').count(),
        'submitted': Product.query.filter_by(status='submitted').count(),
        'published': Product.query.filter_by(status='published').count(),
        'archived': Product.query.filter_by(status='archived').count(),
    }
    compliance_counts = {
        'pending': Product.query.filter_by(compliance_status='pending').count(),
        'under_review': Product.query.filter_by(compliance_status='under_review').count(),
        'compliant': Product.query.filter_by(compliance_status='compliant').count(),
        'non_compliant': Product.query.filter_by(compliance_status='non_compliant').count(),
    }

    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(8).all()

    return render_template(
        'dashboard.html',
        title='Dashboard',
        stats=stats,
        role_counts=role_counts,
        status_counts=status_counts,
        compliance_counts=compliance_counts,
        recent_products=recent_products,
        recent_logs=recent_logs,
        user=current_user
    )


@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='My Profile', user=current_user)
