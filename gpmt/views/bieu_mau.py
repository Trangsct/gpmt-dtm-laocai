"""Biểu mẫu khai báo theo danh sách trường — dùng chung cho mọi bảng nhập tay.

Mỗi trường: (tên cột, nhãn, kiểu, tùy chọn). Kiểu: text, textarea, date, int, float, bool, chon (danh sách
cố định), goi_y (ô chữ có gợi ý), fk (khóa ngoại — hàm trả danh sách (id, nhãn)).
"""
from dataclasses import dataclass, field
from datetime import date

from ..models import TRANG_THAI_HO_SO, TRANG_THAI_VHTN

NHOM_DU_AN = ["", "I", "II", "III", "IV"]
LOAI_CAP = ["", "cấp mới", "cấp điều chỉnh", "cấp lại"]
DIA_BAN_CU = ["", "LC", "YB"]
LUA_CHON_CHUYEN_TIEP = ["", "Tiếp tục sử dụng GPMT đến hết hạn", "Chuyển sang đăng ký môi trường"]
LOAI_XA_THAI = ["nước thải", "khí thải", "ồn-rung"]
LOAI_CHAT_THAI = ["CTNH", "CTRCNTT", "CTRSH", "CTR thông thường (sổ)", "khác"]
LOAI_HO_SO = ["GPMT cấp mới", "GPMT cấp điều chỉnh", "GPMT cấp lại", "GPMT (chưa rõ loại cấp)", "ĐTM"]
LOAI_CHU_THE = ["", "doanh nghiệp", "ban QLDA", "đơn vị sự nghiệp", "cơ quan nhà nước", "hợp tác xã", "khác"]
CO_QUAN_GOI_Y = ["UBND tỉnh Lào Cai", "UBND tỉnh Yên Bái (cũ)", "UBND cấp huyện (cũ)",
                 "Bộ Nông nghiệp và Môi trường", "Bộ Tài nguyên và Môi trường"]


@dataclass
class Truong:
    ten: str
    nhan: str
    kieu: str = "text"
    lua_chon: object = None       # list hoặc hàm
    bat_buoc: bool = False
    goi_y: str = ""
    noi_bo: bool = False          # ẩn với tài khoản bên ngoài

    def ds_lua_chon(self):
        return self.lua_chon() if callable(self.lua_chon) else (self.lua_chon or [])


@dataclass
class BieuMau:
    truong: list = field(default_factory=list)

    def gia_tri_hien(self, obj, t: Truong):
        v = getattr(obj, t.ten, None) if obj is not None else None
        if v is None:
            return ""
        if t.kieu == "date":
            return v.isoformat()
        if t.kieu == "float":
            return f"{v:g}"
        return v

    def dien(self, obj, form) -> list[str]:
        """Ghi dữ liệu form vào obj. Trả danh sách lỗi (rỗng = hợp lệ). Chưa commit."""
        loi = []
        for t in self.truong:
            if t.kieu == "bool":
                setattr(obj, t.ten, form.get(t.ten) == "1")
                continue
            tho = (form.get(t.ten) or "").strip()
            if not tho:
                if t.bat_buoc:
                    loi.append(f"Chưa nhập '{t.nhan}'.")
                setattr(obj, t.ten, None)
                continue
            try:
                if t.kieu == "date":
                    gt = date.fromisoformat(tho)
                elif t.kieu in ("int", "fk"):
                    gt = int(tho)
                elif t.kieu == "float":
                    gt = float(tho.replace(",", "."))
                elif t.kieu == "chon":
                    hop_le = [x[0] if isinstance(x, tuple) else x for x in t.ds_lua_chon()]
                    if tho not in hop_le:
                        raise ValueError
                    gt = tho
                else:
                    gt = tho
            except ValueError:
                loi.append(f"'{t.nhan}' không hợp lệ: {tho}")
                continue
            setattr(obj, t.ten, gt)
        return loi


def _ds_co_so():
    from ..extensions import db
    from ..models import CoSoDuAn
    return [(c.id, c.ten[:120]) for c in db.session.query(CoSoDuAn).order_by(CoSoDuAn.ten)]


def _ds_chu_the():
    from ..extensions import db
    from ..models import ChuThe
    return [(c.id, c.ten[:120]) for c in db.session.query(ChuThe).order_by(ChuThe.ten)]


def _ds_gpmt():
    from ..extensions import db
    from ..models import Gpmt
    return [(g.id, f"{g} — {(g.co_so.ten if g.co_so else '')[:70]}")
            for g in db.session.query(Gpmt).order_by(Gpmt.ngay_ky.desc().nulls_last())]


def _ds_dtm():
    from ..extensions import db
    from ..models import Dtm
    return [(d.id, f"{d.so_qd or '(chưa có số)'} — {(d.co_so.ten if d.co_so else '')[:70]}")
            for d in db.session.query(Dtm).order_by(Dtm.ngay_qd.desc().nulls_last())]


