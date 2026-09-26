"""Trang /suc-khoe tự chẩn đoán cấu hình — cho người dùng không chuyên."""
from gpmt import create_app

from .conftest import tao_tai_khoan


def _app_loi(monkeypatch, tmp_path):
    """Giống Vercel chưa nối Neon: không có biến CSDL, SQLite nằm trong thư mục không tồn tại/chỉ đọc."""
    for k in ("DATABASE_URL", "POSTGRES_URL"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("VERCEL", "1")
    return create_app({"SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path}/khong-co/thu-muc/x.sqlite3",
                       "SECRET_KEY": "x"})


def test_chua_noi_neon_bao_ro_viec_can_lam(monkeypatch, tmp_path):
    c = _app_loi(monkeypatch, tmp_path).test_client()
    r = c.get("/suc-khoe")
    assert r.status_code == 503
    assert "Bước 4" in r.text and "Storage" in r.text
    j = c.get("/suc-khoe?json=1").get_json()
    assert j["trang_thai"] == "loi"
    assert [x["dat"] for x in j["kiem_tra"] if x["ten"] == "Kết nối CSDL"] == [False]


def test_trang_khac_hien_loi_tieng_viet(monkeypatch, tmp_path):
    c = _app_loi(monkeypatch, tmp_path).test_client()
    r = c.get("/dang-nhap")   # trang đăng nhập kiểm tra đã có tài khoản chưa → phải truy vấn CSDL
    assert r.status_code == 500 and "Kiểm tra hệ thống" in r.text and "Traceback" not in r.text


def test_thieu_bien_quan_tri(app, db, monkeypatch):
    for k in ("QUAN_TRI_EMAIL", "QUAN_TRI_MAT_KHAU"):
        monkeypatch.delenv(k, raising=False)
    r = app.test_client().get("/suc-khoe?json=1")
    tk = [x for x in r.get_json()["kiem_tra"] if x["ten"] == "Tài khoản"][0]
    assert tk["dat"] is None and "/cai-dat" in tk["viec_can_lam"]


def test_tu_tao_quan_tri_khi_kiem_tra(app, db, monkeypatch):
    # Biến đặt sau khi ứng dụng đã khởi động: mở /suc-khoe là tự tạo tài khoản
    monkeypatch.setenv("QUAN_TRI_EMAIL", "qt@so.local")
    monkeypatch.setenv("QUAN_TRI_MAT_KHAU", "mat-khau-dai-123")
    j = app.test_client().get("/suc-khoe?json=1").get_json()
    assert [x["dat"] for x in j["kiem_tra"] if x["ten"] == "Tài khoản"] == [True]


def test_day_du_thi_dat_va_khong_lo_bi_mat(app, db, monkeypatch):
    tao_tai_khoan(db, "qt@thu.local", "quan_tri")
    monkeypatch.setenv("DATABASE_URL", "postgres://nguoi:matkhau-bi-mat@may/db")
    r = app.test_client().get("/suc-khoe")
    assert r.status_code == 200 and "matkhau-bi-mat" not in r.text


def test_dat_tien_to_khi_noi_neon(monkeypatch):
    from gpmt.config import tim_bien_csdl
    for k in ("DATABASE_URL", "POSTGRES_URL", "NEON_DATABASE_URL"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("STORAGE_DATABASE_URL_UNPOOLED", "postgres://a@b/khong-dung")
    monkeypatch.setenv("STORAGE_DATABASE_URL", "postgres://a@b/dung")
    assert tim_bien_csdl() == ("STORAGE_DATABASE_URL", "postgres://a@b/dung")
