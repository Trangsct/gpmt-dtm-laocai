"""Cấp lại tên đăng nhập / mật khẩu quản trị qua biến môi trường trên Vercel (Bạn yêu cầu 28/9/2026)."""
from gpmt.dich_vu import cap_quan_tri_tu_bien_moi_truong
from gpmt.models import TaiKhoan

from .conftest import tao_tai_khoan


def test_dat_lai_mat_khau_tai_khoan_co_san(app, db, monkeypatch):
    tao_tai_khoan(db, "qt@vd.vn", "bien_tap", hoat_dong=False)
    monkeypatch.setenv("QUAN_TRI_EMAIL", " QT@vd.vn ")
    monkeypatch.setenv("QUAN_TRI_MAT_KHAU", "mat-khau-moi-2026")
    with app.app_context():
        assert cap_quan_tri_tu_bien_moi_truong() == "dat-lai"
        tk = db.session.query(TaiKhoan).filter_by(email="qt@vd.vn").one()
        assert tk.kiem_mat_khau("mat-khau-moi-2026") and tk.hoat_dong and tk.vai_tro == "quan_tri"
        assert cap_quan_tri_tu_bien_moi_truong() is None  # khởi động lại: không ghi gì thêm
    c = app.test_client()
    r = c.get("/dang-nhap")
    import re
    tok = re.search(r'name="_csrf" value="([^"]+)"', r.text).group(1)
    r = c.post("/dang-nhap", data={"_csrf": tok, "email": "qt@vd.vn", "mat_khau": "mat-khau-moi-2026"})
    assert r.status_code == 302


def test_tao_quan_tri_moi_khi_da_co_tai_khoan_khac(app, db, monkeypatch):
    tao_tai_khoan(db, "cu@vd.vn", "quan_tri")
    monkeypatch.setenv("QUAN_TRI_EMAIL", "moi@vd.vn")
    monkeypatch.setenv("QUAN_TRI_MAT_KHAU", "mat-khau-moi-2026")
    monkeypatch.setenv("QUAN_TRI_HO_TEN", "Trần Trọng Trang")
    with app.app_context():
        assert cap_quan_tri_tu_bien_moi_truong() == "tao"
        assert db.session.query(TaiKhoan).filter_by(email="moi@vd.vn").one().ho_ten == "Trần Trọng Trang"


def test_mat_khau_ngan_bi_bo_qua(app, db, monkeypatch):
    monkeypatch.setenv("QUAN_TRI_EMAIL", "qt@vd.vn")
    monkeypatch.setenv("QUAN_TRI_MAT_KHAU", "ngan")
    with app.app_context():
        assert cap_quan_tri_tu_bien_moi_truong() is None


def test_suc_khoe_goi_nho_ten_dang_nhap_da_che(app, db):
    tao_tai_khoan(db, "trangsct@vd.vn", "quan_tri")
    r = app.test_client().get("/suc-khoe")
    assert "tr•••@vd.vn" in r.text and "trangsct@vd.vn" not in r.text
    assert "QUAN_TRI_MAT_KHAU" in r.text
