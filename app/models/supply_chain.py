from datetime import datetime
from app import db


class SupplyChainEvent(db.Model):
    __tablename__ = 'supply_chain_events'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'), nullable=True)
    event_type = db.Column(db.String(50), nullable=False)  # sourcing, processing, manufacturing, shipment, receipt, sale, recall
    event_date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(150))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    reference_no = db.Column(db.String(80))
    notes = db.Column(db.Text)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organization = db.relationship('Organization', foreign_keys=[organization_id])
    recorder = db.relationship('User', foreign_keys=[recorded_by])
    batch = db.relationship('ProductBatch', foreign_keys=[batch_id])

    def __repr__(self):
        return f'<Event {self.event_type} {self.event_date}>'


class Shipment(db.Model):
    __tablename__ = 'shipments'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'))
    from_org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    to_org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    shipped_date = db.Column(db.Date)
    received_date = db.Column(db.Date)
    status = db.Column(db.String(30), default='pending')  # pending, in_transit, received, cancelled
    tracking_no = db.Column(db.String(80))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='shipments')
    from_org = db.relationship('Organization', foreign_keys=[from_org_id])
    to_org = db.relationship('Organization', foreign_keys=[to_org_id])
    batch = db.relationship('ProductBatch', foreign_keys=[batch_id])
