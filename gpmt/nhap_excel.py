"""Nhập sổ theo dõi GPMT (Excel 97, .xls) vào CSDL — mục 3.1 HUONG_DAN.md.

Hai bước tách rời để kiểm thử được:
1. `doc_so_theo_doi(duong_dan)` — chỉ đọc Excel, trả các dòng thô đã làm sạch.
2. `nhap_vao_csdl(du_lieu)` — ghép, chuẩn hóa, gắn cờ, ghi CSDL, trả `BaoCaoNhap`.

Không bỏ qua dòng nào một cách lặng lẽ: mọi dòng bị bỏ, bị gộp hoặc bị gắn cờ đều có trong báo cáo.
"""
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from difflib import SequenceMatcher

import xlrd

from .extensions import db
from .models import ChuThe, CoSoDuAn, Gpmt, GpmtChatThai, GpmtXaThai, Vhtn
from .phan_tich import (chuan_ten, doc_so_lieu, lam_sach, quy_doi_kg_nam, tach_giay_phep,
                        tach_kcn_ccn)

SHEET_LC = "GPMT Tinh cap"
SHEET_YB = "GPMT tỉnh YB cũ"
SHEET_HUYEN = "GPMT cấp huyện cũ"
SHEET_VHTN = "VHTN"
SHEET_GPMT = [SHEET_LC, SHEET_YB, SHEET_HUYEN]

NGAY_HOP_NHAT_TINH = date(2025, 7, 1)

CO_QUAN = {
    "LC": "UBND tỉnh Lào Cai",
    "YB": "UBND tỉnh Yên Bái (cũ)",
    "BTNMT": "Bộ Tài nguyên và Môi trường",
    "BNNMT": "Bộ Nông nghiệp và Môi trường",
    "HUYEN": "UBND cấp huyện (cũ)",
}

# Cột chung của 3 sheet GPMT
C_TT, C_TEN, C_DIA_CHI, C_LOAI_HINH, C_GP, C_CONG_SUAT, C_NUOC, C_KHI, C_CTR, C_CTNH = range(10)


# ================================================================ Bước 1: đọc Excel

@dataclass
class DongGpmt:
    sheet: str
    dong: int                    # số dòng theo Excel (bắt đầu từ 1)
    nam_nhom: int | None
    nhom_phu: str | None         # nhãn nhóm không phải năm, vd "GPMT do Bộ cấp"
    tt: str
    ten: str
    dia_chi: str
    loai_hinh: str
    gp_goc: str
    cong_suat: str
    nuoc_thai: object
    khi_thai: object
    ctr: object
    ctnh: object
    ghi_chu: str = ""
    bao_cao_chap_hanh: str = ""
    vhtn: str = ""

    @property
    def nguon(self):
        return f"excel:{self.sheet}:dòng {self.dong}"


@dataclass
class DongVhtn:
    dong: int
    stt: str
    ten: str
    chu: str
    dia_chi: str
    gp_goc: str
    vhtn: str
    noi_dong: list = field(default_factory=list)   # các dòng Excel được nối vào (tên bị xuống dòng)


@dataclass
class DuLieuSo:
    gpmt: list
    vhtn: list
    bo_qua: list                  # (sheet, dòng, lý do)
    so_dong_du_lieu: Counter      # sheet → số dòng dữ liệu
    so_dong_theo_nam: dict        # sheet → Counter(năm nhóm)

    @property
    def khong_tt(self):
        """Dòng dữ liệu không có số TT (vẫn nhập) — lý do số dòng đọc được lệch với số TT cuối của sổ."""
        return [d for d in self.gpmt if not d.tt]


_RE_NAM = re.compile(r"(20\d\d)")
_LA_MA = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"}


def _o(sheet, r, c):
    return sheet.cell_value(r, c) if c < sheet.ncols else ""


