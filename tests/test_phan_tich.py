"""Tách số/ngày GP từ các chuỗi lộn xộn (mục 3.1) và đọc số kiểu Việt."""
from datetime import date

import pytest

from gpmt.phan_tich import doc_so_lieu, doc_so_viet, quy_doi_kg_nam, tach_giay_phep, tach_kcn_ccn


@pytest.mark.parametrize("chuoi, so_hieu, ngay", [
    ("2074/GPMT-UBND 20/09/2022", "2074/GPMT-UBND", date(2022, 9, 20)),
    ("1587/GPMT-UBND ngày18/07/2022", "1587/GPMT-UBND", date(2022, 7, 18)),
    ("123/GP-UBND ngày 16/01/2023", "123/GP-UBND", date(2023, 1, 16)),
    ("1051/GP-UBND ngày 05/5//2023", "1051/GP-UBND", date(2023, 5, 5)),
    ("1663/GP-UBND ngày 007/7/2023", "1663/GP-UBND", date(2023, 7, 7)),
    ("866/GPMT- UBND ngày 31/3/2025", "866/GPMT-UBND", date(2025, 3, 31)),
    ("3010/QĐ-UBND 27/11/2023 ngày", "3010/QĐ-UBND", date(2023, 11, 27)),
    ("175/GPMT-BNNMT ngày 09/6/2025", "175/GPMT-BNNMT", date(2025, 6, 9)),
])
def test_tach_so_ngay(chuoi, so_hieu, ngay):
    (gp,) = tach_giay_phep(chuoi)
    assert gp.so_hieu == so_hieu
    assert gp.ngay_ky == ngay


def test_thieu_ngay_gan_co():
    (gp,) = tach_giay_phep("150/GPMT-BTNMT")
    assert gp.so_hieu == "150/GPMT-BTNMT" and gp.ngay_ky is None
    assert any("không ghi ngày" in x for x in gp.can_ra_soat)


def test_mot_o_hai_giay_phep():
    ds = tach_giay_phep("2568/GPMT-UBND ngày 27/12/2022, cấp điều chỉnh GPMT số 1827/GPMT-UBND ngày 16/9/2024")
    assert [g.so_hieu for g in ds] == ["2568/GPMT-UBND", "1827/GPMT-UBND"]
    assert [g.ngay_ky for g in ds] == [date(2022, 12, 27), date(2024, 9, 16)]
    assert [g.cap_dieu_chinh for g in ds] == [False, True]


def test_loi_go_ky_hieu():
    (gp,) = tach_giay_phep("768/GPMT-UNMD ngày 16/05/2023")
    assert gp.so_hieu == "768/GPMT-UBND"
    assert gp.canh_bao and gp.loai_van_ban == "GPMT"


@pytest.mark.parametrize("chuoi", ["2010/QĐ-UBND 14/08/2023", "3234/GPTN-UBND 20/12/2023",
                                   "2341/GPTNMT-UBND 27/09/2023"])
def test_ky_hieu_chua_ro_khong_tu_doan(chuoi):
    (gp,) = tach_giay_phep(chuoi)
    assert gp.loai_van_ban == "chưa rõ"
    assert gp.can_ra_soat


def test_o_trong():
    assert tach_giay_phep("") == [] and tach_giay_phep(None) == []


@pytest.mark.parametrize("chuoi, so", [
    ("1.949", 1949), ("3074,5", 3074.5), ("13.887,1", 13887.1), ("09", 9), ("3.000", 3000),
    ("48.113,5", 48113.5), ("1.466.278", 1466278),
])
def test_so_kieu_viet(chuoi, so):
    assert doc_so_viet(chuoi) == so


@pytest.mark.parametrize("chuoi", ["0.7", "1,234.5", "1.94", "abc"])
def test_so_khong_chac_thi_khong_doan(chuoi):
    assert doc_so_viet(chuoi) is None


@pytest.mark.parametrize("o, don_vi_cot, so, don_vi", [
    ("126 m3/ngày đêm", "m3/ngày đêm", 126, "m3/ngày đêm"),
    ("NTSH: 09", "m3/ngày đêm", 9, "m3/ngày đêm"),
    ("1.949 tấn/năm", "kg/năm", 1949, "tấn/năm"),
    ("3074,5m3/năm", "kg/năm", 3074.5, "m3/năm"),
    (162607.0, "kg/năm", 162607, "kg/năm"),
])
def test_doc_o_so_lieu(o, don_vi_cot, so, don_vi):
    sl = doc_so_lieu(o, don_vi_cot)
    assert sl.so == so and sl.don_vi == don_vi


@pytest.mark.parametrize("o", ["Tuần hoàn", "15.000m3/năm Đất đá thải; 10 kg/năm CTRSH", "180-300",
                               "0.7 m3/ngày đêm NTSH;  80 m3/ngày đêm NTSX", "phân 0,5 tấn/ngày"])
def test_o_lon_xon_chi_giu_nguyen_van(o):
    sl = doc_so_lieu(o, "kg/năm")
    assert sl.so is None and sl.goc


def test_quy_doi_chi_khi_chac():
    assert quy_doi_kg_nam(1949, "tấn/năm") == 1949000
    assert quy_doi_kg_nam(36, "kg/tháng") is None


def test_tach_kcn():
    assert tach_kcn_ccn("Lô F24, Khu công nghiệp Đông Phố Mới, tỉnh Lào Cai") == "KCN Đông Phố Mới"
    assert tach_kcn_ccn("KCN phía Nam, tỉnh Yên Bái") == "KCN Phía Nam"
    assert tach_kcn_ccn("Phường Yên Bái, tỉnh Lào Cai") is None
