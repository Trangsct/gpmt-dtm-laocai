"""Mô hình dữ liệu (mục 4 HUONG_DAN.md).

Nguyên tắc:
- Trường `*_goc` giữ nguyên văn như trong sổ/PDF; trường `*_so`, `*_don_vi` chỉ điền khi chắc chắn.
- Trạng thái GPMT KHÔNG lưu cứng, tính lại mỗi lần đọc (xem gpmt/trang_thai.py).
- `can_ra_soat` + `ly_do_ra_soat` đánh dấu dòng cần người phụ trách xác nhận; không tự đoán.
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def _now():
    return datetime.now()


# ---------------------------------------------------------------- Danh mục

class ChuThe(db.Model):
    """Chủ cơ sở / chủ dự án (doanh nghiệp, ban QLDA, đơn vị sự nghiệp…)."""
    __tablename__ = "chu_the"
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(500), nullable=False)
    ma_so_thue = db.Column(db.String(20), index=True)
    dia_chi_tru_so = db.Column(db.Text)
    loai = db.Column(db.String(50))  # doanh nghiệp / ban QLDA / đơn vị sự nghiệp / khác
    ghi_chu = db.Column(db.Text)

    co_so = db.relationship("CoSoDuAn", back_populates="chu_the")

    def __str__(self):
        return self.ten


class CoSoDuAn(db.Model):
    __tablename__ = "co_so_du_an"
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.Text, nullable=False)
    chu_the_id = db.Column(db.Integer, db.ForeignKey("chu_the.id"))
    dia_diem = db.Column(db.Text)            # địa chỉ như ghi trong GP / sổ
    xa_phuong_moi = db.Column(db.String(300), index=True)  # sau sắp xếp ĐVHC (sheet VHTN, GP mới)
    dia_ban_cu = db.Column(db.String(2))     # LC / YB (tỉnh trước hợp nhất)
    kcn_ccn = db.Column(db.String(200), index=True)
    loai_hinh = db.Column(db.Text)
    nhom_du_an = db.Column(db.String(5))     # I / II / III / IV theo Luật BVMT
    dien_tich = db.Column(db.String(100))    # giữ dạng chữ, vd "48.113,5 m2"
    cong_suat_goc = db.Column(db.Text)
    toa_do_lat = db.Column(db.Float)
    toa_do_lng = db.Column(db.Float)
    ghi_chu = db.Column(db.Text)             # nội bộ

    chu_the = db.relationship("ChuThe", back_populates="co_so")
    gpmt = db.relationship("Gpmt", back_populates="co_so", order_by="Gpmt.ngay_ky")
    dtm = db.relationship("Dtm", back_populates="co_so")
    ho_so = db.relationship("HoSo", back_populates="co_so")
    dang_ky_mt = db.relationship("DangKyMoiTruong", back_populates="co_so")

    def __str__(self):
        return self.ten


# ---------------------------------------------------------------- Hồ sơ đang giải quyết

class HoSo(db.Model):
    __tablename__ = "ho_so"
    id = db.Column(db.Integer, primary_key=True)
    co_so_du_an_id = db.Column(db.Integer, db.ForeignKey("co_so_du_an.id"), nullable=False)
    loai = db.Column(db.String(50), nullable=False)  # GPMT mới / điều chỉnh / cấp lại / ĐTM
    van_ban_de_nghi = db.Column(db.String(300))
    ngay_tiep_nhan = db.Column(db.Date)
    qd_doan_kiem_tra_hoac_hoi_dong = db.Column(db.String(300))
    van_ban_bo_sung = db.Column(db.Text)
    to_trinh = db.Column(db.String(300))
    trang_thai = db.Column(db.String(50), default="Tiếp nhận")
    can_bo_thu_ly = db.Column(db.String(200))
    ket_qua_gpmt_id = db.Column(db.Integer, db.ForeignKey("gpmt.id"))
    ket_qua_dtm_id = db.Column(db.Integer, db.ForeignKey("dtm.id"))
    ghi_chu = db.Column(db.Text)

    co_so = db.relationship("CoSoDuAn", back_populates="ho_so")
    ket_qua_gpmt = db.relationship("Gpmt", foreign_keys=[ket_qua_gpmt_id])
    ket_qua_dtm = db.relationship("Dtm", foreign_keys=[ket_qua_dtm_id])


TRANG_THAI_HO_SO = [
    "Tiếp nhận",
    "Đoàn kiểm tra / Hội đồng thẩm định",
    "Chủ cơ sở chỉnh sửa, bổ sung",
    "Sở trình (tờ trình)",
    "Đã ký GP/QĐ",
    "Trả hồ sơ / dừng",
]


# ---------------------------------------------------------------- GPMT

class Gpmt(db.Model):
    __tablename__ = "gpmt"
    # Không đặt ràng buộc duy nhất cho (số hiệu, ngày): sổ có trường hợp một số hiệu ghi cho hai cơ sở
    # khác nhau (vd 1827/GPMT-UBND ngày 16/9/2024). Trùng lặp được phát hiện khi nhập và gắn cờ rà soát.

    id = db.Column(db.Integer, primary_key=True)
    so_hieu = db.Column(db.String(100), index=True)   # đã chuẩn hóa, vd "2519/GPMT-UBND"
    so_hieu_goc = db.Column(db.Text)                  # nguyên văn cột "Giấy phép số"
    so = db.Column(db.Integer, index=True)
    ky_hieu = db.Column(db.String(50))
    loai_van_ban = db.Column(db.String(30), default="GPMT")  # GPMT / chưa rõ (QĐ, GPTN…)
    ngay_ky = db.Column(db.Date, index=True)
    nam_cap = db.Column(db.Integer, index=True)       # theo ngày ký; không có thì theo dòng nhóm năm của sổ
    co_quan_cap = db.Column(db.String(200), index=True)
    nguoi_ky = db.Column(db.String(200))
    loai_cap = db.Column(db.String(30))               # cấp mới / cấp điều chỉnh / cấp lại
    co_so_du_an_id = db.Column(db.Integer, db.ForeignKey("co_so_du_an.id"))
    thoi_han_nam = db.Column(db.Float)                # đọc từ Điều 3 của GP; không suy từ nhóm dự án
    ngay_het_han_nhap_tay = db.Column(db.Date)        # khi GP ghi ngày hết hạn cụ thể
    thay_the_gpmt_id = db.Column(db.Integer, db.ForeignKey("gpmt.id"))    # GP này làm GP kia hết hiệu lực
    dieu_chinh_gpmt_id = db.Column(db.Integer, db.ForeignKey("gpmt.id"))  # GP điều chỉnh cho GP kia (không tự làm hết hiệu lực)
    lua_chon_chuyen_tiep = db.Column(db.String(100))  # NĐ 48/2026: dùng tiếp GP / chuyển sang ĐKMT
    qd_doan_kiem_tra = db.Column(db.String(300))
    to_trinh = db.Column(db.String(300))
    van_ban_de_nghi = db.Column(db.Text)
    cong_suat_goc = db.Column(db.Text)
    nguon_du_lieu = db.Column(db.String(300))         # excel:<sheet>:dòng <n> / pdf / nhập tay
    can_ra_soat = db.Column(db.Boolean, default=False, index=True)
    ly_do_ra_soat = db.Column(db.Text)                # mỗi lý do một dòng
    ghi_chu_goc = db.Column(db.Text)                  # nguyên văn các cột ghi chú của sổ (nội bộ)
    tep_pdf = db.Column(db.String(300))
    cong_khai = db.Column(db.Boolean, default=True)   # GP có trong "Nơi nhận: Cổng TTĐT (để công khai)"
    tao_luc = db.Column(db.DateTime, default=_now)

    co_so = db.relationship("CoSoDuAn", back_populates="gpmt")
    thay_the = db.relationship("Gpmt", remote_side=[id], foreign_keys=[thay_the_gpmt_id],
                               backref=db.backref("bi_thay_the_boi", lazy="select"))
    dieu_chinh_cho = db.relationship("Gpmt", remote_side=[id], foreign_keys=[dieu_chinh_gpmt_id],
                                     backref=db.backref("cac_ban_dieu_chinh", lazy="select"))
    xa_thai = db.relationship("GpmtXaThai", back_populates="gpmt", cascade="all, delete-orphan")
    chat_thai = db.relationship("GpmtChatThai", back_populates="gpmt", cascade="all, delete-orphan")
    vhtn = db.relationship("Vhtn", back_populates="gpmt", cascade="all, delete-orphan")

    def them_ly_do(self, ly_do: str):
        """Gắn cờ cần rà soát kèm lý do (không trùng lặp)."""
        self.can_ra_soat = True
        cu = [x for x in (self.ly_do_ra_soat or "").split("\n") if x]
        if ly_do not in cu:
            cu.append(ly_do)
        self.ly_do_ra_soat = "\n".join(cu)

    @property
    def ds_ly_do(self):
        return [x for x in (self.ly_do_ra_soat or "").split("\n") if x]

    @property
    def ngay_het_han(self):
        from .trang_thai import tinh_ngay_het_han
        return tinh_ngay_het_han(self)

    @property
    def trang_thai(self):
        from .trang_thai import tinh_trang_thai
        return tinh_trang_thai(self)

    def __str__(self):
        ngay = self.ngay_ky.strftime("%d/%m/%Y") if self.ngay_ky else "?"
        return f"{self.so_hieu or '(chưa có số)'} ngày {ngay}"


class GpmtXaThai(db.Model):
    __tablename__ = "gpmt_xa_thai"
    id = db.Column(db.Integer, primary_key=True)
    gpmt_id = db.Column(db.Integer, db.ForeignKey("gpmt.id"), nullable=False)
    loai = db.Column(db.String(30), nullable=False)   # nước thải / khí thải / ồn-rung
    ten_dong = db.Column(db.String(300))              # "Tổng" khi là lưu lượng lớn nhất toàn cơ sở
    luu_luong_goc = db.Column(db.Text)
    luu_luong_max = db.Column(db.Float)
    don_vi = db.Column(db.String(50))
    quy_chuan = db.Column(db.String(300))
    nguon_tiep_nhan = db.Column(db.Text)
    toa_do_vn2000 = db.Column(db.String(200))
    cong_trinh_xu_ly = db.Column(db.Text)

    gpmt = db.relationship("Gpmt", back_populates="xa_thai")


class GpmtChatThai(db.Model):
    __tablename__ = "gpmt_chat_thai"
    id = db.Column(db.Integer, primary_key=True)
    gpmt_id = db.Column(db.Integer, db.ForeignKey("gpmt.id"), nullable=False)
    loai = db.Column(db.String(30), nullable=False)   # CTNH / CTRCNTT / CTRSH / CTR thông thường (sổ) / khác
    khoi_luong_goc = db.Column(db.Text)
    khoi_luong_so = db.Column(db.Float)
    don_vi = db.Column(db.String(50))
    khoi_luong_kg_nam = db.Column(db.Float)           # chỉ điền khi đơn vị quy đổi chắc chắn (kg/năm, tấn/năm)

    gpmt = db.relationship("Gpmt", back_populates="chat_thai")


class Vhtn(db.Model):
    __tablename__ = "vhtn"
    id = db.Column(db.Integer, primary_key=True)
    gpmt_id = db.Column(db.Integer, db.ForeignKey("gpmt.id"), nullable=False)
    cong_trinh = db.Column(db.Text)
    bat_dau = db.Column(db.Date)
    ket_thuc_du_kien = db.Column(db.Date)
    gia_han_den = db.Column(db.Date)
    trang_thai = db.Column(db.String(30), default="chưa rõ")  # chưa / đang / đã xong / không phải VHTN / chưa rõ
    van_ban_thong_bao = db.Column(db.String(300))
    ghi_chu_goc = db.Column(db.Text)

    gpmt = db.relationship("Gpmt", back_populates="vhtn")


TRANG_THAI_VHTN = ["chưa rõ", "chưa", "đang", "đã xong", "không phải VHTN"]


# ---------------------------------------------------------------- ĐTM, ĐKMT, giai đoạn 2

class Dtm(db.Model):
    __tablename__ = "dtm"
    id = db.Column(db.Integer, primary_key=True)
    so_qd = db.Column(db.String(100), index=True)
    ngay_qd = db.Column(db.Date)
    co_quan_phe_duyet = db.Column(db.String(200))
    co_so_du_an_id = db.Column(db.Integer, db.ForeignKey("co_so_du_an.id"))
    nhom_du_an = db.Column(db.String(5))
    qd_thanh_lap_hoi_dong = db.Column(db.String(300))
    tep_pdf = db.Column(db.String(300))
    can_ra_soat = db.Column(db.Boolean, default=False)
    ly_do_ra_soat = db.Column(db.Text)
    ghi_chu = db.Column(db.Text)

    co_so = db.relationship("CoSoDuAn", back_populates="dtm")


class DangKyMoiTruong(db.Model):
    """Đăng ký môi trường (UBND cấp xã tiếp nhận). Bạn chốt 26/9/2026: đưa vào phạm vi; giao diện đầy đủ ở giai đoạn 2."""
    __tablename__ = "dang_ky_moi_truong"
    id = db.Column(db.Integer, primary_key=True)
    co_so_du_an_id = db.Column(db.Integer, db.ForeignKey("co_so_du_an.id"))
    so_van_ban = db.Column(db.String(100))
    ngay_tiep_nhan = db.Column(db.Date)
    co_quan_tiep_nhan = db.Column(db.String(200))    # UBND xã/phường …
    tu_gpmt_id = db.Column(db.Integer, db.ForeignKey("gpmt.id"))  # chuyển từ GPMT theo NĐ 48/2026 (nếu có)
    tep_pdf = db.Column(db.String(300))
    ghi_chu = db.Column(db.Text)

    co_so = db.relationship("CoSoDuAn", back_populates="dang_ky_mt")
    tu_gpmt = db.relationship("Gpmt")


class BaoCaoBvmt(db.Model):  # giai đoạn 2
    __tablename__ = "bao_cao_bvmt"
    id = db.Column(db.Integer, primary_key=True)
    co_so_du_an_id = db.Column(db.Integer, db.ForeignKey("co_so_du_an.id"), nullable=False)
    nam = db.Column(db.Integer)
    da_nop = db.Column(db.Boolean)
    ngay_nop = db.Column(db.Date)
    ghi_chu = db.Column(db.Text)


class KiemTra(db.Model):  # giai đoạn 2
    __tablename__ = "kiem_tra"
    id = db.Column(db.Integer, primary_key=True)
    co_so_du_an_id = db.Column(db.Integer, db.ForeignKey("co_so_du_an.id"), nullable=False)
    ngay = db.Column(db.Date)
    co_quan = db.Column(db.String(200))
    ket_luan = db.Column(db.Text)
    van_ban = db.Column(db.String(300))


# ---------------------------------------------------------------- Tài khoản, nhật ký

VAI_TRO = {
    "quan_tri": "Quản trị",
    "bien_tap": "Biên tập",
    "chi_xem": "Chỉ xem (trong Sở)",
    "ben_ngoai": "Xem giới hạn (BQL các KCN / UBND xã)",
}


class TaiKhoan(UserMixin, db.Model):
    __tablename__ = "tai_khoan"
    id = db.Column(db.Integer, primary_key=True)
    ho_ten = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    mat_khau_hash = db.Column(db.String(300), nullable=False)
    vai_tro = db.Column(db.String(20), nullable=False, default="chi_xem")
    don_vi = db.Column(db.String(200))        # Phòng …/ BQL các KCN / UBND xã …
    pham_vi_xa = db.Column(db.String(200))    # tài khoản UBND xã: chỉ thấy cơ sở trên địa bàn xã này
    pham_vi_kcn = db.Column(db.Boolean, default=False)  # tài khoản BQL các KCN: chỉ thấy cơ sở trong KCN/CCN
    hoat_dong = db.Column(db.Boolean, default=True)

    def dat_mat_khau(self, mk):
        self.mat_khau_hash = generate_password_hash(mk)

    def kiem_mat_khau(self, mk):
        return check_password_hash(self.mat_khau_hash, mk)

    @property
    def is_active(self):
        return bool(self.hoat_dong)

    @property
    def duoc_sua(self):
        return self.vai_tro in ("quan_tri", "bien_tap")

    @property
    def noi_bo(self):
        """Được xem thông tin nội bộ (hồ sơ đang giải quyết, ghi chú, nhật ký)."""
        return self.vai_tro in ("quan_tri", "bien_tap", "chi_xem")


class NhatKy(db.Model):
    __tablename__ = "nhat_ky"
    id = db.Column(db.Integer, primary_key=True)
    tai_khoan_id = db.Column(db.Integer, db.ForeignKey("tai_khoan.id"))
    thoi_diem = db.Column(db.DateTime, default=_now, index=True)
    bang = db.Column(db.String(50))
    ban_ghi = db.Column(db.Integer)
    hanh_dong = db.Column(db.String(10))   # them / sua / xoa
    thay_doi = db.Column(db.Text)          # JSON {truong: [cũ, mới]}

    tai_khoan = db.relationship("TaiKhoan")


class BaoCaoNhapLuu(db.Model):
    """Báo cáo mỗi lần nhập dữ liệu qua trang web (máy chủ Vercel không ghi được tệp nên lưu vào CSDL)."""
    __tablename__ = "bao_cao_nhap"
    id = db.Column(db.Integer, primary_key=True)
    thoi_diem = db.Column(db.DateTime, default=_now)
    tai_khoan_id = db.Column(db.Integer, db.ForeignKey("tai_khoan.id"))
    loai = db.Column(db.String(30))        # so-excel / bo-sung-thoi-han
    ten_tep = db.Column(db.String(300))
    tom_tat = db.Column(db.String(500))
    noi_dung = db.Column(db.Text)          # Markdown

    tai_khoan = db.relationship("TaiKhoan")