def _doc_sheet_gpmt(sh, bo_qua):
    dong_du_lieu = []
    theo_nam = Counter()
    # Tiêu đề chiếm 3 dòng, có ô gộp: dữ liệu bắt đầu sau dòng có "Nước thải"
    bat_dau = 0
    for r in range(min(sh.nrows, 10)):
        if "Nước thải" in str(_o(sh, r, C_NUOC)):
            bat_dau = r + 1
            break
    nam, nhom_phu = None, None
    for r in range(bat_dau, sh.nrows):
        o = [_o(sh, r, c) for c in range(sh.ncols)]
        tt = lam_sach(o[C_TT])
        con_lai = [lam_sach(x) for x in o[1:]]
        if not any(con_lai):
            if tt:
                bo_qua.append((sh.name, r + 1, f"chỉ có số thứ tự '{tt}', các cột khác trống"))
            continue
        # Dòng nhóm năm: "I | 2022", "II | 2023", "II | 2024" (La Mã lặp), "III | Năm 2025"
        ten = lam_sach(o[C_TEN])
        if tt.upper() in _LA_MA and not any(con_lai[1:]):
            m = _RE_NAM.search(ten)
            if m:
                nam, nhom_phu = int(m.group(1)), None
                continue
        # Dòng nhãn nhóm không có TT, không có GP: "GPMT do Bộ cấp"
        if not tt and ten and not any(con_lai[1:]):
            nhom_phu = ten
            bo_qua.append((sh.name, r + 1, f"dòng nhãn nhóm '{ten}' (dùng làm nhãn cho các dòng sau)"))
            continue
        d = DongGpmt(
            sheet=sh.name, dong=r + 1, nam_nhom=nam, nhom_phu=nhom_phu, tt=tt, ten=ten,
            dia_chi=lam_sach(o[C_DIA_CHI]), loai_hinh=lam_sach(o[C_LOAI_HINH]),
            gp_goc=lam_sach(o[C_GP]), cong_suat=lam_sach(o[C_CONG_SUAT]),
            nuoc_thai=o[C_NUOC], khi_thai=o[C_KHI], ctr=o[C_CTR], ctnh=o[C_CTNH],
        )
        if sh.name == SHEET_YB:
            d.ghi_chu = lam_sach(_o(sh, r, 10))
            d.bao_cao_chap_hanh = lam_sach(_o(sh, r, 11))
        if sh.name == SHEET_HUYEN:
            d.vhtn = lam_sach(_o(sh, r, 10))
        dong_du_lieu.append(d)
        theo_nam[nam] += 1
    return dong_du_lieu, theo_nam


def _doc_sheet_vhtn(sh, bo_qua):
    ket_qua = []
    for r in range(1, sh.nrows):
        o = [lam_sach(_o(sh, r, c)) for c in range(6)]
        stt = o[0].strip(" .")
        if not any(o[1:]):
            if stt:
                bo_qua.append((sh.name, r + 1, f"chỉ có số thứ tự '{stt}'"))
            continue
        # Dòng nối: tên bị xuống dòng sang ô dưới (không STT, không chủ, không địa chỉ, không GP)
        if not stt and o[1] and not any(o[2:5]) and ket_qua:
            truoc = ket_qua[-1]
            truoc.ten = f"{truoc.ten} {o[1]}"
            truoc.noi_dong.append(r + 1)
            continue
        ket_qua.append(DongVhtn(dong=r + 1, stt=stt, ten=o[1], chu=o[2], dia_chi=o[3],
                                gp_goc=o[4], vhtn=o[5]))
    return ket_qua


def doc_so_theo_doi(duong_dan=None, noi_dung: bytes | None = None) -> DuLieuSo:
    """Đọc sổ từ đường dẫn tệp, hoặc từ nội dung tệp (bytes) khi người dùng tải lên qua trang web."""
    book = xlrd.open_workbook(file_contents=noi_dung) if noi_dung is not None else xlrd.open_workbook(duong_dan)
    ten_sheet = book.sheet_names()
    thieu = [s for s in SHEET_GPMT + [SHEET_VHTN] if s not in ten_sheet]
    if thieu:
        raise ValueError(f"Sổ thiếu sheet: {thieu}. Sheet hiện có: {ten_sheet}")
    bo_qua, gpmt, dem, theo_nam = [], [], Counter(), {}
    for s in SHEET_GPMT:
        dong, nam = _doc_sheet_gpmt(book.sheet_by_name(s), bo_qua)
        gpmt += dong
        dem[s] = len(dong)
        theo_nam[s] = nam
    vhtn = _doc_sheet_vhtn(book.sheet_by_name(SHEET_VHTN), bo_qua)
    dem[SHEET_VHTN] = len(vhtn)
    return DuLieuSo(gpmt=gpmt, vhtn=vhtn, bo_qua=bo_qua, so_dong_du_lieu=dem, so_dong_theo_nam=theo_nam)


# ================================================================ Bước 2: ghép và ghi CSDL

@dataclass
class BaoCaoNhap:
    so_dong_du_lieu: Counter = field(default_factory=Counter)
    so_dong_theo_nam: dict = field(default_factory=dict)
    so_gpmt_tao: int = 0
    so_co_so: int = 0
    so_chu_the: int = 0
    so_vhtn: int = 0
    bo_qua: list = field(default_factory=list)
    gop_trung: list = field(default_factory=list)      # (nguồn giữ, nguồn gộp, số hiệu)
    canh_bao: list = field(default_factory=list)       # (nguồn, số hiệu, nội dung) — đã tự sửa, chỉ liệt kê
    ghep_vhtn: Counter = field(default_factory=Counter)
    khong_tt: list = field(default_factory=list)       # (sheet, dòng, tên)


