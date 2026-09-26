"""Tự chẩn đoán cấu hình triển khai (trang /suc-khoe) — cho người dùng không chuyên tự biết thiếu gì.

Không hiện giá trị bí mật (chuỗi kết nối, mật khẩu): chỉ hiện TÊN biến và thông báo lỗi đã che thông tin đăng nhập.
Tự sửa những gì sửa được: tạo bảng còn thiếu, tạo tài khoản quản trị đầu tiên nếu biến đã đặt.
"""
import os
import re
from dataclasses import dataclass

from sqlalchemy import inspect, text

from .config import tim_bien_csdl
from .extensions import db


@dataclass
class KetQua:
    ten: str
    dat: bool | None          # True đạt, False lỗi, None thông tin
    chi_tiet: str
    viec_can_lam: str = ""


def _che(s: str) -> str:
    """Che người dùng/mật khẩu trong chuỗi kết nối nếu lọt vào thông báo lỗi."""
    s = re.sub(r"(\w+://)[^@\s/]+@", r"\1***@", s)
    return re.sub(r"(password\s*=\s*)\S+", r"\1***", s, flags=re.I)


def _goi_y_loi(msg: str) -> str:
    m = msg.lower()
    if "could not translate host name" in m or "name or service not known" in m:
        return "Chuỗi kết nối sai máy chủ. Vào Vercel → Storage → chọn CSDL Neon → Disconnect rồi Connect lại vào dự án, sau đó Redeploy."
    if "password authentication failed" in m:
        return "Sai mật khẩu CSDL. Vào Vercel → Storage → CSDL Neon → Connect lại vào dự án (để Vercel cập nhật biến), rồi Redeploy."
    if "endpoint" in m and ("disabled" in m or "suspend" in m):
        return "CSDL Neon đang tạm nghỉ (gói miễn phí). Chờ 10–20 giây rồi tải lại trang này."
    if "timeout" in m or "timed out" in m:
        return "Kết nối CSDL quá thời gian. Tải lại trang sau ít phút; lặp lại thì chụp trang này gửi Claude."
    if "does not exist" in m and "database" in m:
        return "Tên CSDL trong chuỗi kết nối không tồn tại. Connect lại CSDL Neon vào dự án rồi Redeploy."
    if "unable to open database file" in m or "read-only" in m:
        return "Chưa có CSDL Neon nên ứng dụng không lưu được dữ liệu. Làm Bước 4 trong HUONG_DAN_TRIEN_KHAI.md."
    return "Chụp màn hình trang này gửi Claude để được sửa."


def kiem_tra(app) -> list[KetQua]:
    kq = []
    tren_vercel = bool(os.environ.get("VERCEL"))
    kq.append(KetQua("Nơi chạy", None, "Vercel" + (f" ({os.environ.get('VERCEL_ENV')})" if os.environ.get("VERCEL_ENV") else "")
                     if tren_vercel else "Máy cục bộ / máy chủ riêng"))

    ten_bien, _ = tim_bien_csdl()
    lien_quan = sorted(k for k in os.environ if re.search(r"DATABASE|POSTGRES|^PG|NEON", k))
    if ten_bien:
        kq.append(KetQua("Biến kết nối CSDL", True, f"Dùng biến {ten_bien}"))
    else:
        kq.append(KetQua(
            "Biến kết nối CSDL", False if tren_vercel else None,
            "Không tìm thấy biến chứa chuỗi kết nối PostgreSQL"
            + (f" (các biến liên quan đang có: {', '.join(lien_quan)})" if lien_quan else " (không có biến nào liên quan)"),
            "Làm Bước 4: Vercel → dự án → thẻ Storage → Create Database → Neon → Connect Project (tích cả "
            "Production) → sau đó thẻ Deployments → ⋯ → Redeploy." if tren_vercel else
            "Chạy cục bộ dùng SQLite — không cần làm gì."))

    # Kết nối
    try:
        with db.engine.connect() as c:
            c.execute(text("SELECT 1"))
        kq.append(KetQua("Kết nối CSDL", True, f"Kết nối được ({db.engine.dialect.name})"))
    except Exception as e:
        msg = _che(f"{type(e).__name__}: {str(e).strip().splitlines()[0] if str(e).strip() else ''}")[:400]
        kq.append(KetQua("Kết nối CSDL", False, msg, _goi_y_loi(msg)))
        return kq

    # Bảng + tài khoản đầu tiên: tự sửa bằng cách chạy lại khởi tạo
    from .dich_vu import khoi_tao_tu_dong
    khoi_tao_tu_dong(app)
    bang = set(inspect(db.engine).get_table_names())
    thieu = {"gpmt", "tai_khoan", "co_so_du_an", "nhat_ky", "bao_cao_nhap"} - bang
    kq.append(KetQua("Bảng dữ liệu", not thieu, "Đủ bảng" if not thieu else f"Thiếu bảng: {', '.join(sorted(thieu))}",
                     "" if not thieu else "Chụp trang này gửi Claude."))

    from .models import Gpmt, TaiKhoan
    so_tk = db.session.query(TaiKhoan).count()
    if so_tk:
        kq.append(KetQua("Tài khoản", True, f"Đã có {so_tk} tài khoản"))
    else:
        kq.append(KetQua("Tài khoản", None, "Chưa có tài khoản nào",
                         "Mở trang /cai-dat (hoặc bấm 'Cán bộ đăng nhập') để tạo tài khoản quản trị — không cần "
                         "đặt biến trên Vercel. Làm ngay, vì ai mở trang này trước sẽ tạo được tài khoản."))

    so_gp = db.session.query(Gpmt).count()
    kq.append(KetQua("Dữ liệu GPMT", True if so_gp else None,
                     f"Đã có {so_gp} giấy phép" if so_gp else "Chưa có giấy phép nào",
                     "" if so_gp else "Đăng nhập → menu Nhập dữ liệu → tải sổ Excel (.xls) lên."))
    return kq
