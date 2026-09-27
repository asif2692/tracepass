from datetime import datetime
from app import db


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Integer, default=0)  # bitmask style if needed later
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='role', lazy='dynamic')

    # Permission constants (can be expanded)
    PERMISSION_VIEW_PUBLIC = 0x01
    PERMISSION_MANAGE_PRODUCTS = 0x02
    PERMISSION_MANAGE_SUPPLIERS = 0x04
    PERMISSION_COMPLIANCE = 0x08
    PERMISSION_ADMIN = 0x80

    def __repr__(self):
        return f'<Role {self.name}>'

    def has_permission(self, perm):
        return (self.permissions & perm) == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    @staticmethod
    def insert_roles():
        """Seed the fixed set of roles required by TracePass."""
        roles = {
            'Customer': {
                'description': 'Public / end customer – view product passports',
                'permissions': Role.PERMISSION_VIEW_PUBLIC,
                'is_default': True
            },
            'Supplier': {
                'description': 'Supplier organization – materials & certificates',
                'permissions': Role.PERMISSION_VIEW_PUBLIC | Role.PERMISSION_MANAGE_SUPPLIERS,
                'is_default': False
            },
            'Manufacturer': {
                'description': 'Manufacturer – create product passports & batches',
                'permissions': (Role.PERMISSION_VIEW_PUBLIC |
                                Role.PERMISSION_MANAGE_PRODUCTS |
                                Role.PERMISSION_MANAGE_SUPPLIERS),
                'is_default': False
            },
            'Distributor': {
                'description': 'Distributor / Retailer – record transfers & shipments',
                'permissions': Role.PERMISSION_VIEW_PUBLIC | Role.PERMISSION_MANAGE_PRODUCTS,
                'is_default': False
            },
            'Auditor': {
                'description': 'Compliance Officer / Auditor – review & approve',
                'permissions': (Role.PERMISSION_VIEW_PUBLIC |
                                Role.PERMISSION_COMPLIANCE |
                                Role.PERMISSION_MANAGE_PRODUCTS),
                'is_default': False
            },
            'Admin': {
                'description': 'System Administrator – full access',
                'permissions': 0xff,  # all permissions
                'is_default': False
            },
        }

        for role_name, data in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            role.description = data['description']
            role.reset_permissions()
            role.add_permission(data['permissions'])
            role.is_default = data['is_default']
            db.session.add(role)
        db.session.commit()