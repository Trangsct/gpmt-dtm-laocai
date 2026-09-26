"""Bảng điều khiển, danh sách cần rà soát, nhật ký, xuất Excel."""
import io
import json
from collections import Counter
from datetime import date

from flask import Blueprint, render_template, request, send_file
from flask_login import current_user

from ..auth import can_noi_bo, can_xem
from ..extensions import db
from ..models import CoSoDuAn, Dtm, Gpmt, HoSo, NhatKy, Vhtn
from ..trang_thai import BI_THAY_THE, CHUA_XAC_DINH, HET_HAN, SAP_HET_HAN
from .pham_vi import loc_co_so

bp = Blueprint("main", __name__)


def ds_gpmt_trong_pham_vi():
    q = db.session.query(Gpmt).outerjoin(CoSoDuAn, Gpmt.co_so_du_an_id == CoSoDuAn.id)
    return loc_co_so(q)


@bp.route("/")
@can_xem
def trang_chu():
    """Trang chủ giới thiệu, quảng bá Sở NN&MT (Bạn yêu cầu 27/9/2026). Số liệu lấy trực tiếp từ CSDL."""
    from .cong_bo import doc_du_lieu
    ds = ds_gpmt_trong_pham_vi().all()
    co_so = {g.co_so_du_an_id for g in ds if g.co_so_du_an_id}
    xa = {g.co_so.xa_phuong_moi for g in ds if g.co_so and g.co_so.xa_phuong_moi}
    moi = sorted([g for g in ds if g.ngay_ky and g.loai_van_ban == "GPMT"], key=lambda g: g.ngay_ky, reverse=True)[:6]
    tthc = doc_du_lieu()
    nam = sorted({g.nam_cap for g in ds if g.nam_cap})
    return render_template(
        "trang_chu.html", tong=len(ds), so_nam=len(nam), nam_dau=nam[0] if nam else None,
        nam_cuoi=nam[-1] if nam else None,
        so_co_so=len(co_so), so_xa=len(xa), so_dtm=db.session.query(Dtm).count(),
        so_tthc=sum(1 for t in tthc["thu_tuc"] if not t["da_thay_the"]), gp_moi=moi)


@bp.route("/thong-ke")
@can_xem
def bang_dieu_khien():
    hom_nay = date.today()
    ds = ds_gpmt_trong_pham_vi().all()
    theo_nam = Counter(g.nam_cap for g in ds)
    theo_co_quan = Counter(g.co_quan_cap or "(chưa xác định)" for g in ds)
    theo_trang_thai = Counter(g.trang_thai for g in ds)
    sap_het = sorted([g for g in ds if g.trang_thai == SAP_HET_HAN], key=lambda g: g.ngay_het_han)
    het_han = sorted([g for g in ds if g.trang_thai == HET_HAN], key=lambda g: g.ngay_het_han)
    ids = {g.id for g in ds}
    vhtn_qua_han = [v for v in db.session.query(Vhtn).filter(Vhtn.trang_thai.in_(["đang", "chưa"])).all()
                    if v.gpmt_id in ids and (v.gia_han_den or v.ket_thuc_du_kien)
                    and (v.gia_han_den or v.ket_thuc_du_kien) < hom_nay]
    ho_so = []
    ra_soat = 0
    if current_user.noi_bo:
        ho_so = (db.session.query(HoSo).filter(HoSo.trang_thai.notin_(["Đã ký GP/QĐ", "Trả hồ sơ / dừng"]))
                 .order_by(HoSo.ngay_tiep_nhan).all())
        ra_soat = sum(1 for g in ds if g.can_ra_soat)
    thieu_thoi_han = sum(1 for g in ds if g.trang_thai == CHUA_XAC_DINH)
    max_nam = max(theo_nam.values(), default=1)
    max_cq = max(theo_co_quan.values(), default=1)
    return render_template(
        "bang_dieu_khien.html", tong=len(ds), theo_nam=sorted(theo_nam.items(), key=lambda x: x[0] or 0),
        theo_co_quan=theo_co_quan.most_common(), theo_trang_thai=theo_trang_thai, max_nam=max_nam,
        max_cq=max_cq, sap_het=sap_het, het_han=het_han, vhtn_qua_han=vhtn_qua_han, ho_so=ho_so,
        ra_soat=ra_soat, thieu_thoi_han=thieu_thoi_han, bi_thay_the=theo_trang_thai.get(BI_THAY_THE, 0))


@bp.route("/ra-soat")
@can_noi_bo
def ra_soat():
    ds = (db.session.query(Gpmt).filter(Gpmt.can_ra_soat.is_(True))
          .order_by(Gpmt.nguon_du_lieu).all())
    nhom = Counter()
    for g in ds:
        for x in g.ds_ly_do:
            nhom[x.split(" — ")[0].split("'")[0].split("(")[0].strip()] += 1
    return render_template("ra_soat.html", ds=ds, nhom=nhom.most_common())


@bp.route("/nhat-ky")
@can_noi_bo
def nhat_ky():
    bang = request.args.get("bang")
    ban_ghi = request.args.get("ban_ghi", type=int)
    q = db.session.query(NhatKy).order_by(NhatKy.thoi_diem.desc())
    if bang:
        q = q.filter(NhatKy.bang == bang)
    if ban_ghi:
        q = q.filter(NhatKy.ban_ghi == ban_ghi)
    ds = q.limit(500).all()
    for x in ds:
        try:
            x.doi = json.loads(x.thay_doi or "{}")
        except ValueError:
            x.doi = {}
    return render_template("nhat_ky.html", ds=ds)


@bp.route("/xuat-excel")
@can_xem
def xuat_excel():
    from ..xuat_excel import xuat_phu_luc_64
    from .gpmt import loc_danh_sach
    ds, _ = loc_danh_sach(request.args)
    tieu_de = request.args.get("tieu_de") or None
    tep = io.BytesIO()
    xuat_phu_luc_64(ds, tep, tieu_de=tieu_de, noi_bo=current_user.noi_bo)
    tep.seek(0)
    return send_file(tep, as_attachment=True,
                     download_name=f"Phu_luc_6.4_GPMT_{date.today().isoformat()}.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@bp.route("/suc-khoe")
def suc_khoe():
    """Tự chẩn đoán cấu hình (không cần đăng nhập, không hiện giá trị bí mật). ?json=1 cho máy giám sát."""
    from flask import current_app

    from ..chan_doan import kiem_tra
    try:
        kq = kiem_tra(current_app)
    finally:
        db.session.rollback()
    ok = all(x.dat is not False for x in kq)
    if request.args.get("json") == "1":
        return ({"trang_thai": "ok" if ok else "loi",
                 "kiem_tra": [{"ten": x.ten, "dat": x.dat, "chi_tiet": x.chi_tiet, "viec_can_lam": x.viec_can_lam}
                              for x in kq]}, 200 if ok else 503)
    return render_template("suc_khoe.html", kq=kq, ok=ok), 200 if ok else 503