_TIEN_TO_THUA = re.compile(r"^(Cấp phép môi trường cho|Giấy phép môi trường cho|Cấp GPMT)\s+", re.I)
_BAT_DAU_DU_AN = re.compile(
    r"^(Dự án|DA |dự án|Nhà máy|NM |Khách sạn|Bệnh vi|Trụ sở|Cơ sở|Khu |Tổ hợp|Trang trại|Mỏ |Trung tâm|"
    r"Xưởng|Hệ thống|Cấp GPMT|Công trình|Tòa nhà)", re.I)
_BAT_DAU_TO_CHUC = re.compile(
    r"^(Công ty|Cty|Ban |BQL|Chi nhánh|Hợp tác|HTX|Sở |Văn phòng|Doanh nghiệp|Tổng công ty|Liên d|Viễn thông|"
    r"Trung tâm|Bộ |BCH)", re.I)


def _tach_ten_chu_yb(s):
    """Sheet YB gộp 'Tên cơ sở/ Chủ cơ sở': '… Eurostark - Công ty CP …' hoặc '… của Công ty …'."""
    for mau in (" - ", " của ", "-"):
        i = s.rfind(mau)
        if i > 0:
            phai = s[i + len(mau):].strip()
            if _BAT_DAU_TO_CHUC.match(phai):
                return s[:i].strip(" -"), phai
    return s, ""


def _ten_chu_tu_dong(d: DongGpmt):
    """Trả (tên cơ sở, chủ cơ sở, địa điểm, loại hình) theo cách ghi của từng sheet."""
    if d.sheet == SHEET_LC:
        chu = _TIEN_TO_THUA.sub("", d.ten)
        dia_chi_chu = ""
        if ", địa chỉ" in chu:
            chu, dia_chi_chu = chu.split(", địa chỉ", 1)
        # Sheet LC ghi không thống nhất: cột 3 lúc là tên dự án, lúc là loại hình
        if _BAT_DAU_DU_AN.match(d.loai_hinh) or len(d.loai_hinh) > 45:
            ten, dia_diem, loai_hinh = d.loai_hinh, d.dia_chi, ""
        else:
            ten, dia_diem, loai_hinh = d.dia_chi, d.dia_chi, d.loai_hinh
        return _TIEN_TO_THUA.sub("", ten).strip(" :-"), chu.strip(), dia_diem, loai_hinh
    if d.sheet == SHEET_YB:
        ten, chu = _tach_ten_chu_yb(d.ten)
        return ten, chu, d.dia_chi, d.loai_hinh
    return d.ten, "", d.dia_chi, d.loai_hinh


def do_giong(a, b):
    """Độ giống của hai tên (0–1): lấy max của tỉ lệ chuỗi và tỉ lệ từ chung trên tên ngắn hơn."""
    a, b = chuan_ten(a), chuan_ten(b)
    if not a or not b:
        return 0.0
    ta, tb = set(a.split()), set(b.split())
    return max(SequenceMatcher(None, a, b).ratio(), len(ta & tb) / min(len(ta), len(tb)))


def _khoa(so, ngay, ky_hieu):
    """Khóa ghép: số + ngày + cơ quan (phần sau '-'), bỏ qua khác biệt GP/GPMT trong ký hiệu."""
    return (so, ngay, (ky_hieu or "").split("-")[-1])


def _co_quan(sheet, ky_hieu, ngay):
    duoi = (ky_hieu or "").split("-")[-1]
    if duoi in ("BTNMT", "BNNMT"):
        return CO_QUAN[duoi], None
    if sheet == SHEET_LC:
        return CO_QUAN["LC"], None
    if sheet == SHEET_YB:
        if ngay and ngay >= NGAY_HOP_NHAT_TINH:
            return None, ("Ngày ký sau khi hợp nhất tỉnh (01/7/2025) nhưng nằm ở sheet 'GPMT tỉnh YB cũ' — "
                          "cần xác nhận cơ quan cấp")
        return CO_QUAN["YB"], None
    if sheet == SHEET_HUYEN:
        return CO_QUAN["HUYEN"], "GP cấp huyện cũ: sổ không ghi UBND huyện nào — cần xác nhận cơ quan cấp"
    return None, "Chưa xác định được cơ quan cấp"


