"""Danh sách, chi tiết, nhập/sửa GPMT và các bảng con (xả thải, chất thải, VHTN)."""
import json
import os
from pathlib import Path

from flask import (Blueprint, abort, current_app, flash, redirect, render_template, request, send_file,
                   url_for)
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..auth import can_quan_tri, can_quyen_sua
from ..extensions import db
from ..models import ChuThe, CoSoDuAn, Gpmt, GpmtChatThai, GpmtXaThai, Vhtn
from ..phan_tich import tach_giay_phep
from .bieu_mau import BM_CHAT_THAI, BM_GPMT, BM_VHTN, BM_XA_THAI, NHOM_DU_AN
from .pham_vi import kiem_co_so, loc_co_so

bp = Blueprint("gpmt", __name__, url_prefix="/gpmt")

BANG_CON = {
    "xa-thai": (GpmtXaThai, BM_XA_THAI, "Xả thải"),
    "chat-thai": (GpmtChatThai, BM_CHAT_THAI, "Chất thải"),
    "vhtn": (Vhtn, BM_VHTN, "Vận hành thử nghiệm"),
}


def loc_danh_sach(args):
    """Tìm theo số hiệu, tên cơ sở, chủ cơ sở, MST; lọc theo năm, cơ quan cấp, địa bàn cũ, xã/phường,
    loại hình, nhóm, KCN/CCN, trạng thái, cờ rà soát. Trả (danh sách, bộ lọc đang dùng)."""
    q = (db.session.query(Gpmt).outerjoin(CoSoDuAn, Gpmt.co_so_du_an_id == CoSoDuAn.id)
         .outerjoin(ChuThe, CoSoDuAn.chu_the_id == ChuThe.id))
    q = loc_co_so(q)
    loc = {k: (args.get(k) or "").strip() for k in
           ("q", "nam", "co_quan", "dia_ban", "xa", "loai_hinh", "nhom", "kcn", "trang_thai", "ra_soat",
            "loai_van_ban")}
    if loc["q"]:
        tu = f"%{loc['q']}%"
        q = q.filter(or_(Gpmt.so_hieu.ilike(tu), Gpmt.so_hieu_goc.ilike(tu), CoSoDuAn.ten.ilike(tu),
                         ChuThe.ten.ilike(tu), ChuThe.ma_so_thue.ilike(tu)))
    if loc["nam"].isdigit():
        q = q.filter(Gpmt.nam_cap == int(loc["nam"]))
    if loc["co_quan"]:
        q = q.filter(Gpmt.co_quan_cap.is_(None) if loc["co_quan"] == "_trong" else Gpmt.co_quan_cap == loc["co_quan"])
    if loc["dia_ban"]:
        q = q.filter(CoSoDuAn.dia_ban_cu == loc["dia_ban"])
    if loc["xa"]:
        q = q.filter(CoSoDuAn.xa_phuong_moi.ilike(f"%{loc['xa']}%"))
    if loc["loai_hinh"]:
        q = q.filter(CoSoDuAn.loai_hinh.ilike(f"%{loc['loai_hinh']}%"))
    if loc["nhom"]:
        q = q.filter(CoSoDuAn.nhom_du_an == loc["nhom"])
    if loc["kcn"]:
        q = q.filter(CoSoDuAn.kcn_ccn == loc["kcn"])
    if loc["loai_van_ban"]:
        q = q.filter(Gpmt.loai_van_ban == loc["loai_van_ban"])
    if loc["ra_soat"] == "1" and current_user.noi_bo:
        q = q.filter(Gpmt.can_ra_soat.is_(True))
    ds = q.order_by(Gpmt.ngay_ky.desc().nulls_last(), Gpmt.id.desc()).all()
    if loc["trang_thai"]:
        ds = [g for g in ds if g.trang_thai == loc["trang_thai"]]
    return ds, loc


def _lua_chon_loc():
    def khac(cot):
        return [x[0] for x in db.session.query(cot).distinct().order_by(cot) if x[0]]
    return dict(ds_nam=[x for x in khac(Gpmt.nam_cap)][::-1], ds_co_quan=khac(Gpmt.co_quan_cap),
                ds_kcn=khac(CoSoDuAn.kcn_ccn), ds_nhom=[x for x in NHOM_DU_AN if x])


@bp.route("/")
@login_required
def danh_sach():
    ds, loc = loc_danh_sach(request.args)
    return render_template("gpmt_danh_sach.html", ds=ds, loc=loc, **_lua_chon_loc())


@bp.route("/<int:id>")
@login_required
def chi_tiet(id):
    gp = db.get_or_404(Gpmt, id)
    kiem_co_so(gp.co_so)
    # Chuỗi thay thế: lần ngược về GP gốc rồi đi xuôi
    chuoi, x, da_qua = [], gp, set()
    while x.thay_the and x.thay_the.id not in da_qua:
        da_qua.add(x.id)
        x = x.thay_the
    da_qua = set()
    while x and x.id not in da_qua:
        chuoi.append(x)
        da_qua.add(x.id)
        x = x.bi_thay_the_boi[0] if x.bi_thay_the_boi else None
    ghi_chu_goc = {}
    if current_user.noi_bo and gp.ghi_chu_goc:
        try:
            ghi_chu_goc = json.loads(gp.ghi_chu_goc)
        except ValueError:
            ghi_chu_goc = {"Ghi chú": gp.ghi_chu_goc}
    return render_template("gpmt_chi_tiet.html", gp=gp, chuoi=chuoi, ghi_chu_goc=ghi_chu_goc,
                           co_pdf=bool(_duong_dan_pdf(gp) or current_app.config["PDF_BASE_URL"] and gp.tep_pdf))


