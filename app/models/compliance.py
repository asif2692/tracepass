from datetime import datetime
from app import db


class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    cert_type = db.Column(db.String(100), nullable=False)
    issuer = db.Column(db.String(150))
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    file_path = db.Column(db.String(255))
    verification_status = db.Column(db.String(30), default='pending')  # pending, verified, rejected
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organization = db.relationship('Organization', foreign_keys=[organization_id])
    uploader = db.relationship('User', foreign_keys=[uploaded_by])

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < datetime.utcnow().date()
        return False

    def __repr__(self):
        return f'<Certificate {self.cert_type}>'


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    owner_type = db.Column(db.String(50))  # product, organization, certificate
    owner_id = db.Column(db.Integer)
    file_path = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(200))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploader = db.relationship('User', foreign_keys=[uploaded_by])


class ComplianceRule(db.Model):
    __tablename__ = 'compliance_rules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80))
    rule_definition = db.Column(db.Text)  # description / JSON-like text
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requirements = db.relationship('ComplianceRequirement', backref='rule', lazy='dynamic', cascade='all, delete-orphan')
    checks = db.relationship('ComplianceCheck', backref='rule', lazy='dynamic')

    def __repr__(self):
        return f'<Rule {self.name}>'


class ComplianceRequirement(db.Model):
    __tablename__ = 'compliance_requirements'

    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('compliance_rules.id'), nullable=False)
    product_category = db.Column(db.String(100))
    mandatory_evidence_type = db.Column(db.String(100))


class ComplianceCheck(db.Model):
    __tablename__ = 'compliance_checks'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('compliance_rules.id'), nullable=False)
    result = db.Column(db.String(30), default='pending')  # pass, fail, pending, warning
    notes = db.Column(db.Text)
    checked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)

    checker = db.relationship('User', foreign_keys=[checked_by])


class ComplianceReview(db.Model):
    __tablename__ = 'compliance_reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    decision = db.Column(db.String(30), nullable=False)  # approved, rejected, request_correction
    comments = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviewer = db.relationship('User', foreign_keys=[reviewer_id])


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])


class Recall(db.Model):
    __tablename__ = 'recalls'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(30), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(30), default='open')  # open, in_progress, closed
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)

    product = db.relationship('Product', backref='recalls')
    batch = db.relationship('ProductBatch', foreign_keys=[batch_id])
    issuer = db.relationship('User', foreign_keys=[issued_by])