_VHTN_KHONG_PHAI = re.compile(r"không thuộc đối tượng", re.I)
_VHTN_XONG = re.compile(r"^(đã vhtn|đã báo cáo vhtn|đã có báo cáo vhtn)$", re.I)
_VHTN_DANG = re.compile(r"^đã có tb vhtn$", re.I)
_DKMT = re.compile(r"đã thực hiện (dkmt|đkmt)|dã thực hiện đkmt|đã thực hiện đkmt", re.I)


def tach_xa_phuong(dia_chi):
    """'Lô F24, KCN Đông Phố Mới, tỉnh Lào Cai' → None; 'Xã Lương Thịnh, huyện Trấn Yên, tỉnh Lào Cai'
    → 'Xã Lương Thịnh'; 'Xã Văn Bàn và xã Võ Lao, tỉnh Lào Cai' → giữ cả cụm."""
    s = " ".join((dia_chi or "").split())
    s = re.sub(r",?\s*tỉnh Lào Cai\s*$", "", s, flags=re.I)
    s = re.sub(r",\s*huyện [^,]+", "", s, flags=re.I)
    m = re.search(r"\b(Xã|Phường|Phương)\s+\S.*$", s, flags=re.I)
    if not m:
        return None
    ket_qua = m.group(0).strip(" ,")
    ket_qua = re.sub(r"^Phương\b", "Phường", ket_qua)
    return ket_qua[:1].upper() + ket_qua[1:]


def _trang_thai_vhtn(chu):
    c = chu.strip()
    if _VHTN_KHONG_PHAI.search(c):
        return "không phải VHTN"
    if _VHTN_XONG.match(c):
        return "đã xong"
    if _VHTN_DANG.match(c):
        return "đang"
    return "chưa rõ"