BM_GPMT = BieuMau([
    Truong("so_hieu", "Số hiệu", goi_y="vd 2519/GPMT-UBND — ký hiệu lấy theo trang bìa"),
    Truong("ngay_ky", "Ngày ký", "date", goi_y="PDF ký số: đọc số/ngày trên ảnh trang 1, không dựa vào lớp chữ"),
    Truong("co_quan_cap", "Cơ quan cấp", "goi_y", CO_QUAN_GOI_Y),
    Truong("nguoi_ky", "Người ký"),
    Truong("loai_van_ban", "Loại văn bản", "chon", ["GPMT", "chưa rõ"]),
    Truong("loai_cap", "Loại cấp", "chon", LOAI_CAP),
    Truong("co_so_du_an_id", "Cơ sở / dự án", "fk", _ds_co_so, bat_buoc=True),
    Truong("thoi_han_nam", "Thời hạn (năm)", "float", goi_y="Đọc tại Điều 3 của GP. Không suy từ nhóm dự án."),
    Truong("ngay_het_han_nhap_tay", "Ngày hết hạn (nếu GP ghi cụ thể)", "date"),
    Truong("thay_the_gpmt_id", "Thay thế GP (GP cũ hết hiệu lực)", "fk", _ds_gpmt,
           goi_y="Chỉ chọn khi GP này ghi rõ 'GP số … hết hiệu lực'"),
    Truong("dieu_chinh_gpmt_id", "Điều chỉnh cho GP", "fk", _ds_gpmt),
    Truong("lua_chon_chuyen_tiep", "Lựa chọn chuyển tiếp (NĐ 48/2026)", "chon", LUA_CHON_CHUYEN_TIEP),
    Truong("qd_doan_kiem_tra", "QĐ thành lập đoàn kiểm tra", noi_bo=True),
    Truong("to_trinh", "Tờ trình của Sở", noi_bo=True),
    Truong("van_ban_de_nghi", "Văn bản đề nghị / bổ sung của chủ cơ sở", "textarea", noi_bo=True),
    Truong("cong_suat_goc", "Công suất (nguyên văn)", "textarea"),
    Truong("tep_pdf", "Tệp PDF gốc", goi_y="vd 2519_GPMT-UBND.pdf; trùng số giữa các năm thêm _2022"),
    Truong("cong_khai", "Đã công khai trên Cổng TTĐT", "bool"),
    Truong("can_ra_soat", "Cần rà soát", "bool", noi_bo=True),
    Truong("ly_do_ra_soat", "Lý do rà soát (mỗi dòng một lý do)", "textarea", noi_bo=True),
])

BM_CO_SO = BieuMau([
    Truong("ten", "Tên cơ sở / dự án", "textarea", bat_buoc=True),
    Truong("chu_the_id", "Chủ cơ sở", "fk", _ds_chu_the),
    Truong("dia_diem", "Địa điểm (như ghi trong GP)", "textarea"),
    Truong("xa_phuong_moi", "Xã/phường (ĐVHC mới)"),
    Truong("dia_ban_cu", "Địa bàn cũ", "chon", DIA_BAN_CU),
    Truong("kcn_ccn", "KCN / CCN"),
    Truong("loai_hinh", "Loại hình sản xuất"),
    Truong("nhom_du_an", "Nhóm theo Luật BVMT", "chon", NHOM_DU_AN),
    Truong("dien_tich", "Diện tích"),
    Truong("cong_suat_goc", "Quy mô, công suất", "textarea"),
    Truong("toa_do_lat", "Vĩ độ (WGS84, tùy chọn)", "float"),
    Truong("toa_do_lng", "Kinh độ (WGS84, tùy chọn)", "float"),
    Truong("ghi_chu", "Ghi chú nội bộ", "textarea", noi_bo=True),
])

BM_CHU_THE = BieuMau([
    Truong("ten", "Tên chủ cơ sở", bat_buoc=True),
    Truong("ma_so_thue", "Mã số thuế"),
    Truong("dia_chi_tru_so", "Địa chỉ trụ sở", "textarea"),
    Truong("loai", "Loại", "chon", LOAI_CHU_THE),
    Truong("ghi_chu", "Ghi chú", "textarea", noi_bo=True),
])

BM_XA_THAI = BieuMau([
    Truong("loai", "Loại", "chon", LOAI_XA_THAI, bat_buoc=True),
    Truong("ten_dong", "Tên dòng thải"),
    Truong("luu_luong_goc", "Lưu lượng (nguyên văn)"),
    Truong("luu_luong_max", "Lưu lượng xả lớn nhất (số)", "float"),
    Truong("don_vi", "Đơn vị", "goi_y", ["m3/ngày đêm", "m3/giờ"]),
    Truong("quy_chuan", "Quy chuẩn"),
    Truong("nguon_tiep_nhan", "Nguồn tiếp nhận", "textarea"),
    Truong("toa_do_vn2000", "Tọa độ điểm xả (VN-2000)"),
    Truong("cong_trinh_xu_ly", "Công trình xử lý", "textarea"),
])

BM_CHAT_THAI = BieuMau([
    Truong("loai", "Loại", "chon", LOAI_CHAT_THAI, bat_buoc=True),
    Truong("khoi_luong_goc", "Khối lượng (nguyên văn)"),
    Truong("khoi_luong_so", "Khối lượng (số)", "float"),
    Truong("don_vi", "Đơn vị", "goi_y", ["kg/năm", "tấn/năm", "kg/tháng", "kg/ngày"]),
    Truong("khoi_luong_kg_nam", "Quy đổi kg/năm (chỉ khi chắc chắn)", "float"),
])

