"""Cấu hình đọc từ biến môi trường — đổi nơi chạy (Vercel, máy chủ của Sở) không phải sửa code."""
import os
import secrets
from pathlib import Path

GOC_DU_AN = Path(__file__).resolve().parent.parent


def _database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return f"sqlite:///{GOC_DU_AN / 'gpmt-local.sqlite3'}"
    # Neon/Heroku trả "postgres://", SQLAlchemy cần "postgresql://"
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Bản chạy thật BẮT BUỘC đặt SECRET_KEY; thiếu thì sinh ngẫu nhiên (phiên đăng nhập mất khi khởi động lại)
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    # Thư mục tệp PDF gốc (chạy cục bộ / máy chủ của Sở). Trên Vercel để trống và dùng PDF_BASE_URL.
    PDF_DIR = os.environ.get("PDF_DIR", str(GOC_DU_AN / "du-lieu-goc"))
    # Địa chỉ gốc nơi lưu PDF riêng tư (dịch vụ lưu tệp); nếu đặt thì nút "Mở PDF" trỏ tới đây
    PDF_BASE_URL = os.environ.get("PDF_BASE_URL", "").rstrip("/")
    TEN_DON_VI = os.environ.get("TEN_DON_VI", "Sở Nông nghiệp và Môi trường tỉnh Lào Cai")
