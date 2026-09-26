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

from flask import (Blueprint, abort, current_app, flash, redirect, render_template, request, session,
                   url_for)
from flask_login import AnonymousUserMixin, current_user, login_required, login_user, logout_user

from .extensions import db, login_manager
from .models import TaiKhoan

bp = Blueprint("auth", __name__)


@login_manager.user_loader
def _nap_nguoi_dung(uid):
    return db.session.get(TaiKhoan, int(uid))


class KhachXem(AnonymousUserMixin):
    """Người dân, doanh nghiệp xem không đăng nhập (Bạn chốt 27/9/2026: dữ liệu GPMT cần công khai).
    Quyền như tài khoản 'xem giới hạn' không giới hạn phạm vi: không sửa, không thấy thông tin nội bộ."""
    id = None
    ho_ten = "Khách"
    vai_tro = "khach"
    pham_vi_xa = None
    pham_vi_kcn = False
    duoc_sua = False
    noi_bo = False


login_manager.anonymous_user = KhachXem


def can_xem(f):
    """Trang xem dữ liệu: công khai khi CONG_KHAI bật (mặc định), ngược lại phải đăng nhập."""
    @wraps(f)
    def boc(*a, **kw):
        if not current_app.config.get("CONG_KHAI", True) and not current_user.is_authenticated:
            return login_manager.unauthorized()
        return f(*a, **kw)
    return boc


def _chua_dang_nhap_thi_moi():
    """Chưa đăng nhập mà vào trang cần quyền → mời đăng nhập thay vì báo 403."""
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    abort(403)


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
            return _chua_dang_nhap_thi_moi()
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
    if chua_co_tai_khoan():
        return redirect(url_for("auth.cai_dat"))
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


def chua_co_tai_khoan():
    return db.session.query(TaiKhoan.id).first() is None


@bp.route("/cai-dat", methods=["GET", "POST"])
def cai_dat():
    """Tạo tài khoản quản trị đầu tiên ngay trên trang web — chỉ mở khi CSDL chưa có tài khoản nào.
    Có tài khoản rồi thì trang tự khóa (chuyển về đăng nhập)."""
    if not chua_co_tai_khoan():
        return redirect(url_for("auth.dang_nhap"))
    if request.method == "POST":
        f = request.form
        ho_ten, email = f.get("ho_ten", "").strip(), f.get("email", "").strip().lower()
        mk, mk2 = f.get("mat_khau", ""), f.get("mat_khau_2", "")
        loi = []
        if not ho_ten:
            loi.append("Chưa nhập họ tên.")
        if "@" not in email:
            loi.append("Email không hợp lệ.")
        if len(mk) < 10:
            loi.append("Mật khẩu phải có ít nhất 10 ký tự.")
        elif mk != mk2:
            loi.append("Hai lần nhập mật khẩu không khớp.")
        if not loi:
            tk = TaiKhoan(ho_ten=ho_ten, email=email, vai_tro="quan_tri", hoat_dong=True)
            tk.dat_mat_khau(mk)
            db.session.add(tk)
            db.session.commit()
            session.clear()
            login_user(tk)
            flash("Đã tạo tài khoản quản trị và đăng nhập. Bước tiếp theo: menu Nhập dữ liệu → tải sổ Excel lên.", "ok")
            return redirect(url_for("nhap_du_lieu.trang_chinh"))
        for x in loi:
            flash(x, "loi")
    return render_template("cai_dat.html")


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
