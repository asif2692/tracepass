from datetime import datetime
import uuid
from app import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    passport_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    description = db.Column(db.Text)
    manufacturer_org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    origin_country = db.Column(db.String(80))
    status = db.Column(db.String(30), default='draft')  # draft, submitted, published, archived
    compliance_status = db.Column(db.String(30), default='pending')  # pending, compliant, non_compliant, under_review
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)

    manufacturer = db.relationship('Organization', backref='products', foreign_keys=[manufacturer_org_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    batches = db.relationship('ProductBatch', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    materials = db.relationship('ProductMaterial', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    events = db.relationship('SupplyChainEvent', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='product', lazy='dynamic')
    compliance_checks = db.relationship('ComplianceCheck', backref='product', lazy='dynamic')
    compliance_reviews = db.relationship('ComplianceReview', backref='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.passport_code}>'

    @staticmethod
    def generate_passport_code():
        return f'TP-{uuid.uuid4().hex[:10].upper()}'

    @property
    def is_published(self):
        return self.status == 'published'


class ProductBatch(db.Model):
    __tablename__ = 'product_batches'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    batch_no = db.Column(db.String(80), nullable=False)
    manufacture_date = db.Column(db.Date)
    production_location = db.Column(db.String(150))
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(30), default='units')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Batch {self.batch_no}>'


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80))
    origin_country = db.Column(db.String(80))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Material {self.name}>'


class ProductMaterial(db.Model):
    __tablename__ = 'product_materials'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    supplier_org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    quantity = db.Column(db.Float)
    percentage = db.Column(db.Float)
    unit = db.Column(db.String(30))

    material = db.relationship('Material')
    supplier = db.relationship('Organization', foreign_keys=[supplier_org_id])


class Supplier(db.Model):
    """Legacy-compatible supplier link to organization."""
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    material_categories = db.Column(db.String(255))
    status = db.Column(db.String(30), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organization = db.relationship('Organization', backref='supplier_profile')
