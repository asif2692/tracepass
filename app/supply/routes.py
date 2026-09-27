from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.supply import supply_bp
from app.supply.forms import EventForm, ShipmentForm
from app.decorators import role_required
from app.models import Product, ProductBatch, SupplyChainEvent, Shipment, Organization


@supply_bp.route('/product/<int:product_id>/events')
@login_required
def events(product_id):
    product = Product.query.get_or_404(product_id)
    events_list = product.events.order_by(SupplyChainEvent.event_date.desc()).all()
    return render_template('supply/events.html', product=product, events=events_list, title='Supply Chain Events')


@supply_bp.route('/product/<int:product_id>/events/add', methods=['GET', 'POST'])
@login_required
@role_required('Manufacturer', 'Distributor', 'Supplier', 'Admin')
def add_event(product_id):
    product = Product.query.get_or_404(product_id)
    form = EventForm()
    form.organization_id.choices = [(0, '— None —')] + [
        (o.id, o.name) for o in Organization.query.filter_by(is_active=True).order_by(Organization.name).all()
    ]
    form.batch_id.choices = [(0, '— None —')] + [
        (b.id, b.batch_no) for b in product.batches.all()
    ]
    if form.validate_on_submit():
        event = SupplyChainEvent(
            product_id=product.id,
            batch_id=form.batch_id.data if form.batch_id.data else None,
            event_type=form.event_type.data,
            event_date=datetime.combine(form.event_date.data, datetime.min.time()) if form.event_date.data else datetime.utcnow(),
            location=form.location.data,
            organization_id=form.organization_id.data if form.organization_id.data else None,
            reference_no=form.reference_no.data,
            notes=form.notes.data,
            recorded_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Supply-chain event recorded.', 'success')
        return redirect(url_for('supply.events', product_id=product_id))
    return render_template('supply/event_form.html', form=form, product=product, title='Add Event')


@supply_bp.route('/product/<int:product_id>/shipments', methods=['GET', 'POST'])
@login_required
@role_required('Manufacturer', 'Distributor', 'Admin')
def shipments(product_id):
    product = Product.query.get_or_404(product_id)
    form = ShipmentForm()
    orgs = [(o.id, o.name) for o in Organization.query.filter_by(is_active=True).order_by(Organization.name).all()]
    form.from_org_id.choices = orgs
    form.to_org_id.choices = orgs
    form.batch_id.choices = [(0, '— None —')] + [(b.id, b.batch_no) for b in product.batches.all()]

    if form.validate_on_submit():
        ship = Shipment(
            product_id=product.id,
            batch_id=form.batch_id.data if form.batch_id.data else None,
            from_org_id=form.from_org_id.data,
            to_org_id=form.to_org_id.data,
            shipped_date=form.shipped_date.data,
            received_date=form.received_date.data,
            status=form.status.data,
            tracking_no=form.tracking_no.data,
            notes=form.notes.data
        )
        db.session.add(ship)
        # Also create a supply-chain event
        evt = SupplyChainEvent(
            product_id=product.id,
            batch_id=ship.batch_id,
            event_type='shipment',
            event_date=datetime.utcnow(),
            organization_id=ship.from_org_id,
            reference_no=ship.tracking_no,
            notes=f'Shipment to org #{ship.to_org_id}',
            recorded_by=current_user.id
        )
        db.session.add(evt)
        db.session.commit()
        flash('Shipment recorded.', 'success')
        return redirect(url_for('supply.shipments', product_id=product_id))

    shipments_list = Shipment.query.filter_by(product_id=product.id).order_by(Shipment.created_at.desc()).all()
    return render_template('supply/shipments.html', product=product, form=form,
                           shipments=shipments_list, title='Shipments')


@supply_bp.route('/timeline/<int:product_id>')
@login_required
def timeline(product_id):
    product = Product.query.get_or_404(product_id)
    events = product.events.order_by(SupplyChainEvent.event_date.asc()).all()
    return render_template('supply/timeline.html', product=product, events=events, title='Product Timeline')
