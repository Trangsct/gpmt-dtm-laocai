"""Đăng nhập, phân quyền, chống CSRF.

Vai trò (Bạn chốt 26/9/2026: người dùng gồm Sở, BQL các KCN và UBND xã):
- quan_tri: sửa dữ liệu + quản lý tài khoản
- bien_tap: sửa dữ liệu
- chi_xem: xem toàn bộ, kể cả thông tin nội bộ (hồ sơ đang giải quyết, ghi chú)
- ben_ngoai: BQL các KCN / UBND xã — chỉ xem GPMT, ĐTM, cơ sở; không thấy thông tin nội bộ;
  có thể giới hạn theo xã/phường hoặc chỉ cơ sở trong KCN/CCN.
Mặc định tài khoản mới chỉ được xem.
"""
import secrets
from functools import wraps
from urllib.parse import urlparse

from flask import (Blueprint, abort, flash, redirect, render_template, request, session,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from .extensions import db, login_manager
from .models import TaiKhoan

bp = Blueprint("auth", __name__)


@login_manager.user_loader
def _nap_nguoi_dung(uid):
    return db.session.get(TaiKhoan, int(uid))


def can_quyen_sua(f):
    @wraps(f)
    @login_required
    def boc(*a, **kw):
        if not current_user.duoc_sua:
            abort(403)
        return f(*a, **kw)
    return boc


def can_noi_bo(f):
    @wraps(f)
    @login_required
    def boc(*a, **kw):
        if not current_user.noi_bo:
            abort(403)
        return f(*a, **kw)
    return boc


def can_quan_tri(f):
    @wraps(f)
    @login_required
    def boc(*a, **kw):
        if current_user.vai_tro != "quan_tri":
            abort(403)
        return f(*a, **kw)
    return boc


# ---------------------------------------------------------------- CSRF

def lay_csrf():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def dang_ky_csrf(app):
    app.jinja_env.globals["csrf_token"] = lay_csrf

    @app.before_request
    def _kiem_csrf():
        if request.method in ("POST", "PUT", "PATCH", "DELETE") and not app.config.get("TESTING_NO_CSRF"):
            gui = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
            if not gui or not secrets.compare_digest(gui, session.get("_csrf", "")):
                abort(400, "Phiên làm việc đã hết hạn, vui lòng tải lại trang.")


# ---------------------------------------------------------------- Trang đăng nhập

def _an_toan(dich):
    return dich and not urlparse(dich).netloc and dich.startswith("/")


@bp.route("/dang-nhap", methods=["GET", "POST"])
def dang_nhap():
    if current_user.is_authenticated:
        return redirect(url_for("main.bang_dieu_khien"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        tk = db.session.query(TaiKhoan).filter_by(email=email).first()
        if tk and tk.hoat_dong and tk.kiem_mat_khau(request.form.get("mat_khau", "")):
            session.clear()
            login_user(tk)
            dich = request.args.get("next")
            return redirect(dich if _an_toan(dich) else url_for("main.bang_dieu_khien"))
        flash("Email hoặc mật khẩu không đúng.", "loi")
    return render_template("dang_nhap.html")


@bp.route("/dang-xuat", methods=["POST"])
@login_required
def dang_xuat():
    logout_user()
    session.clear()
    return redirect(url_for("auth.dang_nhap"))


@bp.route("/doi-mat-khau", methods=["GET", "POST"])
@login_required
def doi_mat_khau():
    if request.method == "POST":
        cu, moi = request.form.get("mat_khau_cu", ""), request.form.get("mat_khau_moi", "")
        if not current_user.kiem_mat_khau(cu):
            flash("Mật khẩu cũ không đúng.", "loi")
        elif len(moi) < 10:
            flash("Mật khẩu mới phải có ít nhất 10 ký tự.", "loi")
        else:
            current_user.dat_mat_khau(moi)
            db.session.commit()
            flash("Đã đổi mật khẩu.", "ok")
            return redirect(url_for("main.bang_dieu_khien"))
    return render_template("doi_mat_khau.html")
