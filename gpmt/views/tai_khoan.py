"""Quản lý tài khoản (chỉ quản trị). Không có trang tự đăng ký: tài khoản do quản trị cấp."""
import secrets

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..auth import can_quan_tri
from ..extensions import db
from ..models import VAI_TRO, TaiKhoan

bp = Blueprint("tai_khoan", __name__, url_prefix="/tai-khoan")


@bp.route("/")
@can_quan_tri
def danh_sach():
    return render_template("tai_khoan.html", ds=db.session.query(TaiKhoan).order_by(TaiKhoan.ho_ten).all(),
                           tk=None)


@bp.route("/moi", methods=["GET", "POST"])
@bp.route("/<int:id>", methods=["GET", "POST"])
@can_quan_tri
def sua(id=None):
    tk = db.get_or_404(TaiKhoan, id) if id else TaiKhoan(vai_tro="chi_xem", hoat_dong=True)
    if request.method == "POST":
        f = request.form
        email = f.get("email", "").strip().lower()
        loi = []
        if not email or "@" not in email:
            loi.append("Email không hợp lệ.")
        elif db.session.query(TaiKhoan).filter(TaiKhoan.email == email, TaiKhoan.id != (tk.id or 0)).first():
            loi.append("Email đã có tài khoản khác.")
        if not f.get("ho_ten", "").strip():
            loi.append("Chưa nhập họ tên.")
        if f.get("vai_tro") not in VAI_TRO:
            loi.append("Vai trò không hợp lệ.")
        if tk.id == current_user.id and f.get("vai_tro") != "quan_tri":
            loi.append("Không tự hạ quyền quản trị của chính mình.")
        if loi:
            for x in loi:
                flash(x, "loi")
        else:
            tk.email, tk.ho_ten, tk.vai_tro = email, f["ho_ten"].strip(), f["vai_tro"]
            tk.don_vi = f.get("don_vi", "").strip() or None
            tk.pham_vi_xa = f.get("pham_vi_xa", "").strip() or None
            tk.pham_vi_kcn = f.get("pham_vi_kcn") == "1"
            tk.hoat_dong = f.get("hoat_dong") == "1" or tk.id == current_user.id
            mk_moi = None
            if not tk.id or f.get("dat_lai_mk") == "1":
                mk_moi = secrets.token_urlsafe(9)
                tk.dat_mat_khau(mk_moi)
            db.session.add(tk)
            db.session.commit()
            if mk_moi:
                flash(f"Mật khẩu tạm của {tk.email}: {mk_moi} — gửi riêng cho người dùng và yêu cầu đổi ngay.", "ok")
            else:
                flash("Đã lưu tài khoản.", "ok")
            return redirect(url_for("tai_khoan.danh_sach"))
    return render_template("tai_khoan.html", ds=None, tk=tk)
