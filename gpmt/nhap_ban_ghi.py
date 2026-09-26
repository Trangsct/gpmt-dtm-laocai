"""Nhập một bản ghi GPMT đã đối chiếu tay với bản gốc (tệp JSON trong gpmt/ban_ghi_doi_chieu/).

Giai đoạn 1 chưa có bộ đọc PDF tự động (giai đoạn 2), nên GP mẫu 2519/GPMT-UBND được nhập từ tệp JSON
mà số, ngày đã đối chiếu với ảnh trang 1. Nếu JSON có `thay_the` thì GP cũ được gắn quan hệ thay thế và
tự chuyển sang "Hết hiệu lực — bị thay thế".
"""
import json
from datetime import date

from .extensions import db
from .models import ChuThe, CoSoDuAn, Gpmt, GpmtChatThai, GpmtXaThai, Vhtn
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


def nhap_tep_json(duong_dan):
    with open(duong_dan, encoding="utf-8") as f:
        return nhap_ban_ghi(json.load(f))