class _BoNhap:
    def __init__(self):
        self.bc = BaoCaoNhap()
        self.chu_the = {}      # khóa tên → ChuThe
        self.co_so = {}        # (khóa tên, id chủ) → CoSoDuAn
        self.gp_theo_khoa = defaultdict(list)
        self.tat_ca_gp = []

    # ----- danh mục
    def lay_chu_the(self, ten):
        ten = " ".join((ten or "").split())
        if not ten:
            return None
        k = chuan_ten(ten)
        if k not in self.chu_the:
            ct = ChuThe(ten=ten)
            db.session.add(ct)
            self.chu_the[k] = ct
        return self.chu_the[k]

    def lay_co_so(self, ten, chu, **thuoc_tinh):
        ct = self.lay_chu_the(chu)
        k = (chuan_ten(ten), chuan_ten(chu or ""))
        cs = self.co_so.get(k)
        if cs is None:
            cs = CoSoDuAn(ten=ten or "(chưa có tên)", chu_the=ct)
            db.session.add(cs)
            self.co_so[k] = cs
        for ten_tt, gt in thuoc_tinh.items():
            if gt and not getattr(cs, ten_tt):
                setattr(cs, ten_tt, gt)
        return cs

    def canh_bao(self, nguon, so_hieu, noi_dung):
        self.bc.canh_bao.append((nguon, so_hieu or "(chưa có số)", noi_dung))

    # ----- các sheet GPMT
    def nhap_dong_gpmt(self, d: DongGpmt):
        ten, chu, dia_diem, loai_hinh = _ten_chu_tu_dong(d)
        dia_ban = {SHEET_LC: "LC", SHEET_YB: "YB"}.get(d.sheet)
        cs = self.lay_co_so(ten, chu, dia_diem=dia_diem, loai_hinh=loai_hinh, dia_ban_cu=dia_ban,
                            cong_suat_goc=d.cong_suat, kcn_ccn=tach_kcn_ccn(d.dia_chi, d.ten, d.loai_hinh))
        cac_gp = tach_giay_phep(d.gp_goc)
        ghi_chu_goc = {k: v for k, v in {
            "Tên cơ sở (sổ)": d.ten, "Địa chỉ (sổ)": d.dia_chi, "Loại hình (sổ)": d.loai_hinh,
            "Ghi chú": d.ghi_chu, "Báo cáo việc chấp hành": d.bao_cao_chap_hanh, "VHTN (sổ)": d.vhtn,
            "Nhóm trong sổ": d.nhom_phu}.items() if v}
        chinh = None
        for i, g in enumerate(cac_gp or [None]):
            gp = Gpmt(co_so=cs, so_hieu_goc=d.gp_goc or None, nguon_du_lieu=d.nguon,
                      cong_suat_goc=d.cong_suat or None,
                      ghi_chu_goc=json.dumps(ghi_chu_goc, ensure_ascii=False) if ghi_chu_goc else None)
            db.session.add(gp)
            if g is None:
                gp.them_ly_do("Sổ không ghi số giấy phép")
                gp.nam_cap = d.nam_nhom
                gp.co_quan_cap, ly_do = _co_quan(d.sheet, None, None)
            else:
                gp.so, gp.ky_hieu, gp.so_hieu, gp.ngay_ky = g.so, g.ky_hieu, g.so_hieu, g.ngay_ky
                gp.loai_van_ban = g.loai_van_ban
                for x in g.can_ra_soat:
                    gp.them_ly_do(x)
                for x in g.canh_bao:
                    self.canh_bao(d.nguon, g.so_hieu, x)
                gp.co_quan_cap, ly_do = _co_quan(d.sheet, g.ky_hieu, g.ngay_ky)
                gp.nam_cap = g.ngay_ky.year if g.ngay_ky else d.nam_nhom
                if i == 0 and g.ngay_ky and d.nam_nhom and g.ngay_ky.year != d.nam_nhom:
                    gp.them_ly_do(f"Năm ký ({g.ngay_ky.year}) khác nhóm năm của sổ ({d.nam_nhom}) — "
                                  "kiểm tra lại ngày ký")
                if len(cac_gp) > 1:
                    gp.them_ly_do(f"Ô 'Giấy phép số' chứa {len(cac_gp)} giấy phép — đã tách thành "
                                  f"{len(cac_gp)} bản ghi, cần xác nhận")
                if i > 0 and g.cap_dieu_chinh:
                    gp.loai_cap = "cấp điều chỉnh"
                    gp.dieu_chinh_cho = chinh
                self.gp_theo_khoa[_khoa(g.so, g.ngay_ky, g.ky_hieu)].append(gp)
            if ly_do:
                gp.them_ly_do(ly_do)
            if re.search(r"\(cấp lại\)", d.loai_hinh + d.dia_chi + d.ten, re.I):
                gp.loai_cap = "cấp lại"
                gp.them_ly_do("Sổ ghi 'cấp lại' nhưng không ghi GP bị thay thế — cần xác định GP cũ")
            if _DKMT.search(d.ghi_chu):
                gp.lua_chon_chuyen_tiep = "Chuyển sang đăng ký môi trường"
                gp.them_ly_do(f"Ghi chú sổ: '{d.ghi_chu}' — cần xác nhận lựa chọn chuyển tiếp")
            if i == 0:
                chinh = gp
                self._chat_thai(gp, d)
                if d.vhtn:
                    db.session.add(Vhtn(gpmt=gp, trang_thai=_trang_thai_vhtn(d.vhtn), ghi_chu_goc=d.vhtn))
                    self.bc.so_vhtn += 1
            self.tat_ca_gp.append(gp)

    def _chat_thai(self, gp, d):
        muc = [("xa", "nước thải", d.nuoc_thai, "m3/ngày đêm"),
               ("xa", "khí thải", d.khi_thai, "m3/giờ"),
               ("ct", "CTR thông thường (sổ)", d.ctr, "kg/năm"),
               ("ct", "CTNH", d.ctnh, "kg/năm")]
        for kieu, loai, gia_tri, don_vi in muc:
            sl = doc_so_lieu(gia_tri, don_vi)
            if not sl.goc:
                continue
            if (isinstance(gia_tri, float) and gia_tri == int(gia_tri) and 2015 <= gia_tri <= 2035
                    and loai == "nước thải"):
                sl.so, sl.don_vi = None, None
                gp.them_ly_do(f"Ô {loai} ghi '{sl.goc}' — nghi nhập nhầm năm vào cột số liệu")
            if sl.ghi_chu and sl.ghi_chu != "không có số":
                self.canh_bao(d.nguon, gp.so_hieu, f"{loai}: '{sl.goc}' giữ nguyên văn ({sl.ghi_chu})")
            if kieu == "xa":
                db.session.add(GpmtXaThai(gpmt=gp, loai=loai, ten_dong="Theo sổ theo dõi",
                                          luu_luong_goc=sl.goc, luu_luong_max=sl.so, don_vi=sl.don_vi))
            else:
                db.session.add(GpmtChatThai(gpmt=gp, loai=loai, khoi_luong_goc=sl.goc, khoi_luong_so=sl.so,
                                            don_vi=sl.don_vi,
                                            khoi_luong_kg_nam=quy_doi_kg_nam(sl.so, sl.don_vi)))

    # ----- trùng lặp trong các sheet GPMT
    def xu_ly_trung(self):
        for khoa, ds in self.gp_theo_khoa.items():
            if len(ds) < 2:
                continue
            giu = ds[0]
            for gp in ds[1:]:
                cung_chu = (gp.co_so.chu_the is giu.co_so.chu_the or
                            do_giong(str(gp.co_so.chu_the or ""), str(giu.co_so.chu_the or "")) >= 0.9)
                cung_co_so = gp.co_so is giu.co_so or (cung_chu and do_giong(gp.co_so.ten, giu.co_so.ten) >= 0.5)
                if cung_co_so:
                    self.bc.gop_trung.append((giu.nguon_du_lieu, gp.nguon_du_lieu, giu.so_hieu))
                    giu.nguon_du_lieu += f"; {gp.nguon_du_lieu} (dòng trùng, đã gộp)"
                    if gp.so_hieu != giu.so_hieu:
                        self.canh_bao(gp.nguon_du_lieu, gp.so_hieu,
                                      f"Dòng trùng ghi ký hiệu khác ('{gp.so_hieu}' so với '{giu.so_hieu}')")
                    for x in gp.ds_ly_do:
                        if not x.startswith("Ô 'Giấy phép số'"):
                            giu.them_ly_do(x)
                    self._xoa(gp)
                else:
                    ly_do = (f"Trùng số hiệu và ngày ký với bản ghi khác nhưng khác cơ sở "
                             f"('{giu.co_so.ten[:60]}' / '{gp.co_so.ten[:60]}') — cần đối chiếu bản gốc")
                    giu.them_ly_do(ly_do)
                    gp.them_ly_do(ly_do)
            self.gp_theo_khoa[khoa] = [g for g in ds if g in self.tat_ca_gp]

    def _xoa(self, gp):
        """Bỏ bản ghi trùng (chưa ghi xuống CSDL); expunge lan sang các bảng con."""
        self.tat_ca_gp.remove(gp)
        gp.co_so = None
        db.session.expunge(gp)

    # ----- sheet VHTN
    def ghep_vhtn(self, v: DongVhtn):
        nguon = f"excel:{SHEET_VHTN}:dòng {v.dong}"
        cac_gp = tach_giay_phep(v.gp_goc)
        if not cac_gp:
            self.bc.ghep_vhtn["không có số GP"] += 1
            self.canh_bao(nguon, None, f"Dòng VHTN '{v.ten}' không ghi số GP — chưa ghép được")
            return
        xa_moi = tach_xa_phuong(v.dia_chi)
        if xa_moi and v.dia_chi.strip().startswith("Phương "):
            self.canh_bao(nguon, None, f"Địa chỉ '{v.dia_chi}' viết 'Phương', đã hiểu là 'Phường'")
        for g in cac_gp:
            ung_vien = self._tim_theo_so(g)
            gp = max(ung_vien, key=lambda x: do_giong(x.co_so.ten, v.ten)) if ung_vien else None
            cach_ghep = "theo số hiệu"
            if gp is None:
                gp = self._ghep_theo_ten(v)
                cach_ghep = "theo tên (sổ chính không ghi số)"
                if gp is not None:
                    gp.so, gp.ky_hieu, gp.so_hieu, gp.ngay_ky = g.so, g.ky_hieu, g.so_hieu, g.ngay_ky
                    gp.loai_van_ban = g.loai_van_ban
                    gp.nam_cap = g.ngay_ky.year if g.ngay_ky else gp.nam_cap
                    gp.ly_do_ra_soat = "\n".join(x for x in gp.ds_ly_do if x != "Sổ không ghi số giấy phép")
                    gp.can_ra_soat = bool(gp.ly_do_ra_soat)
                    for x in g.can_ra_soat:
                        gp.them_ly_do(x)
                    gp.them_ly_do(f"Số GP lấy từ sheet VHTN dòng {v.dong}, ghép với sổ chính theo tên gần đúng "
                                  "— cần duyệt")
                    self.gp_theo_khoa[_khoa(g.so, g.ngay_ky, g.ky_hieu)].append(gp)
            if gp is None:
                gp = self._tao_tu_vhtn(v, g, nguon, xa_moi)
                cach_ghep = "tạo mới (chỉ có trong sheet VHTN)"
            else:
                gp.nguon_du_lieu += f"; {nguon}"
            self.bc.ghep_vhtn[cach_ghep] += 1
            cs = gp.co_so
            # Tên, chủ, địa chỉ ở sheet VHTN sạch hơn và đã theo ĐVHC mới
            if v.ten and cach_ghep != "tạo mới (chỉ có trong sheet VHTN)":
                cs.ten = v.ten.strip()
            if v.chu:
                ct = self.lay_chu_the(v.chu)
                if cs.chu_the is not ct:
                    cs.chu_the = ct
            if xa_moi:
                cs.xa_phuong_moi = xa_moi
            if not cs.kcn_ccn:
                cs.kcn_ccn = tach_kcn_ccn(v.dia_chi, v.ten)
            if v.vhtn:
                if not any(x.ghi_chu_goc == v.vhtn for x in gp.vhtn):
                    db.session.add(Vhtn(gpmt=gp, trang_thai=_trang_thai_vhtn(v.vhtn), ghi_chu_goc=v.vhtn))
                    self.bc.so_vhtn += 1
                if _DKMT.search(v.vhtn) and not gp.lua_chon_chuyen_tiep:
                    gp.lua_chon_chuyen_tiep = "Chuyển sang đăng ký môi trường"
                    gp.them_ly_do(f"Sheet VHTN ghi: '{v.vhtn}' — cần xác nhận lựa chọn chuyển tiếp")

    def _tim_theo_so(self, g):
        """Bản ghi cùng số + cơ quan; ngày phải trùng, trừ khi một bên không ghi ngày."""
        duoi = _khoa(g.so, None, g.ky_hieu)[2]
        return [gp for (so, ngay, d), ds in self.gp_theo_khoa.items()
                if so == g.so and d == duoi and (ngay == g.ngay_ky or ngay is None or g.ngay_ky is None)
                for gp in ds]

    def _ghep_theo_ten(self, v):
        tot, diem = None, 0.0
        for gp in self.tat_ca_gp:
            if gp.so_hieu:
                continue
            d = max(do_giong(gp.co_so.ten, v.ten),
                    do_giong(gp.co_so.ten + " " + str(gp.co_so.chu_the or ""), v.ten + " " + v.chu))
            if d > diem:
                tot, diem = gp, d
        return tot if diem >= 0.8 else None

    def _tao_tu_vhtn(self, v, g, nguon, xa_moi):
        cs = self.lay_co_so(v.ten, v.chu, dia_diem=v.dia_chi, xa_phuong_moi=xa_moi,
                            kcn_ccn=tach_kcn_ccn(v.dia_chi, v.ten))
        duoi = (g.ky_hieu or "").split("-")[-1]
        gp = Gpmt(co_so=cs, so=g.so, ky_hieu=g.ky_hieu, so_hieu=g.so_hieu, ngay_ky=g.ngay_ky,
                  so_hieu_goc=v.gp_goc, loai_van_ban=g.loai_van_ban, nguon_du_lieu=nguon,
                  nam_cap=g.ngay_ky.year if g.ngay_ky else None,
                  co_quan_cap=CO_QUAN.get(duoi))
        db.session.add(gp)
        for x in g.can_ra_soat:
            gp.them_ly_do(x)
        gp.them_ly_do("Chỉ có trong sheet VHTN, không có ở 3 sheet GPMT — cần bổ sung thông tin"
                      + ("" if gp.co_quan_cap else " và cơ quan cấp"))
        self.gp_theo_khoa[_khoa(g.so, g.ngay_ky, g.ky_hieu)].append(gp)
        self.tat_ca_gp.append(gp)
        return gp


