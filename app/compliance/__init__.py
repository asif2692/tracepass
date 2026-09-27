from flask import Blueprint
compliance_bp = Blueprint('compliance', __name__)
from app.compliance import routes  # noqa
