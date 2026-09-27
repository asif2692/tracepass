from flask import Blueprint
supply_bp = Blueprint('supply', __name__)
from app.supply import routes  # noqa
