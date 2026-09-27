from datetime import datetime
from app import db


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)  # supplier, manufacturer, distributor, auditor, other
    registration_no = db.Column(db.String(100), unique=True)
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(30))
    address = db.Column(db.Text)
    country = db.Column(db.String(80))
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship('User', backref='organization', lazy='dynamic')

    def __repr__(self):
        return f'<Organization {self.name}>'

    @property
    def display_type(self):
        return self.type.replace('_', ' ').title() if self.type else ''