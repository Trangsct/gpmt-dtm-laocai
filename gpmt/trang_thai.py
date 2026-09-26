"""Tính ngày hết hạn và trạng thái GPMT.

- Thời hạn đọc từ Điều 3 của chính GP, tính từ ngày ký (mục 2 HUONG_DAN.md).
- Không có ngày ký hoặc thời hạn → "Chưa xác định"; KHÔNG suy thời hạn từ nhóm dự án.
- GP bị một GP khác thay thế (GP mới ghi "GP số … hết hiệu lực") → "Hết hiệu lực — bị thay thế",
  bất kể còn hạn hay không.
"""
from calendar import monthrange
from datetime import date

CON_HIEU_LUC = "Còn hiệu lực"
SAP_HET_HAN = "Sắp hết hạn"
HET_HAN = "Hết hạn"
BI_THAY_THE = "Hết hiệu lực — bị thay thế"
CHUA_XAC_DINH = "Chưa xác định"

DS_TRANG_THAI = [CON_HIEU_LUC, SAP_HET_HAN, HET_HAN, BI_THAY_THE, CHUA_XAC_DINH]

SO_THANG_CANH_BAO = 12


def cong_thang(d: date, so_thang: int) -> date:
    """Cộng tháng; ngày không tồn tại ở tháng đích (29/2, 31/…) lùi về ngày cuối tháng."""
    thang = d.month - 1 + so_thang
    nam = d.year + thang // 12
    thang = thang % 12 + 1
    return date(nam, thang, min(d.day, monthrange(nam, thang)[1]))


def tinh_ngay_het_han(gp):
    """Ngày hết hạn = ngày ký + thời hạn (năm). Thời hạn lẻ (vd 7,5 năm) quy ra tháng."""
    if gp.ngay_het_han_nhap_tay:
        return gp.ngay_het_han_nhap_tay
    if not gp.ngay_ky or not gp.thoi_han_nam:
        return None
    so_thang = round(gp.thoi_han_nam * 12)
    return cong_thang(gp.ngay_ky, so_thang)


def tinh_trang_thai(gp, hom_nay: date | None = None) -> str:
    hom_nay = hom_nay or date.today()
    if gp.bi_thay_the_boi:
        return BI_THAY_THE
    het_han = tinh_ngay_het_han(gp)
    if het_han is None:
        return CHUA_XAC_DINH
    if het_han < hom_nay:
        return HET_HAN
    if het_han <= cong_thang(hom_nay, SO_THANG_CANH_BAO):
        return SAP_HET_HAN
    return CON_HIEU_LUC


MAU_TRANG_THAI = {
    CON_HIEU_LUC: "ok",
    SAP_HET_HAN: "canh-bao",
    HET_HAN: "loi",
    BI_THAY_THE: "xam",
    CHUA_XAC_DINH: "chua-ro",
}