@bp.route("/moi", methods=["GET", "POST"])
@bp.route("/<int:id>/sua", methods=["GET", "POST"])
@can_quyen_sua
def sua(id=None):
    gp = db.get_or_404(Gpmt, id) if id else Gpmt(co_so_du_an_id=request.args.get("co_so", type=int),
                                                   loai_van_ban="GPMT", cong_khai=True)
    if request.method == "POST":
        loi = BM_GPMT.dien(gp, request.form)
        if gp.thay_the_gpmt_id and gp.thay_the_gpmt_id == gp.id:
            loi.append("GP không thể tự thay thế chính nó.")
        if gp.so_hieu:
            g = tach_giay_phep(gp.so_hieu)
            if g:
                gp.so, gp.ky_hieu, gp.so_hieu = g[0].so, g[0].ky_hieu, g[0].so_hieu
            else:
                loi.append("Số hiệu phải có dạng <số>/<ký hiệu>, vd 2519/GPMT-UBND.")
        gp.nam_cap = gp.ngay_ky.year if gp.ngay_ky else gp.nam_cap
        if not loi:
            if not gp.nguon_du_lieu:
                gp.nguon_du_lieu = "nhập tay"
            db.session.add(gp)
            db.session.commit()
            flash("Đã lưu giấy phép.", "ok")
            return redirect(url_for("gpmt.chi_tiet", id=gp.id))
        db.session.rollback()
        for x in loi:
            flash(x, "loi")
    return render_template("bieu_mau.html", bm=BM_GPMT, obj=gp,
                           tieu_de=f"Sửa {gp}" if id else "Nhập giấy phép môi trường mới",
                           quay_lai=url_for("gpmt.chi_tiet", id=id) if id else url_for("gpmt.danh_sach"))


@bp.route("/<int:id>/xoa", methods=["POST"])
@can_quan_tri
def xoa(id):
    gp = db.get_or_404(Gpmt, id)
    for g in list(gp.bi_thay_the_boi) + list(gp.cac_ban_dieu_chinh):
        if g.thay_the_gpmt_id == gp.id:
            g.thay_the_gpmt_id = None
        if g.dieu_chinh_gpmt_id == gp.id:
            g.dieu_chinh_gpmt_id = None
    db.session.delete(gp)
    db.session.commit()
    flash(f"Đã xóa {gp}.", "ok")
    return redirect(url_for("gpmt.danh_sach"))


@bp.route("/<int:id>/da-ra-soat", methods=["POST"])
@can_quyen_sua
def da_ra_soat(id):
    gp = db.get_or_404(Gpmt, id)
    gp.can_ra_soat = False
    gp.ly_do_ra_soat = None
    db.session.commit()
    flash(f"Đã bỏ cờ rà soát cho {gp}.", "ok")
    return redirect(request.form.get("tiep") or url_for("gpmt.chi_tiet", id=id))


def _duong_dan_pdf(gp):
    thu_muc = current_app.config["PDF_DIR"]
    if not gp.tep_pdf or not thu_muc:
        return None
    goc = Path(thu_muc).resolve()
    p = (goc / gp.tep_pdf).resolve()
    if goc not in p.parents or not p.is_file():
        return None
    return p


@bp.route("/<int:id>/pdf")
@login_required
def pdf(id):
    gp = db.get_or_404(Gpmt, id)
    kiem_co_so(gp.co_so)
    p = _duong_dan_pdf(gp)
    if p:
        return send_file(p, mimetype="application/pdf", download_name=os.path.basename(p))
    goc_url = current_app.config["PDF_BASE_URL"]
    if goc_url and gp.tep_pdf:
        return redirect(f"{goc_url}/{gp.tep_pdf}")
    abort(404)


# ---------------------------------------------------------------- Bảng con

@bp.route("/<int:gpmt_id>/<loai>/moi", methods=["GET", "POST"])
@bp.route("/<int:gpmt_id>/<loai>/<int:id>", methods=["GET", "POST"])
@can_quyen_sua
def sua_con(gpmt_id, loai, id=None):
    if loai not in BANG_CON:
        abort(404)
    mo_hinh, bm, ten = BANG_CON[loai]
    gp = db.get_or_404(Gpmt, gpmt_id)
    obj = db.get_or_404(mo_hinh, id) if id else mo_hinh(gpmt_id=gp.id)
    if id and obj.gpmt_id != gp.id:
        abort(404)
    if request.method == "POST":
        if request.form.get("_xoa") == "1" and id:
            db.session.delete(obj)
            db.session.commit()
            flash(f"Đã xóa dòng {ten.lower()}.", "ok")
            return redirect(url_for("gpmt.chi_tiet", id=gp.id))
        loi = bm.dien(obj, request.form)
        if not loi:
            db.session.add(obj)
            db.session.commit()
            flash("Đã lưu.", "ok")
            return redirect(url_for("gpmt.chi_tiet", id=gp.id))
        db.session.rollback()
        for x in loi:
            flash(x, "loi")
    return render_template("bieu_mau.html", bm=bm, obj=obj, tieu_de=f"{ten} — {gp}", co_xoa=bool(id),
                           quay_lai=url_for("gpmt.chi_tiet", id=gp.id))