BM_VHTN = BieuMau([
    Truong("cong_trinh", "Công trình VHTN", "textarea"),
    Truong("trang_thai", "Trạng thái", "chon", TRANG_THAI_VHTN, bat_buoc=True),
    Truong("bat_dau", "Bắt đầu", "date"),
    Truong("ket_thuc_du_kien", "Kết thúc dự kiến", "date", goi_y="VHTN không quá 06 tháng"),
    Truong("gia_han_den", "Gia hạn đến", "date", goi_y="Gia hạn một lần, không quá 06 tháng"),
    Truong("van_ban_thong_bao", "Văn bản thông báo"),
    Truong("ghi_chu_goc", "Ghi chú", "textarea"),
])

BM_DTM = BieuMau([
    Truong("so_qd", "Số QĐ phê duyệt kết quả thẩm định"),
    Truong("ngay_qd", "Ngày QĐ", "date"),
    Truong("co_quan_phe_duyet", "Cơ quan phê duyệt", "goi_y", CO_QUAN_GOI_Y),
    Truong("co_so_du_an_id", "Cơ sở / dự án", "fk", _ds_co_so, bat_buoc=True),
    Truong("nhom_du_an", "Nhóm dự án", "chon", NHOM_DU_AN),
    Truong("qd_thanh_lap_hoi_dong", "QĐ thành lập hội đồng thẩm định"),
    Truong("tep_pdf", "Tệp PDF gốc"),
    Truong("can_ra_soat", "Cần rà soát", "bool", noi_bo=True),
    Truong("ly_do_ra_soat", "Lý do rà soát", "textarea", noi_bo=True),
    Truong("ghi_chu", "Ghi chú nội bộ", "textarea", noi_bo=True),
])

BM_HO_SO = BieuMau([
    Truong("co_so_du_an_id", "Cơ sở / dự án", "fk", _ds_co_so, bat_buoc=True),
    Truong("loai", "Loại hồ sơ", "chon", LOAI_HO_SO, bat_buoc=True),
    Truong("van_ban_de_nghi", "Văn bản đề nghị"),
    Truong("ngay_tiep_nhan", "Ngày tiếp nhận", "date"),
    Truong("qd_doan_kiem_tra_hoac_hoi_dong", "QĐ đoàn kiểm tra / hội đồng thẩm định"),
    Truong("van_ban_bo_sung", "Văn bản chỉnh sửa, bổ sung", "textarea"),
    Truong("to_trinh", "Tờ trình của Sở"),
    Truong("trang_thai", "Trạng thái", "chon", TRANG_THAI_HO_SO, bat_buoc=True),
    Truong("can_bo_thu_ly", "Cán bộ thụ lý"),
    Truong("ket_qua_gpmt_id", "Kết quả: GPMT", "fk", _ds_gpmt),
    Truong("ket_qua_dtm_id", "Kết quả: QĐ ĐTM", "fk", _ds_dtm),
    Truong("ghi_chu", "Ghi chú", "textarea"),
])

BM_DKMT = BieuMau([
    Truong("co_so_du_an_id", "Cơ sở / dự án", "fk", _ds_co_so, bat_buoc=True),
    Truong("so_van_ban", "Số văn bản / số tiếp nhận"),
    Truong("ngay_tiep_nhan", "Ngày tiếp nhận", "date"),
    Truong("co_quan_tiep_nhan", "Cơ quan tiếp nhận", goi_y="UBND xã/phường …"),
    Truong("tu_gpmt_id", "Chuyển từ GPMT (NĐ 48/2026)", "fk", _ds_gpmt),
    Truong("tep_pdf", "Tệp PDF"),
    Truong("ghi_chu", "Ghi chú", "textarea"),
])


# Tên quan hệ ứng với cột khóa ngoại — để hiển thị nhãn thay cho số id
QUAN_HE = {
    "co_so_du_an_id": "co_so", "chu_the_id": "chu_the", "thay_the_gpmt_id": "thay_the",
    "dieu_chinh_gpmt_id": "dieu_chinh_cho", "ket_qua_gpmt_id": "ket_qua_gpmt", "ket_qua_dtm_id": "ket_qua_dtm",
    "tu_gpmt_id": "tu_gpmt",
}


def hien_thi(obj, t: Truong):
    """Giá trị để hiện trong bảng danh sách."""
    from . import dinh_dang_ngay, dinh_dang_so
    if t.kieu == "fk":
        rel = getattr(obj, QUAN_HE.get(t.ten, ""), None)
        if rel is None:
            return ""
        return getattr(rel, "so_qd", None) or str(rel)
    v = getattr(obj, t.ten, None)
    if t.kieu == "date":
        return dinh_dang_ngay(v)
    if t.kieu == "float":
        return dinh_dang_so(v)
    if t.kieu == "bool":
        return "Có" if v else ""
    return v if v is not None else ""
