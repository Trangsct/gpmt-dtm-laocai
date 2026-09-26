"""Ứng dụng quản lý GPMT và báo cáo ĐTM — Sở Nông nghiệp và Môi trường tỉnh Lào Cai."""
from flask import Flask

from .config import Config
from .extensions import db, login_manager


def create_app(cau_hinh=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if cau_hinh:
        app.config.update(cau_hinh)

    db.init_app(app)
    login_manager.init_app(app)

    from . import models  # noqa: F401  (đăng ký bảng)
    from .nhat_ky import dang_ky_nhat_ky
    dang_ky_nhat_ky()

    from .auth import bp as auth_bp, dang_ky_csrf
    from .views import dang_ky_views
    app.register_blueprint(auth_bp)
    dang_ky_views(app)
    dang_ky_csrf(app)

    from .cli import dang_ky_lenh
    dang_ky_lenh(app)

    if app.config.get("KHOI_TAO_TU_DONG", True):
        from .dich_vu import khoi_tao_tu_dong
        khoi_tao_tu_dong(app)
    return app