def nhap_vao_csdl(du_lieu: DuLieuSo) -> BaoCaoNhap:
    """Ghi dữ liệu sổ vào CSDL đang trống. Gọi trong app context; tự commit."""
    if db.session.query(Gpmt.id).filter(Gpmt.nguon_du_lieu.like("excel:%")).first():
        raise RuntimeError("CSDL đã có dữ liệu nhập từ sổ Excel. Dùng lệnh 'xoa-du-lieu-nhap' trước nếu muốn nhập lại.")
    bn = _BoNhap()
    bn.bc.so_dong_du_lieu = du_lieu.so_dong_du_lieu
    bn.bc.so_dong_theo_nam = du_lieu.so_dong_theo_nam
    bn.bc.bo_qua = list(du_lieu.bo_qua)
    bn.bc.khong_tt = [(d.sheet, d.dong, d.ten) for d in du_lieu.khong_tt]
    for d in du_lieu.gpmt:
        bn.nhap_dong_gpmt(d)
    bn.xu_ly_trung()
    for v in du_lieu.vhtn:
        bn.ghep_vhtn(v)
    for v in du_lieu.vhtn:
        for dong in v.noi_dong:
            bn.canh_bao(f"excel:{SHEET_VHTN}:dòng {dong}", None,
                        f"Tên cơ sở bị xuống dòng, đã nối vào dòng {v.dong}")
    db.session.flush()
    # Cơ sở / chủ thể mồ côi (do gộp dòng trùng hoặc đổi chủ theo sheet VHTN)
    for cs in list(bn.co_so.values()):
        if not cs.gpmt:
            db.session.delete(cs)
    db.session.flush()
    for ct in list(bn.chu_the.values()):
        if not ct.co_so:
            db.session.delete(ct)
    db.session.commit()
    bn.bc.so_gpmt_tao = db.session.query(Gpmt).count()
    bn.bc.so_co_so = db.session.query(CoSoDuAn).count()
    bn.bc.so_chu_the = db.session.query(ChuThe).count()
    return bn.bc


