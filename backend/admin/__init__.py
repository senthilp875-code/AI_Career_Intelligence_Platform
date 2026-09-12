from flask import Blueprint

from admin.schema import ensure_admin_schema
from admin.routes import register_routes


def create_admin_blueprint(upload_folder):
    bp = Blueprint("admin", __name__, url_prefix="/admin")
    register_routes(bp, upload_folder)
    return bp


def init_admin(app):
    ensure_admin_schema()
    app.register_blueprint(create_admin_blueprint(app.config.get("UPLOAD_FOLDER", "uploads")))
