"""Nhập sổ Excel thật + GP 2519 — các tiêu chí nghiệm thu của mục 3."""
from datetime import date

from gpmt.models import CoSoDuAn, Gpmt
from gpmt.nhap_excel import doc_so_theo_doi, viet_bao_cao
from gpmt.trang_thai import BI_THAY_THE

from .conftest import TEP_SO


def test_doc_so_dung_so_dong():
    dl = doc_so_theo_doi(TEP_SO)
    assert dl.so_dong_du_lieu["GPMT Tinh cap"] == 80
    assert dict(dl.so_dong_theo_nam["GPMT Tinh cap"]) == {2022: 3, 2023: 37, 2024: 26, 2025: 14}
    # 61 dòng có số TT + 5 dòng không có TT nhưng đủ dữ liệu
    assert dl.so_dong_du_lieu["GPMT tỉnh YB cũ"] == 66
    assert len([d for d in dl.gpmt if d.sheet == "GPMT tỉnh YB cũ" and d.tt]) == 61
    assert dl.so_dong_du_lieu["GPMT cấp huyện cũ"] == 1
    assert dl.so_dong_du_lieu["VHTN"] == 144
    assert all("\xa0" not in v.stt for v in dl.vhtn)


def test_2519_lam_1439_bi_thay_the(db, du_lieu_that):
    gp_cu = db.session.query(Gpmt).filter_by(so_hieu="1439/GPMT-UBND").one()
    gp_moi = db.session.query(Gpmt).filter_by(so_hieu="2519/GPMT-UBND").one()
    assert gp_cu.trang_thai == BI_THAY_THE
    assert gp_moi.thay_the is gp_cu
    assert gp_moi.ngay_ky == date(2026, 7, 22)
    assert gp_moi.ngay_het_han == date(2036, 7, 22)
    assert gp_moi.co_so is gp_cu.co_so          # cùng một cơ sở
    assert gp_moi.co_so.chu_the.ma_so_thue == "0107094917"
    assert gp_moi.co_so.nhom_du_an == "II"


def test_nhap_lai_2519_khong_sinh_ban_trung(db, du_lieu_that):
    from gpmt.nhap_ban_ghi import nhap_tep_json

    from .conftest import TEP_2519
    nhap_tep_json(TEP_2519)
    assert db.session.query(Gpmt).filter_by(so_hieu="2519/GPMT-UBND").count() == 1


def test_khong_tu_suy_thoi_han(db, du_lieu_that):
    tu_excel = db.session.query(Gpmt).filter(Gpmt.nguon_du_lieu.like("excel:%")).all()
    assert tu_excel and all(g.thoi_han_nam is None for g in tu_excel)


def test_van_ban_chua_ro_duoc_gan_co(db, du_lieu_that):
    qd = db.session.query(Gpmt).filter(Gpmt.ky_hieu == "QĐ-UBND").all()
    assert len(qd) == 8  # 7 ở sheet Lào Cai + 1 ở sheet YB
    assert all(g.can_ra_soat and g.loai_van_ban == "chưa rõ" for g in qd)
    gptn = db.session.query(Gpmt).filter(Gpmt.ky_hieu.in_(["GPTN-UBND", "GPTNMT-UBND"])).all()
    assert len(gptn) == 4 and all(g.can_ra_soat for g in gptn)


def test_o_hai_giay_phep_tach_va_trung_so_bi_gan_co(db, du_lieu_that):
    ds = db.session.query(Gpmt).filter_by(so_hieu="1827/GPMT-UBND").all()
    assert len(ds) == 2      # một của trại lợn Anifer (ô 2 GP), một của thủy điện Văn Chấn
    assert all(any("Trùng số hiệu" in x for x in g.ds_ly_do) for g in ds)
    dieu_chinh = [g for g in ds if g.dieu_chinh_cho is not None]
    assert len(dieu_chinh) == 1 and dieu_chinh[0].dieu_chinh_cho.so_hieu == "2568/GPMT-UBND"
    assert dieu_chinh[0].trang_thai != BI_THAY_THE   # điều chỉnh không tự làm GP gốc hết hiệu lực


def test_dong_trung_duoc_gop(db, du_lieu_that):
    assert db.session.query(Gpmt).filter(Gpmt.so == 2609).count() == 1
    assert db.session.query(Gpmt).filter(Gpmt.so == 2279).count() == 1


def test_ghep_sheet_vhtn(db, du_lieu_that):
    # Sổ chính không ghi số, sheet VHTN có → ghép theo tên, gắn cờ duyệt
    nam_luc = db.session.query(Gpmt).filter_by(so_hieu="1616/GPMT-UBND", ngay_ky=date(2023, 7, 4)).one()
    assert "Nậm Lúc" in nam_luc.co_so.ten and nam_luc.can_ra_soat
    # Chỉ có ở sheet VHTN → tạo mới, gắn cờ
    sunrise = db.session.query(Gpmt).filter_by(so_hieu="938/GPMT-UBND").one()
    assert sunrise.can_ra_soat
    # Địa chỉ mới lấy từ sheet VHTN
    sojo = db.session.query(Gpmt).filter_by(so_hieu="2074/GPMT-UBND").one()
    assert sojo.co_so.xa_phuong_moi == "Phường Lào Cai"


def test_so_lieu_chat_thai(db, du_lieu_that):
    gp = db.session.query(Gpmt).filter_by(so_hieu="1723/GPMT-UBND").one()
    ctr = next(c for c in gp.chat_thai if c.loai == "CTR thông thường (sổ)")
    assert ctr.khoi_luong_goc == "1.949 tấn/năm" and ctr.khoi_luong_so == 1949
    assert ctr.khoi_luong_kg_nam == 1949000
    nuoc = next(x for x in gp.xa_thai if x.loai == "nước thải")
    assert nuoc.luu_luong_goc == "Tuần hoàn" and nuoc.luu_luong_max is None


def test_nghi_nhap_nham_nam(db, du_lieu_that):
    gp = db.session.query(Gpmt).filter_by(so_hieu="1947/GP-UBND").one()
    assert any("nhầm năm" in x for x in gp.ds_ly_do)


def test_bao_cao_nhap(db, du_lieu_that):
    md = viet_bao_cao(du_lieu_that, "so.xls")
    assert "Bản ghi gắn cờ" in md and "Dòng trùng đã gộp" in md and "không có số TT" in md


def test_khong_co_co_so_mo_coi(db, du_lieu_that):
    assert all(cs.gpmt for cs in db.session.query(CoSoDuAn).all())
