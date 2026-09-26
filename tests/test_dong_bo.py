"""Tự đồng bộ bản ghi mới (GPMT, hồ sơ lấy từ Data360X) khi ứng dụng khởi động — không ghi đè chỉnh sửa."""
from datetime import date

from gpmt.dich_vu import dong_bo_ban_ghi_moi
from gpmt.models import BaoCaoNhapLuu, Gpmt, HoSo


def test_dong_bo_nap_ban_ghi_moi_mot_lan(db, du_lieu_that):
    tb = dong_bo_ban_ghi_moi()
    assert tb
    gp = db.session.query(Gpmt).filter_by(so_hieu="3216/GPMT-UBND").one()
    assert gp.ngay_ky == date(2026, 9, 8) and gp.co_quan_cap == "UBND tỉnh Lào Cai" and gp.can_ra_soat
    assert gp.co_so.chu_the.ten == "Công ty cổ phần Khai thác và Chế biến kim loại Thủ Đô"
    ho_so = db.session.query(HoSo).all()
    assert len(ho_so) == 6
    dtm = [h for h in ho_so if h.loai == "ĐTM"]
    assert len(dtm) == 1 and "753/QĐ-SNNMT" in dtm[0].qd_doan_kiem_tra_hoac_hoi_dong
    assert db.session.query(BaoCaoNhapLuu).filter_by(loai="dong-bo").count() == 1

    # Người dùng sửa trên web → lần khởi động sau KHÔNG ghi đè, không nhân bản
    gp.thoi_han_nam = 10
    ho_so[0].trang_thai = "Sở trình (tờ trình)"
    db.session.commit()
    assert dong_bo_ban_ghi_moi() == []
    db.session.expire_all()
    assert db.session.query(Gpmt).filter_by(so_hieu="3216/GPMT-UBND").one().thoi_han_nam == 10
    assert db.session.query(HoSo).count() == 6
    assert db.session.get(HoSo, ho_so[0].id).trang_thai == "Sở trình (tờ trình)"


def test_chua_nhap_so_thi_chua_dong_bo(db):
    assert dong_bo_ban_ghi_moi() == []
    assert db.session.query(Gpmt).count() == 0
