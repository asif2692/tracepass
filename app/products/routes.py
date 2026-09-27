from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.products import products_bp
from app.products.forms import ProductForm, BatchForm, MaterialForm, ProductMaterialForm
from app.decorators import role_required
from app.models import (
    Product, ProductBatch, Material, ProductMaterial, Organization, AuditLog
)


def log_action(action, entity_type=None, entity_id=None, details=None):
    try:
        entry = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()


@products_bp.route('/')
@login_required
@role_required('Manufacturer', 'Admin', 'Auditor', 'Distributor', 'Supplier')
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str)
    query = Product.query
    if q:
        query = query.filter(
            db.or_(Product.name.ilike(f'%{q}%'), Product.passport_code.ilike(f'%{q}%'),
                   Product.category.ilike(f'%{q}%'))
        )
    if current_user.has_role('Manufacturer') and current_user.organization_id:
        query = query.filter_by(manufacturer_org_id=current_user.organization_id)
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('products/index.html', products=pagination.items,
                           pagination=pagination, q=q, title='Products')


@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Manufacturer', 'Admin')
def create():
    form = ProductForm()
    form.manufacturer_org_id.choices = [
        (o.id, o.name) for o in Organization.query.filter_by(is_active=True).order_by(Organization.name).all()
    ]
    if current_user.organization_id:
        form.manufacturer_org_id.data = current_user.organization_id

    if form.validate_on_submit():
        product = Product(
            passport_code=Product.generate_passport_code(),
            name=form.name.data.strip(),
            category=form.category.data,
            brand=form.brand.data,
            model=form.model.data,
            description=form.description.data,
            manufacturer_org_id=form.manufacturer_org_id.data,
            origin_country=form.origin_country.data,
            status='draft',
            compliance_status='pending',
            created_by=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        log_action('create_product', 'product', product.id, product.passport_code)
        flash(f'Product created. Passport code: {product.passport_code}', 'success')
        return redirect(url_for('products.detail', id=product.id))
    return render_template('products/form.html', form=form, title='Create Product')


@products_bp.route('/<int:id>')
@login_required
def detail(id):
    product = Product.query.get_or_404(id)
    return render_template('products/detail.html', product=product, title=product.name)


@products_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Manufacturer', 'Admin')
def edit(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.manufacturer_org_id.choices = [
        (o.id, o.name) for o in Organization.query.filter_by(is_active=True).order_by(Organization.name).all()
    ]
    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.category = form.category.data
        product.brand = form.brand.data
        product.model = form.model.data
        product.description = form.description.data
        product.manufacturer_org_id = form.manufacturer_org_id.data
        product.origin_country = form.origin_country.data
        db.session.commit()
        log_action('edit_product', 'product', product.id)
        flash('Product updated.', 'success')
        return redirect(url_for('products.detail', id=product.id))
    return render_template('products/form.html', form=form, title='Edit Product', product=product)


@products_bp.route('/<int:id>/publish', methods=['POST'])
@login_required
@role_required('Manufacturer', 'Admin')
def publish(id):
    product = Product.query.get_or_404(id)
    if product.status == 'published':
        flash('Already published.', 'info')
        return redirect(url_for('products.detail', id=id))
    product.status = 'published'
    product.published_at = datetime.utcnow()
    db.session.commit()
    log_action('publish_product', 'product', product.id)
    flash('Product passport published. Public verification is now available.', 'success')
    return redirect(url_for('products.detail', id=id))


@products_bp.route('/<int:id>/submit-compliance', methods=['POST'])
@login_required
@role_required('Manufacturer', 'Admin')
def submit_compliance(id):
    product = Product.query.get_or_404(id)
    product.status = 'submitted'
    product.compliance_status = 'under_review'
    db.session.commit()
    log_action('submit_compliance', 'product', product.id)
    flash('Product submitted for compliance review.', 'success')
    return redirect(url_for('products.detail', id=id))


@products_bp.route('/<int:id>/batches', methods=['GET', 'POST'])
@login_required
@role_required('Manufacturer', 'Admin')
def batches(id):
    product = Product.query.get_or_404(id)
    form = BatchForm()
    if form.validate_on_submit():
        batch = ProductBatch(
            product_id=product.id,
            batch_no=form.batch_no.data.strip(),
            manufacture_date=form.manufacture_date.data,
            production_location=form.production_location.data,
            quantity=form.quantity.data,
            unit=form.unit.data or 'units'
        )
        db.session.add(batch)
        db.session.commit()
        flash('Batch added.', 'success')
        return redirect(url_for('products.batches', id=id))
    return render_template('products/batches.html', product=product, form=form,
                           batches=product.batches.all(), title='Batches')


@products_bp.route('/<int:id>/materials', methods=['GET', 'POST'])
@login_required
@role_required('Manufacturer', 'Admin', 'Supplier')
def materials(id):
    product = Product.query.get_or_404(id)
    form = ProductMaterialForm()
    form.material_id.choices = [(m.id, m.name) for m in Material.query.order_by(Material.name).all()]
    form.supplier_org_id.choices = [(0, '— None —')] + [
        (o.id, o.name) for o in Organization.query.filter(
            Organization.type.in_(['supplier', 'manufacturer'])
        ).order_by(Organization.name).all()
    ]
    if form.validate_on_submit():
        pm = ProductMaterial(
            product_id=product.id,
            material_id=form.material_id.data,
            supplier_org_id=form.supplier_org_id.data if form.supplier_org_id.data else None,
            quantity=form.quantity.data,
            percentage=form.percentage.data,
            unit=form.unit.data
        )
        db.session.add(pm)
        db.session.commit()
        flash('Material linked to product.', 'success')
        return redirect(url_for('products.materials', id=id))
    return render_template('products/materials.html', product=product, form=form,
                           materials=product.materials.all(), title='Product Materials')


@products_bp.route('/materials/catalog', methods=['GET', 'POST'])
@login_required
@role_required('Manufacturer', 'Admin', 'Supplier')
def material_catalog():
    form = MaterialForm()
    if form.validate_on_submit():
        m = Material(
            name=form.name.data.strip(),
            category=form.category.data,
            origin_country=form.origin_country.data,
            description=form.description.data
        )
        db.session.add(m)
        db.session.commit()
        flash('Material added to catalog.', 'success')
        return redirect(url_for('products.material_catalog'))
    materials = Material.query.order_by(Material.name).all()
    return render_template('products/material_catalog.html', form=form, materials=materials,
                           title='Material Catalog')


@products_bp.route('/<int:id>/pdf')
@login_required
def passport_pdf(id):
    from flask import send_file
    from app.products.pdf import build_passport_pdf
    product = Product.query.get_or_404(id)
    buf = build_passport_pdf(product)
    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{product.passport_code}_passport.pdf'
    )
