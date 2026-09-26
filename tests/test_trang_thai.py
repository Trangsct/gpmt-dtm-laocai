"""Tính ngày hết hạn và trạng thái GPMT."""
from datetime import date

from gpmt.models import Gpmt
from gpmt.trang_thai import (BI_THAY_THE, CHUA_XAC_DINH, CON_HIEU_LUC, HET_HAN, SAP_HET_HAN,
                             tinh_ngay_het_han, tinh_trang_thai)


def test_het_han_bang_ngay_ky_cong_thoi_han():
    gp = Gpmt(ngay_ky=date(2026, 7, 22), thoi_han_nam=10)
    assert tinh_ngay_het_han(gp) == date(2036, 7, 22)


def test_ngay_29_2():
    assert tinh_ngay_het_han(Gpmt(ngay_ky=date(2024, 2, 29), thoi_han_nam=7)) == date(2031, 2, 28)


def test_thoi_han_le():
    assert tinh_ngay_het_han(Gpmt(ngay_ky=date(2024, 1, 15), thoi_han_nam=7.5)) == date(2031, 7, 15)


def test_thieu_thoi_han_khong_suy_dien():
    gp = Gpmt(ngay_ky=date(2023, 1, 1), thoi_han_nam=None)
    assert tinh_ngay_het_han(gp) is None
    assert tinh_trang_thai(gp, date(2026, 9, 26)) == CHUA_XAC_DINH


def test_ngay_het_han_nhap_tay_uu_tien():
    gp = Gpmt(ngay_ky=date(2023, 1, 1), thoi_han_nam=10, ngay_het_han_nhap_tay=date(2030, 5, 1))
    assert tinh_ngay_het_han(gp) == date(2030, 5, 1)


def test_cac_trang_thai():
    hom_nay = date(2026, 9, 26)
    assert tinh_trang_thai(Gpmt(ngay_ky=date(2026, 7, 22), thoi_han_nam=10), hom_nay) == CON_HIEU_LUC
    assert tinh_trang_thai(Gpmt(ngay_ky=date(2017, 3, 1), thoi_han_nam=10), hom_nay) == SAP_HET_HAN
    assert tinh_trang_thai(Gpmt(ngay_ky=date(2016, 3, 1), thoi_han_nam=10), hom_nay) == HET_HAN
    cu = Gpmt(ngay_ky=date(2022, 8, 22), thoi_han_nam=10)
    moi = Gpmt(ngay_ky=date(2026, 7, 22), thoi_han_nam=10)
    moi.thay_the = cu
    assert tinh_trang_thai(cu, hom_nay) == BI_THAY_THE
    assert tinh_trang_thai(moi, hom_nay) == CON_HIEU_LUC
