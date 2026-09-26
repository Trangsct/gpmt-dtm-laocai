from datetime import date, datetime

from flask import render_template

from ..models import VAI_TRO
from ..trang_thai import DS_TRANG_THAI, MAU_TRANG_THAI


def dinh_dang_ngay(v):
    if isinstance(v, (date, datetime)):
        return v.strftime("%d/%m/%Y")
    return v or ""


def dinh_dang_so(v):
    """1949.5 → '1.949,5' (kiểu Việt)."""
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        v = int(v)
    s = f"{v:,}" if isinstance(v, int) else f"{v:,.3f}".rstrip("0").rstrip(".")
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def dang_ky_views(app):
    from . import danh_muc, gpmt, main, nhap_du_lieu, tai_khoan
    for bp in (main.bp, gpmt.bp, danh_muc.bp, tai_khoan.bp, nhap_du_lieu.bp):
        app.register_blueprint(bp)

    app.jinja_env.filters["ngay"] = dinh_dang_ngay
    app.jinja_env.filters["so"] = dinh_dang_so
    from .bieu_mau import hien_thi
    app.jinja_env.globals["hien_thi"] = hien_thi

    @app.context_processor
    def _bien_chung():
        return dict(TEN_DON_VI=app.config["TEN_DON_VI"], VAI_TRO=VAI_TRO, MAU_TRANG_THAI=MAU_TRANG_THAI,
                    DS_TRANG_THAI=DS_TRANG_THAI, hom_nay=date.today())

    @app.errorhandler(401)
    def _moi_dang_nhap(e):
        from flask import redirect, request, url_for
        return redirect(url_for("auth.dang_nhap", next=request.full_path.rstrip("?")))

    @app.errorhandler(403)
    def _cam(e):
        return render_template("loi.html", ma=403, thong_bao="Tài khoản không có quyền thực hiện việc này."), 403

    @app.errorhandler(404)
    def _khong_thay(e):
        return render_template("loi.html", ma=404, thong_bao="Không tìm thấy trang hoặc bản ghi."), 404

    @app.errorhandler(500)
    def _loi_may_chu(e):
        # Trang độc lập, không đụng CSDL (lỗi thường do CSDL chưa nối được)
        from ..extensions import db
        try:
            db.session.rollback()
        except Exception:
            pass
        return render_template("loi_500.html"), 500

    @app.errorhandler(400)
    def _sai(e):
        return render_template("loi.html", ma=400, thong_bao=getattr(e, "description", "Yêu cầu không hợp lệ.")), 400
