"""Cấu hình từ biến môi trường (Vercel + Neon)."""
import importlib

import gpmt.config as cau_hinh


def _nap(monkeypatch, **bien):
    for k in ("DATABASE_URL", "POSTGRES_URL", "SECRET_KEY", "VERCEL", "SESSION_COOKIE_SECURE"):
        monkeypatch.delenv(k, raising=False)
    for k, v in bien.items():
        monkeypatch.setenv(k, v)
    return importlib.reload(cau_hinh).Config


def test_neon_dung_driver_psycopg2(monkeypatch):
    # SQLAlchemy 2.1 mặc định postgresql:// → psycopg 3 (không cài) — phải ghi rõ psycopg2
    for url in ("postgres://u:p@ep-x.neon.tech/db?sslmode=require", "postgresql://u:p@ep-x.neon.tech/db?sslmode=require"):
        cfg = _nap(monkeypatch, DATABASE_URL=url)
        assert cfg.SQLALCHEMY_DATABASE_URI == "postgresql+psycopg2://u:p@ep-x.neon.tech/db?sslmode=require"
    assert _nap(monkeypatch, POSTGRES_URL="postgres://a@b/c").SQLALCHEMY_DATABASE_URI.startswith("postgresql+psycopg2://")


def test_secret_key_on_dinh_khi_khong_dat(monkeypatch):
    a = _nap(monkeypatch, DATABASE_URL="postgres://u:p@h/db").SECRET_KEY
    b = _nap(monkeypatch, DATABASE_URL="postgres://u:p@h/db").SECRET_KEY
    assert a == b and len(a) == 64 and "p@h" not in a
    assert _nap(monkeypatch, DATABASE_URL="postgres://u:p@h/db", SECRET_KEY="rieng").SECRET_KEY == "rieng"


def test_cookie_bao_mat_tren_vercel(monkeypatch):
    assert _nap(monkeypatch, VERCEL="1").SESSION_COOKIE_SECURE is True
    assert _nap(monkeypatch).SESSION_COOKIE_SECURE is False
