"""
Seed script – Admin user, demo org, materials, compliance rules, sample product.
Run: python seed.py
"""
from datetime import date, timedelta
from app import create_app, db
from app.models import (
    User, Role, Organization, Product, ProductBatch, Material, ProductMaterial,
    ComplianceRule, Certificate, SupplyChainEvent
)

app = create_app()

with app.app_context():
    Role.insert_roles()

    org = Organization.query.filter_by(name='TracePass Demo Corp').first()
    if not org:
        org = Organization(
            name='TracePass Demo Corp',
            type='manufacturer',
            registration_no='TP-DEMO-001',
            contact_email='demo@tracepass.com',
            contact_phone='+92-300-0000000',
            address='Demo Street, Karachi',
            country='Pakistan',
            is_verified=True,
            is_active=True
        )
        db.session.add(org)
        db.session.commit()
        print(f'Created organization: {org.name}')

    supplier_org = Organization.query.filter_by(name='Green Materials Ltd').first()
    if not supplier_org:
        supplier_org = Organization(
            name='Green Materials Ltd',
            type='supplier',
            registration_no='SUP-001',
            contact_email='supply@greenmaterials.com',
            country='Pakistan',
            is_verified=True,
            is_active=True
        )
        db.session.add(supplier_org)
        db.session.commit()
        print(f'Created supplier: {supplier_org.name}')

    admin_role = Role.query.filter_by(name='Admin').first()
    mfr_role = Role.query.filter_by(name='Manufacturer').first()
    auditor_role = Role.query.filter_by(name='Auditor').first()

    admin = User.query.filter_by(email='admin@tracepass.com').first()
    if not admin:
        admin = User(
            name='System Admin',
            email='admin@tracepass.com',
            role_id=admin_role.id,
            organization_id=org.id,
            is_active=True
        )
        admin.password = 'Admin@123'
        db.session.add(admin)
        db.session.commit()
        print('Created admin: admin@tracepass.com / Admin@123')

    mfr = User.query.filter_by(email='manufacturer@tracepass.com').first()
    if not mfr:
        mfr = User(
            name='Demo Manufacturer',
            email='manufacturer@tracepass.com',
            role_id=mfr_role.id,
            organization_id=org.id,
            is_active=True
        )
        mfr.password = 'Mfr@12345'
        db.session.add(mfr)
        db.session.commit()
        print('Created manufacturer: manufacturer@tracepass.com / Mfr@12345')

    auditor = User.query.filter_by(email='auditor@tracepass.com').first()
    if not auditor:
        auditor = User(
            name='Demo Auditor',
            email='auditor@tracepass.com',
            role_id=auditor_role.id,
            organization_id=org.id,
            is_active=True
        )
        auditor.password = 'Audit@123'
        db.session.add(auditor)
        db.session.commit()
        print('Created auditor: auditor@tracepass.com / Audit@123')

    # Materials
    if Material.query.count() == 0:
        mats = [
            Material(name='Organic Cotton', category='Textile', origin_country='Pakistan'),
            Material(name='Recycled Polyester', category='Textile', origin_country='China'),
            Material(name='Natural Rubber', category='Polymer', origin_country='Malaysia'),
        ]
        db.session.add_all(mats)
        db.session.commit()
        print('Created sample materials')

    # Compliance rules
    if ComplianceRule.query.count() == 0:
        rules = [
            ComplianceRule(
                name='Valid Certificate Required',
                category='Documentation',
                rule_definition='Product must have at least one non-expired certificate.',
                is_active=True
            ),
            ComplianceRule(
                name='Manufacturer Verified',
                category='Organization',
                rule_definition='Manufacturer organization must be verified.',
                is_active=True
            ),
            ComplianceRule(
                name='Origin Declared',
                category='Traceability',
                rule_definition='Origin country must be specified on the product passport.',
                is_active=True
            ),
        ]
        db.session.add_all(rules)
        db.session.commit()
        print('Created compliance rules')

    # Sample product
    if Product.query.count() == 0:
        product = Product(
            passport_code=Product.generate_passport_code(),
            name='Eco Cotton T-Shirt',
            category='Apparel',
            brand='GreenWear',
            model='GW-TS-01',
            description='Sustainable cotton t-shirt with full supply-chain passport.',
            manufacturer_org_id=org.id,
            origin_country='Pakistan',
            status='published',
            compliance_status='compliant',
            created_by=admin.id,
            published_at=__import__('datetime').datetime.utcnow()
        )
        db.session.add(product)
        db.session.flush()

        batch = ProductBatch(
            product_id=product.id,
            batch_no='BATCH-2026-001',
            manufacture_date=date.today() - timedelta(days=30),
            production_location='Karachi Plant',
            quantity=5000,
            unit='units'
        )
        db.session.add(batch)

        cotton = Material.query.filter_by(name='Organic Cotton').first()
        if cotton:
            db.session.add(ProductMaterial(
                product_id=product.id,
                material_id=cotton.id,
                supplier_org_id=supplier_org.id,
                percentage=95,
                unit='%'
            ))

        cert = Certificate(
            organization_id=org.id,
            product_id=product.id,
            cert_type='GOTS Organic',
            issuer='Control Union',
            issue_date=date.today() - timedelta(days=90),
            expiry_date=date.today() + timedelta(days=275),
            verification_status='verified',
            uploaded_by=admin.id
        )
        db.session.add(cert)

        db.session.add(SupplyChainEvent(
            product_id=product.id,
            event_type='sourcing',
            location='Punjab, Pakistan',
            organization_id=supplier_org.id,
            notes='Organic cotton sourced',
            recorded_by=admin.id
        ))
        db.session.add(SupplyChainEvent(
            product_id=product.id,
            event_type='manufacturing',
            location='Karachi Plant',
            organization_id=org.id,
            notes='Cut and sew completed',
            recorded_by=admin.id
        ))
        db.session.commit()
        print(f'Created sample product: {product.passport_code} — {product.name}')

    print('Seed completed successfully.')
