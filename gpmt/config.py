"""Cấu hình đọc từ biến môi trường — đổi nơi chạy (Vercel, máy chủ của Sở) không phải sửa code."""
import hashlib
import os
import secrets
from pathlib import Path

GOC_DU_AN = Path(__file__).resolve().parent.parent


# Tên biến chứa chuỗi kết nối, theo thứ tự ưu tiên. Tích hợp Neon trên Vercel thường đặt DATABASE_URL, có khi
# POSTGRES_URL; nếu người dùng đặt "tiền tố" khi nối (vd STORAGE) thì thành STORAGE_DATABASE_URL, STORAGE_URL…
TEN_BIEN_CSDL = ["DATABASE_URL", "POSTGRES_URL", "NEON_DATABASE_URL"]


def tim_bien_csdl():
    """Trả (tên biến, giá trị) của chuỗi kết nối PostgreSQL tìm được, hoặc (None, "")."""
    for ten in TEN_BIEN_CSDL:
        if os.environ.get(ten, "").strip():
            return ten, os.environ[ten].strip()
    # Dò các biến có tiền tố: …_DATABASE_URL, …_POSTGRES_URL, …_URL — bỏ bản "không qua pool"/"không SSL"
    ung_vien = sorted(
        (k for k, v in os.environ.items()
         if v.strip().startswith(("postgres://", "postgresql://"))
         and not any(x in k for x in ("UNPOOLED", "NON_POOLING", "NO_SSL"))),
        key=lambda k: (not k.endswith("DATABASE_URL"), not k.endswith("POSTGRES_URL"), k))
    if ung_vien:
        return ung_vien[0], os.environ[ung_vien[0]].strip()
    return None, ""


def _url_tho():
    return tim_bien_csdl()[1]


def _database_url():
    url = _url_tho()
    if not url:
        return f"sqlite:///{GOC_DU_AN / 'gpmt-local.sqlite3'}"
    # Neon/Heroku trả "postgres://"; SQLAlchemy 2.1 mặc định "postgresql://" dùng driver psycopg 3 —
    # ghi rõ psycopg2 (có trong requirements.txt)
    for dau in ("postgres://", "postgresql://"):
        if url.startswith(dau):
            url = "postgresql+psycopg2://" + url[len(dau):]
    return url


def _secret_key():
    """Ưu tiên SECRET_KEY. Không đặt thì suy ra khóa cố định từ DATABASE_URL (vốn đã bí mật) để mọi máy
    chủ serverless dùng chung một khóa — bớt một bước cấu hình. Chạy cục bộ không có CSDL: khóa ngẫu nhiên."""
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    if _url_tho():
        return hashlib.sha256(("gpmt-dtm-laocai|" + _url_tho()).encode()).hexdigest()
    return secrets.token_hex(32)


class Config:
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = _secret_key()
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Vercel tự đặt biến VERCEL=1 và luôn chạy HTTPS → bật cookie bảo mật
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "1" if os.environ.get("VERCEL") else "0") == "1"
    # Thư mục tệp PDF gốc (chạy cục bộ / máy chủ của Sở). Trên Vercel để trống và dùng PDF_BASE_URL.
    PDF_DIR = os.environ.get("PDF_DIR", str(GOC_DU_AN / "du-lieu-goc"))
    # Địa chỉ gốc nơi lưu PDF riêng tư (dịch vụ lưu tệp); nếu đặt thì nút "Mở PDF" trỏ tới đây
    PDF_BASE_URL = os.environ.get("PDF_BASE_URL", "").rstrip("/")
    TEN_DON_VI = os.environ.get("TEN_DON_VI", "Sở Nông nghiệp và Môi trường tỉnh Lào Cai")
    # Bạn chốt 27/9/2026: dữ liệu GPMT công khai cho người dân, doanh nghiệp — xem không cần đăng nhập.
    # Đặt CONG_KHAI=0 để bắt buộc đăng nhập mới xem.
    CONG_KHAI = os.environ.get("CONG_KHAI", "1") != "0"
