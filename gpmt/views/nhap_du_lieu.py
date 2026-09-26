"""Trang 'Nhập dữ liệu': tải sổ Excel lên, tải mẫu bổ sung thời hạn/ngày ký, xem báo cáo nhập.

Thay cho các lệnh CLI để cán bộ không chuyên làm được trên trình duyệt.
"""
from datetime import date

from flask import Blueprint, Response, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user

from ..auth import can_quan_tri, can_quyen_sua
from ..dich_vu import da_co_du_lieu_so, nhap_mau_bo_sung, nhap_so, xoa_du_lieu_nghiep_vu, xuat_mau_bo_sung
from ..extensions import db
from ..models import BaoCaoNhapLuu, Gpmt
from ..trang_thai import CHUA_XAC_DINH

bp = Blueprint("nhap_du_lieu", __name__, url_prefix="/nhap-du-lieu")

GIOI_HAN_TEP = 4 * 1024 * 1024  # Vercel nhận tối đa ~4,5 MB mỗi lần gửi


def _doc_tep(ten_o, duoi):
    tep = request.files.get(ten_o)
    if not tep or not tep.filename:
        flash("Chưa chọn tệp.", "loi")
        return None, None
    if not tep.filename.lower().endswith(duoi):
        flash(f"Tệp phải có đuôi {' hoặc '.join(duoi) if isinstance(duoi, tuple) else duoi}.", "loi")
        return None, None
    noi_dung = tep.read(GIOI_HAN_TEP + 1)
    if len(noi_dung) > GIOI_HAN_TEP:
        flash("Tệp quá lớn (tối đa 4 MB).", "loi")
        return None, None
    return noi_dung, tep.filename


@bp.route("/")
@can_quyen_sua
def trang_chinh():
    ds_bao_cao = db.session.query(BaoCaoNhapLuu).order_by(BaoCaoNhapLuu.thoi_diem.desc()).limit(30).all()
    tong = db.session.query(Gpmt).count()
    so_thieu = sum(1 for g in db.session.query(Gpmt).all() if g.trang_thai == CHUA_XAC_DINH)
    return render_template("nhap_du_lieu.html", ds_bao_cao=ds_bao_cao, da_co=da_co_du_lieu_so(), tong=tong,
                           so_thieu=so_thieu)


@bp.route("/so-excel", methods=["POST"])
@can_quan_tri
def tai_so_excel():
    noi_dung, ten = _doc_tep("tep", ".xls")
    if noi_dung is None:
        return redirect(url_for(".trang_chinh"))
    if da_co_du_lieu_so():
        flash("CSDL đã có dữ liệu từ sổ Excel. Muốn nhập lại thì xóa dữ liệu cũ trước (mục 3 bên dưới).", "loi")
        return redirect(url_for(".trang_chinh"))
    try:
        luu = nhap_so(noi_dung=noi_dung, ten_tep=ten, tai_khoan_id=current_user.id)
    except Exception as e:  # sổ sai cấu trúc, thiếu sheet…
        db.session.rollback()
        flash(f"Không nhập được: {e}", "loi")
        return redirect(url_for(".trang_chinh"))
    flash(f"Đã nhập xong: {luu.tom_tat}.", "ok")
    return redirect(url_for(".xem_bao_cao", id=luu.id))


@bp.route("/mau-bo-sung")
@can_quyen_sua
def tai_mau_bo_sung():
    tat_ca = request.args.get("tat_ca") == "1"
    ds = db.session.query(Gpmt).order_by(Gpmt.nam_cap, Gpmt.ngay_ky, Gpmt.id).all()
    if not tat_ca:
        ds = [g for g in ds if g.trang_thai == CHUA_XAC_DINH]
    return send_file(xuat_mau_bo_sung(ds), as_attachment=True,
                     download_name=f"Mau_bo_sung_thoi_han_GPMT_{date.today().isoformat()}.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@bp.route("/bo-sung", methods=["POST"])
@can_quyen_sua
def tai_len_bo_sung():
    noi_dung, ten = _doc_tep("tep", ".xlsx")
    if noi_dung is None:
        return redirect(url_for(".trang_chinh"))
    try:
        luu = nhap_mau_bo_sung(noi_dung, ten_tep=ten, tai_khoan_id=current_user.id)
    except Exception as e:
        db.session.rollback()
        flash(f"Không đọc được tệp: {e}", "loi")
        return redirect(url_for(".trang_chinh"))
    flash(f"Đã xử lý mẫu bổ sung: {luu.tom_tat}.", "ok")
    return redirect(url_for(".xem_bao_cao", id=luu.id))


@bp.route("/xoa", methods=["POST"])
@can_quan_tri
def xoa():
    if request.form.get("xac_nhan", "").strip().upper() != "XOA DU LIEU":
        flash("Chưa gõ đúng cụm xác nhận 'XOA DU LIEU' — không xóa gì.", "loi")
        return redirect(url_for(".trang_chinh"))
    xoa_du_lieu_nghiep_vu()
    db.session.add(BaoCaoNhapLuu(loai="xoa", tai_khoan_id=current_user.id, tom_tat="Xóa toàn bộ dữ liệu nghiệp vụ",
                                 noi_dung=f"# Xóa dữ liệu nghiệp vụ\n\nNgười thực hiện: {current_user.ho_ten}\n"))
    db.session.commit()
    flash("Đã xóa dữ liệu nghiệp vụ. Có thể tải sổ Excel lên lại.", "ok")
    return redirect(url_for(".trang_chinh"))


@bp.route("/bao-cao/<int:id>")
@can_quyen_sua
def xem_bao_cao(id):
    bc = db.get_or_404(BaoCaoNhapLuu, id)
    if request.args.get("tai") == "1":
        return Response(bc.noi_dung, mimetype="text/markdown; charset=utf-8", headers={
            "Content-Disposition": f"attachment; filename=bao-cao-nhap-{bc.id}-{bc.thoi_diem:%Y-%m-%d}.md"})
    return render_template("bao_cao_nhap.html", bc=bc)
