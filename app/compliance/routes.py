from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.compliance import compliance_bp
from app.compliance.forms import CertificateForm, RuleForm, ReviewForm
from app.decorators import role_required
from app.models import (
    Product, Certificate, ComplianceRule, ComplianceCheck, ComplianceReview,
    Organization, AuditLog, Recall, SupplyChainEvent
)


@compliance_bp.route('/certificates')
@login_required
@role_required('Supplier', 'Manufacturer', 'Auditor', 'Admin')
def certificates():
    page = request.args.get('page', 1, type=int)
    pagination = Certificate.query.order_by(Certificate.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('compliance/certificates.html', certificates=pagination.items,
                           pagination=pagination, title='Certificates')


@compliance_bp.route('/certificates/add', methods=['GET', 'POST'])
@login_required
@role_required('Supplier', 'Manufacturer', 'Admin')
def add_certificate():
    form = CertificateForm()
    form.organization_id.choices = [(0, '— None —')] + [
        (o.id, o.name) for o in Organization.query.order_by(Organization.name).all()
    ]
    form.product_id.choices = [(0, '— None —')] + [
        (p.id, f'{p.passport_code} — {p.name}') for p in Product.query.order_by(Product.name).all()
    ]
    if form.validate_on_submit():
        cert = Certificate(
            cert_type=form.cert_type.data.strip(),
            issuer=form.issuer.data,
            issue_date=form.issue_date.data,
            expiry_date=form.expiry_date.data,
            organization_id=form.organization_id.data if form.organization_id.data else None,
            product_id=form.product_id.data if form.product_id.data else None,
            uploaded_by=current_user.id,
            verification_status='pending'
        )
        if form.file.data:
            f = form.file.data
            filename = secure_filename(f.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            path = os.path.join(upload_dir, filename)
            f.save(path)
            cert.file_path = filename
        db.session.add(cert)
        db.session.commit()
        flash('Certificate saved.', 'success')
        return redirect(url_for('compliance.certificates'))
    return render_template('compliance/certificate_form.html', form=form, title='Add Certificate')


@compliance_bp.route('/rules')
@login_required
@role_required('Auditor', 'Admin')
def rules():
    rules_list = ComplianceRule.query.order_by(ComplianceRule.name).all()
    return render_template('compliance/rules.html', rules=rules_list, title='Compliance Rules')


@compliance_bp.route('/rules/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def add_rule():
    form = RuleForm()
    if form.validate_on_submit():
        rule = ComplianceRule(
            name=form.name.data.strip(),
            category=form.category.data,
            rule_definition=form.rule_definition.data,
            is_active=form.is_active.data
        )
        db.session.add(rule)
        db.session.commit()
        flash('Rule created.', 'success')
        return redirect(url_for('compliance.rules'))
    return render_template('compliance/rule_form.html', form=form, title='Add Rule')


@compliance_bp.route('/product/<int:product_id>/run-checks', methods=['POST'])
@login_required
@role_required('Auditor', 'Admin')
def run_checks(product_id):
    product = Product.query.get_or_404(product_id)
    rules = ComplianceRule.query.filter_by(is_active=True).all()
    for rule in rules:
        # Simple automated checks
        result = 'pass'
        notes = 'Automated check passed.'
        if 'certificate' in (rule.rule_definition or '').lower() or 'cert' in (rule.name or '').lower():
            certs = Certificate.query.filter_by(product_id=product.id).all()
            if not certs:
                result = 'fail'
                notes = 'No certificates found for product.'
            else:
                expired = [c for c in certs if c.is_expired]
                if expired:
                    result = 'warning'
                    notes = f'{len(expired)} expired certificate(s).'
        check = ComplianceCheck(
            product_id=product.id,
            rule_id=rule.id,
            result=result,
            notes=notes,
            checked_by=current_user.id
        )
        db.session.add(check)
    db.session.commit()
    flash(f'Ran {len(rules)} compliance checks.', 'success')
    return redirect(url_for('compliance.product_review', product_id=product_id))


@compliance_bp.route('/product/<int:product_id>/review', methods=['GET', 'POST'])
@login_required
@role_required('Auditor', 'Admin')
def product_review(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()
    checks = product.compliance_checks.order_by(ComplianceCheck.checked_at.desc()).all()
    reviews = product.compliance_reviews.order_by(ComplianceReview.reviewed_at.desc()).all()
    certs = product.certificates.all()

    if form.validate_on_submit():
        review = ComplianceReview(
            product_id=product.id,
            reviewer_id=current_user.id,
            decision=form.decision.data,
            comments=form.comments.data
        )
        db.session.add(review)
        if form.decision.data == 'approved':
            product.compliance_status = 'compliant'
            product.status = 'published'
            product.published_at = datetime.utcnow()
        elif form.decision.data == 'rejected':
            product.compliance_status = 'non_compliant'
        else:
            product.compliance_status = 'under_review'
        db.session.commit()
        flash('Review submitted.', 'success')
        return redirect(url_for('compliance.product_review', product_id=product_id))

    return render_template('compliance/review.html', product=product, form=form,
                           checks=checks, reviews=reviews, certificates=certs, title='Compliance Review')


@compliance_bp.route('/queue')
@login_required
@role_required('Auditor', 'Admin')
def queue():
    products = Product.query.filter(
        Product.compliance_status.in_(['under_review', 'pending'])
    ).order_by(Product.updated_at.desc()).all()
    return render_template('compliance/queue.html', products=products, title='Compliance Queue')


@compliance_bp.route('/recalls')
@login_required
@role_required('Auditor', 'Admin', 'Manufacturer')
def recalls():
    items = Recall.query.order_by(Recall.issued_at.desc()).all()
    return render_template('compliance/recalls.html', recalls=items, title='Recalls')


@compliance_bp.route('/recalls/issue', methods=['GET', 'POST'])
@login_required
@role_required('Auditor', 'Admin', 'Manufacturer')
def issue_recall():
    from app.compliance.forms import RecallForm
    from app.models import Recall, ProductBatch
    form = RecallForm()
    form.product_id.choices = [
        (p.id, f'{p.passport_code} — {p.name}') for p in Product.query.order_by(Product.name).all()
    ]
    form.batch_id.choices = [(0, '— All batches —')] + [
        (b.id, f'{b.batch_no} (Product #{b.product_id})') for b in ProductBatch.query.all()
    ]
    if form.validate_on_submit():
        recall = Recall(
            product_id=form.product_id.data,
            batch_id=form.batch_id.data if form.batch_id.data else None,
            reason=form.reason.data.strip(),
            severity=form.severity.data,
            status='open',
            issued_by=current_user.id
        )
        db.session.add(recall)
        product = Product.query.get(form.product_id.data)
        if product:
            evt = SupplyChainEvent(
                product_id=product.id,
                batch_id=recall.batch_id,
                event_type='recall',
                event_date=datetime.utcnow(),
                notes=form.reason.data.strip()[:200],
                recorded_by=current_user.id
            )
            db.session.add(evt)
        db.session.commit()
        flash('Recall issued.', 'warning')
        return redirect(url_for('compliance.recalls'))
    return render_template('compliance/recall_form.html', form=form, title='Issue Recall')


@compliance_bp.route('/recalls/<int:id>/close', methods=['POST'])
@login_required
@role_required('Auditor', 'Admin')
def close_recall(id):
    from app.models import Recall
    recall = Recall.query.get_or_404(id)
    recall.status = 'closed'
    recall.closed_at = datetime.utcnow()
    db.session.commit()
    flash('Recall closed.', 'success')
    return redirect(url_for('compliance.recalls'))
