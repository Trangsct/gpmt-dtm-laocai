"""Nhập một bản ghi GPMT đã đối chiếu tay với bản gốc (tệp JSON trong gpmt/ban_ghi_doi_chieu/).

Giai đoạn 1 chưa có bộ đọc PDF tự động (giai đoạn 2), nên GP mẫu 2519/GPMT-UBND được nhập từ tệp JSON
mà số, ngày đã đối chiếu với ảnh trang 1. Nếu JSON có `thay_the` thì GP cũ được gắn quan hệ thay thế và
tự chuyển sang "Hết hiệu lực — bị thay thế".
"""
import json
from datetime import date

from .extensions import db
from .models import ChuThe, CoSoDuAn, Dtm, Gpmt, GpmtChatThai, GpmtXaThai, HoSo, Vhtn
from .phan_tich import chuan_ten


def _ngay(s):
    return date.fromisoformat(s) if s else None


def tim_gpmt(so_hieu, ngay_ky=None):
    q = db.session.query(Gpmt).filter(Gpmt.so_hieu == so_hieu)
    if ngay_ky:
        q = q.filter((Gpmt.ngay_ky == ngay_ky) | (Gpmt.ngay_ky.is_(None)))
    return q.all()


def nhap_ban_ghi(du_lieu: dict) -> tuple[Gpmt, list[str]]:
    """Trả (bản ghi, thông báo). Chạy lại nhiều lần không sinh bản trùng."""
    tb = []
    ngay_ky = _ngay(du_lieu["ngay_ky"])
    cu = tim_gpmt(du_lieu["so_hieu"], ngay_ky)
    gp = cu[0] if cu else Gpmt()
    if not cu:
        db.session.add(gp)

    # GP bị thay thế: dùng lại cơ sở của nó (cùng một cơ sở, GP mới cấp lại)
    gp_cu = None
    tt = du_lieu.get("thay_the")
    if tt:
        ds = tim_gpmt(tt["so_hieu"], _ngay(tt.get("ngay_ky")))
        if len(ds) == 1:
            gp_cu = ds[0]
        elif not ds:
            tb.append(f"Chưa có GP {tt['so_hieu']} trong CSDL — tạo bản ghi tối thiểu để giữ quan hệ thay thế")
            gp_cu = Gpmt(so_hieu=tt["so_hieu"], so=int(tt["so_hieu"].split("/")[0]),
                         ky_hieu=tt["so_hieu"].split("/")[1], ngay_ky=_ngay(tt.get("ngay_ky")),
                         co_quan_cap=tt.get("co_quan_cap"), nguon_du_lieu="nhập tay (từ Điều 3 của GP thay thế)")
            gp_cu.them_ly_do("Bản ghi tối thiểu tạo từ GP thay thế — cần bổ sung thông tin")
            db.session.add(gp_cu)
        else:
            tb.append(f"Có {len(ds)} bản ghi {tt['so_hieu']} — chưa gắn quan hệ thay thế, cần chọn tay")

    cs_dl, ct_dl = du_lieu["co_so"], du_lieu["chu_the"]
    cs = gp.co_so or (gp_cu.co_so if gp_cu else None)
    if cs is None:
        cs = CoSoDuAn(ten=cs_dl["ten"])
        db.session.add(cs)
    ct = cs.chu_the
    if ct is None or (ct_dl.get("ma_so_thue") and ct.ma_so_thue not in (None, ct_dl["ma_so_thue"])):
        ct = next((c for c in db.session.query(ChuThe).all() if chuan_ten(c.ten) == chuan_ten(ct_dl["ten"])),
                  None) or ChuThe(ten=ct_dl["ten"])
        cs.chu_the = ct
    for k, v in ct_dl.items():
        setattr(ct, k, v)
    for k, v in cs_dl.items():
        setattr(cs, k, v)

    for k in ("so_hieu", "so", "ky_hieu", "co_quan_cap", "nguoi_ky", "loai_cap", "thoi_han_nam",
              "qd_doan_kiem_tra", "to_trinh", "van_ban_de_nghi", "cong_suat_goc", "tep_pdf", "nguon_du_lieu"):
        if k in du_lieu:
            setattr(gp, k, du_lieu[k])
    gp.loai_van_ban = "GPMT"
    for x in du_lieu.get("ly_do_ra_soat", []):
        gp.them_ly_do(x)
    gp.ngay_ky = ngay_ky
    gp.nam_cap = ngay_ky.year
    gp.co_so = cs
    if gp_cu is not None and gp_cu is not gp:
        gp.thay_the = gp_cu
        tb.append(f"{gp_cu.so_hieu} → Hết hiệu lực — bị thay thế bởi {gp.so_hieu}")

    gp.xa_thai.clear()
    gp.chat_thai.clear()
    gp.vhtn.clear()
    for x in du_lieu.get("xa_thai", []):
        gp.xa_thai.append(GpmtXaThai(**x))
    for x in du_lieu.get("chat_thai", []):
        gp.chat_thai.append(GpmtChatThai(**x))
    for x in du_lieu.get("vhtn", []):
        gp.vhtn.append(Vhtn(**{k: (_ngay(v) if k in ("bat_dau", "ket_thuc_du_kien", "gia_han_den") else v)
                               for k, v in x.items()}))
    db.session.commit()
    return gp, tb


