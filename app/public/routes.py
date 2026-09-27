from flask import render_template, request, abort
from app.public import public_bp
from app.models import Product, SupplyChainEvent, Certificate


@public_bp.route('/passport/<passport_code>')
def passport(passport_code):
    """Public product passport view — only published products."""
    product = Product.query.filter_by(passport_code=passport_code.upper()).first_or_404()
    if product.status != 'published':
        abort(404)
    events = product.events.order_by(SupplyChainEvent.event_date.asc()).limit(20).all()
    certs = [c for c in product.certificates.all() if c.verification_status != 'rejected']
    materials = product.materials.all()
    batches = product.batches.all()
    return render_template(
        'public/passport.html',
        product=product,
        events=events,
        certificates=certs,
        materials=materials,
        batches=batches,
        title=f'Passport {product.passport_code}'
    )


@public_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """Public verify page — enter passport code or scan QR."""
    product = None
    code = request.values.get('code', '').strip().upper()
    if code:
        product = Product.query.filter_by(passport_code=code, status='published').first()
    return render_template('public/verify.html', product=product, code=code, title='Verify Passport')
