"""Cơ sở/dự án (trang dòng thời gian), chủ cơ sở, ĐTM, hồ sơ đang giải quyết, đăng ký môi trường."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..auth import can_quyen_sua
from ..extensions import db
from ..models import ChuThe, CoSoDuAn, DangKyMoiTruong, Dtm, HoSo
from .bieu_mau import BM_CHU_THE, BM_CO_SO, BM_DKMT, BM_DTM, BM_HO_SO
from .pham_vi import kiem_co_so, loc_co_so

bp = Blueprint("danh_muc", __name__)

# Bảng quản lý chung: khóa URL → (mô hình, biểu mẫu, tên, chỉ nội bộ?)
BANG = {
    "dtm": (Dtm, BM_DTM, "Quyết định phê duyệt ĐTM", False),
    "ho-so": (HoSo, BM_HO_SO, "Hồ sơ đang giải quyết", True),
    "dang-ky-mt": (DangKyMoiTruong, BM_DKMT, "Đăng ký môi trường", False),
    "chu-the": (ChuThe, BM_CHU_THE, "Chủ cơ sở", False),
}


@bp.route("/co-so")
@login_required
def ds_co_so():
    q = db.session.query(CoSoDuAn).outerjoin(ChuThe, CoSoDuAn.chu_the_id == ChuThe.id)
    q = loc_co_so(q)
    tu = (request.args.get("q") or "").strip()
    if tu:
        q = q.filter(or_(CoSoDuAn.ten.ilike(f"%{tu}%"), ChuThe.ten.ilike(f"%{tu}%"),
                         ChuThe.ma_so_thue.ilike(f"%{tu}%"), CoSoDuAn.xa_phuong_moi.ilike(f"%{tu}%"),
                         CoSoDuAn.kcn_ccn.ilike(f"%{tu}%")))
    return render_template("co_so_danh_sach.html", ds=q.order_by(CoSoDuAn.ten).all(), tu=tu)


@bp.route("/co-so/<int:id>")
@login_required
def co_so(id):
    cs = db.get_or_404(CoSoDuAn, id)
    kiem_co_so(cs)
    # Dòng thời gian: GPMT, ĐTM, ĐKMT, VHTN (và hồ sơ nếu nội bộ)
    su_kien = []
    for g in cs.gpmt:
        su_kien.append((g.ngay_ky, "GPMT", g, None))
        for v in g.vhtn:
            su_kien.append((v.bat_dau or g.ngay_ky, "VHTN", v, g))
    for d in cs.dtm:
        su_kien.append((d.ngay_qd, "ĐTM", d, None))
    for d in cs.dang_ky_mt:
        su_kien.append((d.ngay_tiep_nhan, "ĐKMT", d, None))
    if current_user.noi_bo:
        for h in cs.ho_so:
            su_kien.append((h.ngay_tiep_nhan, "Hồ sơ", h, None))
    thu_tu = {"Hồ sơ": 0, "ĐTM": 1, "GPMT": 2, "VHTN": 3, "ĐKMT": 4}
    su_kien.sort(key=lambda x: (x[0] is None, x[0] or 0, thu_tu[x[1]]))
    return render_template("co_so_chi_tiet.html", cs=cs, su_kien=su_kien)


@bp.route("/co-so/moi", methods=["GET", "POST"])
@bp.route("/co-so/<int:id>/sua", methods=["GET", "POST"])
@can_quyen_sua
def sua_co_so(id=None):
    cs = db.get_or_404(CoSoDuAn, id) if id else CoSoDuAn()
    if request.method == "POST":
        loi = BM_CO_SO.dien(cs, request.form)
        if not loi:
            db.session.add(cs)
            db.session.commit()
            flash("Đã lưu cơ sở/dự án.", "ok")
            return redirect(url_for("danh_muc.co_so", id=cs.id))
        db.session.rollback()
        for x in loi:
            flash(x, "loi")
    return render_template("bieu_mau.html", bm=BM_CO_SO, obj=cs,
                           tieu_de="Sửa cơ sở/dự án" if id else "Thêm cơ sở/dự án",
                           quay_lai=url_for("danh_muc.co_so", id=id) if id else url_for("danh_muc.ds_co_so"))


# ---------------------------------------------------------------- Bảng chung

def _lay_bang(loai):
    if loai not in BANG:
        abort(404)
    mo_hinh, bm, ten, noi_bo = BANG[loai]
    if noi_bo and not current_user.noi_bo:
        abort(403)
    return mo_hinh, bm, ten


@bp.route("/<any(dtm, 'ho-so', 'dang-ky-mt', 'chu-the'):loai>")
@login_required
def ds_bang(loai):
    mo_hinh, bm, ten = _lay_bang(loai)
    q = db.session.query(mo_hinh)
    if hasattr(mo_hinh, "co_so_du_an_id"):
        q = loc_co_so(q.outerjoin(CoSoDuAn, mo_hinh.co_so_du_an_id == CoSoDuAn.id))
    ds = q.order_by(mo_hinh.id.desc()).all()
    cot = [t for t in bm.truong if t.kieu not in ("textarea", "bool")][:6]
    return render_template("bang_danh_sach.html", ds=ds, bm=bm, cot=cot, ten=ten, loai=loai)


@bp.route("/<any(dtm, 'ho-so', 'dang-ky-mt', 'chu-the'):loai>/moi", methods=["GET", "POST"])
@bp.route("/<any(dtm, 'ho-so', 'dang-ky-mt', 'chu-the'):loai>/<int:id>", methods=["GET", "POST"])
@can_quyen_sua
def sua_bang(loai, id=None):
    mo_hinh, bm, ten = _lay_bang(loai)
    obj = db.get_or_404(mo_hinh, id) if id else mo_hinh()
    if not id and hasattr(obj, "co_so_du_an_id"):
        obj.co_so_du_an_id = request.args.get("co_so", type=int)
    if request.method == "POST":
        if request.form.get("_xoa") == "1" and id:
            if current_user.vai_tro != "quan_tri":
                abort(403)
            if loai == "chu-the" and obj.co_so:
                flash("Chủ cơ sở còn gắn với cơ sở/dự án, không xóa được.", "loi")
                return redirect(url_for("danh_muc.sua_bang", loai=loai, id=id))
            db.session.delete(obj)
            db.session.commit()
            flash("Đã xóa.", "ok")
            return redirect(url_for("danh_muc.ds_bang", loai=loai))
        loi = bm.dien(obj, request.form)
        if not loi:
            db.session.add(obj)
            db.session.commit()
            flash("Đã lưu.", "ok")
            return redirect(url_for("danh_muc.ds_bang", loai=loai))
        db.session.rollback()
        for x in loi:
            flash(x, "loi")
    return render_template("bieu_mau.html", bm=bm, obj=obj, tieu_de=f"{ten}{' — sửa' if id else ' — thêm mới'}",
                           co_xoa=bool(id) and current_user.vai_tro == "quan_tri",
                           quay_lai=url_for("danh_muc.ds_bang", loai=loai))