def doc_tep_json(duong_dan) -> list[dict]:
    """Một tệp chứa một bản ghi, hoặc {"ban_ghi": [...]} gồm nhiều bản ghi."""
    with open(duong_dan, encoding="utf-8") as f:
        du_lieu = json.load(f)
    return du_lieu["ban_ghi"] if "ban_ghi" in du_lieu else [du_lieu]


def nhap_tep_json(duong_dan):
    """Tương thích cũ: nhập tệp một GPMT. Trả (bản ghi, thông báo) của bản ghi đầu."""
    kq = [nhap_mot(x) for x in doc_tep_json(duong_dan)]
    return kq[0]


def nhap_mot(du_lieu: dict):
    """Nhập một bản ghi theo trường "loai": gpmt (mặc định) / ho_so / dtm."""
    loai = du_lieu.get("loai", "gpmt")
    if loai == "ho_so":
        return nhap_ho_so(du_lieu)
    if loai == "dtm":
        return nhap_dtm(du_lieu)
    return nhap_ban_ghi(du_lieu)


def da_co(du_lieu: dict) -> bool:
    """Bản ghi đã có trong CSDL chưa (để đồng bộ tự động không ghi đè chỉnh sửa trên web)."""
    loai = du_lieu.get("loai", "gpmt")
    if loai == "ho_so":
        return tim_ho_so(du_lieu) is not None
    if loai == "dtm":
        return tim_dtm(du_lieu["so_qd"], _ngay(du_lieu.get("ngay_qd"))) is not None
    return bool(tim_gpmt(du_lieu["so_hieu"], _ngay(du_lieu["ngay_ky"])))


# ---------------------------------------------------------------- Hồ sơ đang giải quyết

def _lay_co_so(cs_dl: dict, ct_ten: str | None):
    """Tìm cơ sở theo tên (không phân biệt dấu, hoa thường); chưa có thì tạo."""
    khoa = chuan_ten(cs_dl["ten"])
    cs = next((c for c in db.session.query(CoSoDuAn).all() if chuan_ten(c.ten) == khoa), None)
    if cs is None:
        cs = CoSoDuAn(ten=cs_dl["ten"])
        db.session.add(cs)
    for k, v in cs_dl.items():
        if v and not getattr(cs, k):
            setattr(cs, k, v)
    if ct_ten and cs.chu_the is None:
        ct = next((c for c in db.session.query(ChuThe).all() if chuan_ten(c.ten) == chuan_ten(ct_ten)), None)
        cs.chu_the = ct or ChuThe(ten=ct_ten)
    return cs


def tim_ho_so(du_lieu: dict):
    khoa = chuan_ten(du_lieu["co_so"]["ten"])
    for h in db.session.query(HoSo).filter(HoSo.loai == du_lieu["loai_ho_so"]).all():
        if h.co_so and chuan_ten(h.co_so.ten) == khoa:
            return h
    return None


def nhap_ho_so(du_lieu: dict):
    """Hồ sơ đang giải quyết lấy từ văn bản đến (QĐ thành lập HĐTĐ/đoàn kiểm tra, giấy mời, xin ý kiến)."""
    h = tim_ho_so(du_lieu)
    with db.session.no_autoflush:
        cs = _lay_co_so(du_lieu["co_so"], du_lieu.get("chu_the"))
    if h is None:
        h = HoSo(loai=du_lieu["loai_ho_so"], co_so=cs)
        db.session.add(h)
    h.co_so = cs
    for k in ("van_ban_de_nghi", "qd_doan_kiem_tra_hoac_hoi_dong", "van_ban_bo_sung", "to_trinh", "trang_thai",
              "can_bo_thu_ly", "ghi_chu"):
        if k in du_lieu:
            setattr(h, k, du_lieu[k])
    if du_lieu.get("ngay_tiep_nhan"):
        h.ngay_tiep_nhan = _ngay(du_lieu["ngay_tiep_nhan"])
    db.session.commit()
    return h, []


# ---------------------------------------------------------------- Quyết định phê duyệt ĐTM

def tim_dtm(so_qd, ngay_qd=None):
    q = db.session.query(Dtm).filter(Dtm.so_qd == so_qd)
    if ngay_qd:
        q = q.filter((Dtm.ngay_qd == ngay_qd) | (Dtm.ngay_qd.is_(None)))
    return q.first()


def nhap_dtm(du_lieu: dict):
    """QĐ phê duyệt kết quả thẩm định báo cáo ĐTM lấy từ văn bản đến (Data360X). Chạy lại không sinh trùng."""
    ngay = _ngay(du_lieu.get("ngay_qd"))
    d = tim_dtm(du_lieu["so_qd"], ngay)
    with db.session.no_autoflush:
        cs = _lay_co_so(du_lieu["co_so"], du_lieu.get("chu_the"))
    if d is None:
        d = Dtm(so_qd=du_lieu["so_qd"], co_so=cs)
        db.session.add(d)
    d.co_so = cs
    d.ngay_qd = ngay or d.ngay_qd
    for k in ("co_quan_phe_duyet", "nhom_du_an", "qd_thanh_lap_hoi_dong", "tep_pdf", "ghi_chu"):
        if du_lieu.get(k):
            setattr(d, k, du_lieu[k])
    if du_lieu.get("ly_do_ra_soat"):
        d.can_ra_soat = True
        d.ly_do_ra_soat = du_lieu["ly_do_ra_soat"]
    db.session.commit()
    return d, []
