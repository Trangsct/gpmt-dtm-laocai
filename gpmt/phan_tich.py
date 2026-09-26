"""Tách số hiệu, ngày ký và số liệu từ các chuỗi ghi lộn xộn trong sổ theo dõi (mục 3.1 HUONG_DAN.md).

Nguyên tắc: đọc được gì trả nấy, kèm danh sách cảnh báo. Không đoán; chỗ không chắc trả None
và nêu lý do để người phụ trách xác nhận.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date

# ---------------------------------------------------------------- Số hiệu và ngày

# "2074/GPMT-UBND", "866/GPMT- UBND", "3010/QĐ-UBND", "150/GPMT-BTNMT"
_RE_SO_HIEU = re.compile(r"(\d{1,5})\s*/\s*((?:[A-ZĐ]+\s*-\s*)*[A-ZĐ]+)")
# "20/09/2022", "05/5//2023", "007/7/2023", "ngày18/07/2022"
_RE_NGAY = re.compile(r"(\d{1,3})\s*/\s*(\d{1,2})\s*/+\s*(\d{4})")

# Ký hiệu → (ký hiệu chuẩn, loại văn bản, cảnh báo)
KY_HIEU_GPMT = {"GPMT-UBND", "GP-UBND", "GPMT-BTNMT", "GPMT-BNNMT"}
KY_HIEU_LOI_GO = {"GPMT-UNMD": "GPMT-UBND"}
KY_HIEU_CHUA_RO = {"QĐ-UBND", "GPTN-UBND", "GPTNMT-UBND"}


@dataclass
class GiayPhepTach:
    so: int
    ky_hieu: str            # đã chuẩn hóa
    ky_hieu_goc: str
    ngay_ky: date | None
    loai_van_ban: str       # "GPMT" hoặc "chưa rõ"
    cap_dieu_chinh: bool = False   # đứng sau cụm "cấp điều chỉnh"
    canh_bao: list = field(default_factory=list)
    can_ra_soat: list = field(default_factory=list)

    @property
    def so_hieu(self):
        return f"{self.so}/{self.ky_hieu}"


def _chuan_ky_hieu(goc: str):
    kh = re.sub(r"\s+", "", goc.upper())
    canh_bao, ra_soat = [], []
    loai = "GPMT"
    if kh in KY_HIEU_LOI_GO:
        canh_bao.append(f"Ký hiệu gõ lỗi '{kh}', đã sửa thành '{KY_HIEU_LOI_GO[kh]}'")
        kh = KY_HIEU_LOI_GO[kh]
    if kh in KY_HIEU_CHUA_RO:
        loai = "chưa rõ"
        ra_soat.append(f"Ký hiệu '{kh}' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận")
    elif kh not in KY_HIEU_GPMT:
        loai = "chưa rõ"
        ra_soat.append(f"Ký hiệu lạ '{kh}' — cần xác nhận")
    if goc != kh and re.sub(r"\s+", "", goc) == kh:
        canh_bao.append(f"Ký hiệu có dấu cách thừa '{goc}'")
    return kh, loai, canh_bao, ra_soat


def tach_ngay(chuoi: str):
    """Trả (date|None, cảnh báo[]). Chịu được '05/5//2023', '007/7/2023', 'ngày18/07/2022'."""
    m = _RE_NGAY.search(chuoi or "")
    if not m:
        return None, []
    canh_bao = []
    ng, th, nam = m.group(1), m.group(2), m.group(3)
    if len(ng) > 2:
        canh_bao.append(f"Ngày ghi sai định dạng '{m.group(0)}'")
    if "//" in m.group(0):
        canh_bao.append(f"Ngày có dấu '/' thừa '{m.group(0)}'")
    try:
        return date(int(nam), int(th), int(ng)), canh_bao
    except ValueError:
        return None, [f"Ngày không hợp lệ '{m.group(0)}'"]


def tach_giay_phep(chuoi) -> list[GiayPhepTach]:
    """Tách mọi giấy phép trong một ô "Giấy phép số".

    Một ô có thể chứa 2 GP: "2568/GPMT-UBND ngày 27/12/2022, cấp điều chỉnh GPMT số 1827/GPMT-UBND ngày 16/9/2024".
    Ngày của mỗi GP là ngày đầu tiên xuất hiện sau số hiệu và trước số hiệu kế tiếp.
    """
    if chuoi is None:
        return []
    s = str(chuoi).replace("\xa0", " ").strip()
    if not s:
        return []
    ket_qua = []
    cac_so = list(_RE_SO_HIEU.finditer(s))
    for i, m in enumerate(cac_so):
        # Bỏ các khớp nằm trong một ngày (vd "20/09" không có chữ nên không khớp; phòng hờ)
        het = cac_so[i + 1].start() if i + 1 < len(cac_so) else len(s)
        doan_sau = s[m.end():het]
        ngay, cb_ngay = tach_ngay(doan_sau)
        kh, loai, cb, rs = _chuan_ky_hieu(m.group(2))
        truoc = s[cac_so[i - 1].end() if i else 0:m.start()].lower()
        gp = GiayPhepTach(
            so=int(m.group(1)), ky_hieu=kh, ky_hieu_goc=m.group(2), ngay_ky=ngay,
            loai_van_ban=loai, cap_dieu_chinh="điều chỉnh" in truoc,
            canh_bao=cb + cb_ngay, can_ra_soat=rs,
        )
        if m.group(1).startswith("0") and len(m.group(1)) > 1:
            gp.canh_bao.append(f"Số có số 0 đứng đầu '{m.group(1)}'")
        if ngay is None:
            gp.can_ra_soat.append("Sổ không ghi ngày ký — cần bổ sung")
        ket_qua.append(gp)
    return ket_qua


# ---------------------------------------------------------------- Số kiểu Việt

_RE_SO = re.compile(r"(?<![A-Za-z])\d[\d.,]*")  # bỏ số mũ trong m3, Nm3


def doc_so_viet(chuoi: str):
    """Đọc một số viết kiểu Việt: '.' ngăn hàng nghìn, ',' thập phân.

    '1.949' → 1949; '3074,5' → 3074.5; '13.887,1' → 13887.1; '09' → 9.
    Chuỗi chỉ có dấu chấm mà nhóm sau không đủ 3 chữ số ('0.7') là không chắc → None.
    """
    s = str(chuoi).strip().rstrip(".,")
    if not s or not re.fullmatch(r"\d[\d.,]*", s):
        return None
    if "." in s and "," in s:
        if s.rfind(",") < s.rfind("."):
            return None  # kiểu Anh "1,234.5" — không chắc, không đoán
        nguyen, thap_phan = s.split(",", 1)
        if not re.fullmatch(r"\d{1,3}(\.\d{3})+", nguyen) or not thap_phan.isdigit():
            return None
        return float(nguyen.replace(".", "") + "." + thap_phan)
    if "," in s:
        phan = s.split(",")
        if len(phan) != 2:
            return None
        return float(phan[0] + "." + phan[1])
    if "." in s:
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
            return float(s.replace(".", ""))
        return None
    return float(s)


# Đơn vị nhận biết được, theo thứ tự ưu tiên khớp dài trước
_DON_VI = [
    (r"m3\s*/\s*ngày\s*[.\s]?\s*đêm", "m3/ngày đêm"),
    (r"m3\s*/\s*giờ", "m3/giờ"),
    (r"m3\s*/\s*năm", "m3/năm"),
    (r"kg\s*/\s*năm", "kg/năm"),
    (r"kg\s*/\s*tháng", "kg/tháng"),
    (r"kg\s*/\s*ngày", "kg/ngày"),
    (r"tấn\s*/\s*năm", "tấn/năm"),
    (r"tấn\s*/\s*tháng", "tấn/tháng"),
    (r"tấn\s*/\s*ngày", "tấn/ngày"),
]

# Chữ cho phép đi kèm một con số mà vẫn coi là "chắc chắn" (chú thích loại nước thải…)
_CHU_CHO_PHEP = re.compile(
    r"^(ntsh|ntsx|nt|:|;|,|\.|\(bao gồm cả nước mưa qua mỏ\)|khoảng|phát sinh lớn nhất|\s)*$", re.I)


@dataclass
class SoLieu:
    goc: str
    so: float | None = None
    don_vi: str | None = None
    ghi_chu: str | None = None   # lý do không chuẩn hóa được


def doc_so_lieu(gia_tri, don_vi_mac_dinh: str) -> SoLieu:
    """Chuẩn hóa một ô số liệu chất thải. Ô kiểu số (xlrd trả float) là chắc chắn.

    Ô chữ chỉ được chuẩn hóa khi có đúng MỘT con số, đơn vị nhận biết được (hoặc không ghi đơn vị)
    và phần chữ còn lại chỉ là chú thích quen thuộc (NTSH, NTSX…).
    """
    if gia_tri is None or (isinstance(gia_tri, str) and not gia_tri.strip()):
        return SoLieu(goc="")
    if isinstance(gia_tri, (int, float)):
        so = round(float(gia_tri), 6)
        goc = str(int(so)) if so == int(so) else str(so)
        return SoLieu(goc=goc, so=so, don_vi=don_vi_mac_dinh)
    goc = " ".join(str(gia_tri).replace("\xa0", " ").split())
    cac_so = _RE_SO.findall(goc)
    if not cac_so:
        return SoLieu(goc=goc, ghi_chu="không có số")
    if len(cac_so) > 1:
        return SoLieu(goc=goc, ghi_chu="nhiều số liệu trong một ô")
    so = doc_so_viet(cac_so[0])
    if so is None:
        return SoLieu(goc=goc, ghi_chu=f"cách viết số '{cac_so[0]}' không chắc chắn")
    con_lai = goc.replace(cac_so[0], " ", 1)
    don_vi = None
    for mau, ten in _DON_VI:
        m = re.search(mau, con_lai, re.I)
        if m:
            don_vi = ten
            con_lai = con_lai[:m.start()] + " " + con_lai[m.end():]
            break
    if not _CHU_CHO_PHEP.match(con_lai.strip()):
        return SoLieu(goc=goc, ghi_chu="có chữ mô tả kèm theo, cần đọc tay")
    return SoLieu(goc=goc, so=so, don_vi=don_vi or don_vi_mac_dinh)


def quy_doi_kg_nam(so: float | None, don_vi: str | None):
    """Chỉ quy đổi khi chắc chắn (kg/năm, tấn/năm). kg/ngày, kg/tháng phụ thuộc số ngày hoạt động → None."""
    if so is None:
        return None
    if don_vi == "kg/năm":
        return so
    if don_vi == "tấn/năm":
        return so * 1000
    return None


# ---------------------------------------------------------------- Chuỗi tên

def bo_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def chuan_ten(s: str) -> str:
    """Khóa so khớp tên: bỏ dấu, chữ thường, gộp khoảng trắng, bỏ dấu câu."""
    s = bo_dau(s).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def lam_sach(s) -> str:
    if s is None:
        return ""
    if isinstance(s, float):
        return str(int(s)) if s == int(s) else str(s)
    return " ".join(str(s).replace("\xa0", " ").split())


_RE_KCN = re.compile(r"(Khu\s+công\s+nghiệp|KCN|Cụm\s+công\s+nghiệp|CCN)\s+([^,;.\n(]+)", re.I)


def tach_kcn_ccn(*chuoi) -> str | None:
    """'Lô F24, Khu công nghiệp Đông Phố Mới, …' → 'KCN Đông Phố Mới'."""
    for c in chuoi:
        m = _RE_KCN.search(" ".join((c or "").split()))
        if not m:
            continue
        loai = "CCN" if bo_dau(m.group(1)).lower().startswith(("cum", "ccn")) else "KCN"
        ten = m.group(2).strip()
        ten = re.split(r"\s+(?:tỉnh|thành phố|TP\.?|huyện|xã|phường|thị xã|thị trấn)\b", ten, 1, flags=re.I)[0]
        tu = ten.split()
        if not tu or len(tu) > 5:
            continue
        ten = " ".join(t[:1].upper() + t[1:] for t in tu)
        return f"{loai} {ten}"
    return None


SO_LA_MA = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
