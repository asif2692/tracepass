"""
TracePass REST API
Base URL: /api/v1
Auth: session cookie (same as web) OR X-API-Key header for simple demos.
"""
from functools import wraps
from flask import jsonify, request, g
from flask_login import current_user, login_user
from app import db
from app.api import api_bp
from app.models import (
    User, Product, ProductBatch, Organization, Certificate,
    SupplyChainEvent, ComplianceRule, ComplianceCheck, Role
)


def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        # Optional: email/password via Basic-style JSON body for token-less demo
        auth = request.authorization
        if auth and auth.username and auth.password:
            user = User.query.filter_by(email=auth.username.lower()).first()
            if user and user.verify_password(auth.password) and user.is_active:
                login_user(user)
                return f(*args, **kwargs)
        return jsonify({'error': 'Unauthorized', 'message': 'Login required'}), 401
    return decorated


def api_role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Unauthorized'}), 401
            if not current_user.has_role(*roles):
                return jsonify({'error': 'Forbidden', 'message': f'Requires one of: {", ".join(roles)}'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ---------- Health ----------
@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'TracePass API', 'version': '1.0'})


# ---------- Auth ----------
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').lower().strip()
    password = data.get('password') or ''
    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password) or not user.is_active:
        return jsonify({'error': 'Invalid credentials'}), 401
    login_user(user)
    return jsonify({
        'message': 'Logged in',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role.name if user.role else None
        }
    })


@api_bp.route('/auth/me')
@api_login_required
def api_me():
    u = current_user
    return jsonify({
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'role': u.role.name if u.role else None,
        'organization_id': u.organization_id,
        'is_active': u.is_active
    })


# ---------- Products ----------
@api_bp.route('/products')
@api_login_required
def api_products():
    q = request.args.get('q', '').strip()
    status = request.args.get('status')
    query = Product.query
    if q:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{q}%'),
                Product.passport_code.ilike(f'%{q}%'),
                Product.category.ilike(f'%{q}%')
            )
        )
    if status:
        query = query.filter_by(status=status)
    products = query.order_by(Product.created_at.desc()).limit(100).all()
    return jsonify({
        'count': len(products),
        'products': [_product_dict(p) for p in products]
    })


@api_bp.route('/products/<int:id>')
@api_login_required
def api_product_detail(id):
    p = Product.query.get_or_404(id)
    return jsonify(_product_dict(p, detail=True))


@api_bp.route('/products', methods=['POST'])
@api_login_required
@api_role_required('Manufacturer', 'Admin')
def api_create_product():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    org_id = data.get('manufacturer_org_id') or current_user.organization_id
    if not org_id:
        return jsonify({'error': 'manufacturer_org_id required'}), 400
    p = Product(
        passport_code=Product.generate_passport_code(),
        name=name,
        category=data.get('category'),
        brand=data.get('brand'),
        model=data.get('model'),
        description=data.get('description'),
        manufacturer_org_id=org_id,
        origin_country=data.get('origin_country'),
        status='draft',
        compliance_status='pending',
        created_by=current_user.id
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(_product_dict(p)), 201


# ---------- Public passport (no auth) ----------
@api_bp.route('/public/passport/<passport_code>')
def api_public_passport(passport_code):
    p = Product.query.filter_by(passport_code=passport_code.upper(), status='published').first()
    if not p:
        return jsonify({'error': 'Passport not found or not published'}), 404
    events = p.events.order_by(SupplyChainEvent.event_date.asc()).limit(50).all()
    certs = [c for c in p.certificates.all() if c.verification_status != 'rejected']
    return jsonify({
        'passport_code': p.passport_code,
        'name': p.name,
        'category': p.category,
        'brand': p.brand,
        'model': p.model,
        'description': p.description,
        'origin_country': p.origin_country,
        'compliance_status': p.compliance_status,
        'manufacturer': p.manufacturer.name if p.manufacturer else None,
        'published_at': p.published_at.isoformat() if p.published_at else None,
        'batches': [
            {'batch_no': b.batch_no, 'manufacture_date': str(b.manufacture_date) if b.manufacture_date else None,
             'location': b.production_location, 'quantity': b.quantity, 'unit': b.unit}
            for b in p.batches.all()
        ],
        'materials': [
            {
                'name': m.material.name if m.material else None,
                'percentage': m.percentage,
                'supplier': m.supplier.name if m.supplier else None
            } for m in p.materials.all()
        ],
        'certificates': [
            {
                'type': c.cert_type, 'issuer': c.issuer,
                'issue_date': str(c.issue_date) if c.issue_date else None,
                'expiry_date': str(c.expiry_date) if c.expiry_date else None,
                'expired': c.is_expired
            } for c in certs
        ],
        'events': [
            {
                'type': e.event_type,
                'date': e.event_date.isoformat() if e.event_date else None,
                'location': e.location,
                'organization': e.organization.name if e.organization else None
            } for e in events
        ]
    })


@api_bp.route('/public/verify')
def api_verify():
    code = (request.args.get('code') or '').strip().upper()
    if not code:
        return jsonify({'error': 'code query parameter required'}), 400
    p = Product.query.filter_by(passport_code=code, status='published').first()
    if not p:
        return jsonify({'valid': False, 'code': code})
    return jsonify({
        'valid': True,
        'code': code,
        'name': p.name,
        'compliance_status': p.compliance_status,
        'passport_url': f'/public/passport/{p.passport_code}'
    })


# ---------- Organizations ----------
@api_bp.route('/organizations')
@api_login_required
def api_organizations():
    orgs = Organization.query.filter_by(is_active=True).order_by(Organization.name).all()
    return jsonify({
        'count': len(orgs),
        'organizations': [
            {'id': o.id, 'name': o.name, 'type': o.type, 'is_verified': o.is_verified}
            for o in orgs
        ]
    })


# ---------- Compliance ----------
@api_bp.route('/compliance/rules')
@api_login_required
@api_role_required('Auditor', 'Admin')
def api_rules():
    rules = ComplianceRule.query.filter_by(is_active=True).all()
    return jsonify({
        'rules': [
            {'id': r.id, 'name': r.name, 'category': r.category, 'definition': r.rule_definition}
            for r in rules
        ]
    })


@api_bp.route('/products/<int:id>/checks')
@api_login_required
@api_role_required('Auditor', 'Admin', 'Manufacturer')
def api_product_checks(id):
    p = Product.query.get_or_404(id)
    checks = p.compliance_checks.order_by(ComplianceCheck.checked_at.desc()).all()
    return jsonify({
        'product_id': p.id,
        'checks': [
            {
                'id': c.id,
                'rule': c.rule.name if c.rule else None,
                'result': c.result,
                'notes': c.notes,
                'checked_at': c.checked_at.isoformat() if c.checked_at else None
            } for c in checks
        ]
    })


def _product_dict(p, detail=False):
    d = {
        'id': p.id,
        'passport_code': p.passport_code,
        'name': p.name,
        'category': p.category,
        'brand': p.brand,
        'status': p.status,
        'compliance_status': p.compliance_status,
        'origin_country': p.origin_country,
        'manufacturer': p.manufacturer.name if p.manufacturer else None,
        'created_at': p.created_at.isoformat() if p.created_at else None
    }
    if detail:
        d['model'] = p.model
        d['description'] = p.description
        d['published_at'] = p.published_at.isoformat() if p.published_at else None
        d['batches_count'] = p.batches.count()
        d['materials_count'] = p.materials.count()
        d['events_count'] = p.events.count()
    return d