# ================================================================ Báo cáo nhập

def viet_bao_cao(bc: BaoCaoNhap, ten_tep_so: str) -> str:
    dong = [f"# Báo cáo nhập sổ theo dõi GPMT — {date.today().strftime('%d/%m/%Y')}", "",
            f"Tệp nguồn: `{ten_tep_so}`", "", "## 1. Số dòng đã đọc", "",
            "| Sheet | Dòng dữ liệu | Theo nhóm năm của sổ |", "|---|---:|---|"]
    for s, n in bc.so_dong_du_lieu.items():
        theo_nam = bc.so_dong_theo_nam.get(s)
        nam = ", ".join(f"{k or 'không có nhóm'}: {v}" for k, v in sorted(theo_nam.items(), key=lambda x: x[0] or 0)) \
            if theo_nam else ""
        dong.append(f"| {s} | {n} | {nam} |")
    if bc.khong_tt:
        dong += ["", f"Trong đó **{len(bc.khong_tt)} dòng không có số TT** nhưng có đủ dữ liệu, vẫn nhập "
                     "(vì vậy số dòng đọc được có thể lớn hơn số TT cuối cùng của sheet):", ""]
        dong += [f"- {a}, dòng {b}: {c[:90]}" for a, b, c in bc.khong_tt]
    dong += ["", "## 2. Kết quả trong CSDL", "",
             f"- Bản ghi GPMT: **{bc.so_gpmt_tao}**",
             f"- Cơ sở/dự án: {bc.so_co_so}; chủ cơ sở: {bc.so_chu_the}",
             f"- Bản ghi VHTN có nội dung: {bc.so_vhtn}",
             "- Dòng sheet VHTN ghép vào GPMT: " + ", ".join(f"{k}: {v}" for k, v in bc.ghep_vhtn.items()),
             f"- Dòng trùng đã gộp: {len(bc.gop_trung)}", ""]
    ra_soat = db.session.query(Gpmt).filter(Gpmt.can_ra_soat.is_(True)).order_by(Gpmt.nguon_du_lieu).all()
    dem_ly_do = Counter()
    for gp in ra_soat:
        for x in gp.ds_ly_do:
            dem_ly_do[re.sub(r"'[^']*'|\([^)]*\)|\d+", "…", x)] += 1
    dong += [f"## 3. Bản ghi gắn cờ `can_ra_soat`: {len(ra_soat)}", "", "### Nhóm lý do", "",
             "| Lý do | Số bản ghi |", "|---|---:|"]
    dong += [f"| {k} | {v} |" for k, v in dem_ly_do.most_common()]
    dong += ["", "### Danh sách chi tiết", "", "| Số hiệu | Cơ sở | Nguồn | Lý do |", "|---|---|---|---|"]
    for gp in ra_soat:
        ten = (gp.co_so.ten if gp.co_so else "")[:80].replace("|", "/")
        dong.append(f"| {gp.so_hieu or '(chưa có số)'} | {ten} | {gp.nguon_du_lieu.split(';')[0]} | "
                    f"{'<br>'.join(x.replace('|', '/') for x in gp.ds_ly_do)} |")
    dong += ["", f"## 4. Dòng trùng đã gộp: {len(bc.gop_trung)}", "", "| Số hiệu | Giữ | Gộp vào |", "|---|---|---|"]
    dong += [f"| {sh} | {a} | {b} |" for a, b, sh in bc.gop_trung]
    dong += ["", f"## 5. Cảnh báo đã tự xử lý (không gắn cờ, chỉ liệt kê): {len(bc.canh_bao)}", "",
             "| Nguồn | Số hiệu | Nội dung |", "|---|---|---|"]
    dong += [f"| {a} | {b} | {c.replace('|', '/')} |" for a, b, c in bc.canh_bao]
    dong += ["", f"## 6. Dòng bỏ qua: {len(bc.bo_qua)}", "", "| Sheet | Dòng | Lý do |", "|---|---:|---|"]
    dong += [f"| {a} | {b} | {c} |" for a, b, c in bc.bo_qua]
    return "\n".join(dong) + "\n"
