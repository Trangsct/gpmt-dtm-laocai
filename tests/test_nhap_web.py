"""Nhập dữ liệu qua trang web (không cần dòng lệnh) và tự khởi tạo khi chạy lần đầu."""
import io

from openpyxl import load_workbook

from gpmt import create_app
from gpmt.extensions import db as _db
from gpmt.models import BaoCaoNhapLuu, Gpmt, NhatKy, TaiKhoan
from gpmt.trang_thai import BI_THAY_THE, CON_HIEU_LUC

from .conftest import TEP_SO, dang_nhap, tao_tai_khoan


def test_tu_tao_quan_tri_dau_tien(tmp_path, monkeypatch):
    monkeypatch.setenv("QUAN_TRI_EMAIL", "QT@So.local")
    monkeypatch.setenv("QUAN_TRI_MAT_KHAU", "mat-khau-dai-123")
    app = create_app({"SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'moi.sqlite3'}", "SECRET_KEY": "x"})
    with app.app_context():
        tk = _db.session.query(TaiKhoan).one()
        assert tk.email == "qt@so.local" and tk.vai_tro == "quan_tri" and tk.kiem_mat_khau("mat-khau-dai-123")
    # Lần khởi động sau không tạo thêm
    create_app({"SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'moi.sqlite3'}", "SECRET_KEY": "x"})
    with app.app_context():
        assert _db.session.query(TaiKhoan).count() == 1


def _tai_len(c, tok, url, noi_dung, ten):
    return c.post(url, data={"_csrf": tok, "tep": (io.BytesIO(noi_dung), ten)},
                  content_type="multipart/form-data")


def test_nhap_so_qua_web(app, db):
    tao_tai_khoan(db, "qt@thu.local", "quan_tri")
    c = app.test_client()
    tok = dang_nhap(c, "qt@thu.local")
    assert c.get("/nhap-du-lieu/").status_code == 200
    r = _tai_len(c, tok, "/nhap-du-lieu/so-excel", TEP_SO.read_bytes(), "so.xls")
    assert r.status_code == 302 and "/bao-cao/" in r.headers["Location"]
    assert db.session.query(Gpmt).count() == 149      # 147 từ sổ + 2519 đối chiếu tay + 3216 từ Data360X
    assert db.session.query(Gpmt).filter_by(so_hieu="1439/GPMT-UBND").one().trang_thai == BI_THAY_THE
    assert db.session.query(NhatKy).count() == 0      # nhập hàng loạt không ghi nhật ký từng dòng
    bc = db.session.query(BaoCaoNhapLuu).one()
    assert "2519/GPMT-UBND" in bc.noi_dung and c.get(r.headers["Location"]).status_code == 200
    # Nhập lần 2 bị chặn
    _tai_len(c, tok, "/nhap-du-lieu/so-excel", TEP_SO.read_bytes(), "so.xls")
    assert db.session.query(Gpmt).count() == 149
    # Xóa phải gõ đúng cụm xác nhận
    c.post("/nhap-du-lieu/xoa", data={"_csrf": tok, "xac_nhan": "xoa"})
    assert db.session.query(Gpmt).count() == 149
    c.post("/nhap-du-lieu/xoa", data={"_csrf": tok, "xac_nhan": "XOA DU LIEU"})
    assert db.session.query(Gpmt).count() == 0


def test_bien_tap_khong_duoc_tai_so(app, db):
    tao_tai_khoan(db, "bt@thu.local", "bien_tap")
    c = app.test_client()
    tok = dang_nhap(c, "bt@thu.local")
    assert _tai_len(c, tok, "/nhap-du-lieu/so-excel", TEP_SO.read_bytes(), "so.xls").status_code == 403


def test_tep_sai_bao_loi_khong_sap(app, db):
    tao_tai_khoan(db, "qt@thu.local", "quan_tri")
    c = app.test_client()
    tok = dang_nhap(c, "qt@thu.local")
    r = _tai_len(c, tok, "/nhap-du-lieu/so-excel", b"khong phai excel", "so.xls")
    assert r.status_code == 302
    assert "Không nhập được" in c.get("/nhap-du-lieu/").text


def test_mau_bo_sung_thoi_han(app, db, du_lieu_that):
    tao_tai_khoan(db, "bt@thu.local", "bien_tap")
    c = app.test_client()
    tok = dang_nhap(c, "bt@thu.local")
    r = c.get("/nhap-du-lieu/mau-bo-sung")
    wb = load_workbook(io.BytesIO(r.data))
    ws = wb["Bo sung"]
    dong = {ws.cell(i, 2).value: i for i in range(2, ws.max_row + 1)}
    assert "2519/GPMT-UBND" not in dong           # GP đã đủ thời hạn không nằm trong mẫu "còn thiếu"
    ws.cell(dong["2074/GPMT-UBND"], 6).value = 10  # điền thời hạn
    ws.cell(dong["1869/GPMT-UBND"], 3).value = "15/08/2023"   # điền ngày ký còn thiếu
    ws.cell(dong["1869/GPMT-UBND"], 6).value = 7
    ws.cell(dong["123/GP-UBND"], 6).value = 99     # sai → bỏ qua dòng, báo lỗi
    tep = io.BytesIO()
    wb.save(tep)
    r = _tai_len(c, tok, "/nhap-du-lieu/bo-sung", tep.getvalue(), "mau.xlsx")
    assert r.status_code == 302
    db.session.expire_all()
    sojo = db.session.query(Gpmt).filter_by(so_hieu="2074/GPMT-UBND").one()
    assert sojo.thoi_han_nam == 10 and sojo.trang_thai == CON_HIEU_LUC
    gp = db.session.query(Gpmt).filter_by(so_hieu="1869/GPMT-UBND").one()
    assert gp.ngay_ky.isoformat() == "2023-08-15" and gp.nam_cap == 2023 and gp.thoi_han_nam == 7
    assert db.session.query(Gpmt).filter_by(so_hieu="123/GP-UBND").one().thoi_han_nam is None
    bc = db.session.query(BaoCaoNhapLuu).filter_by(loai="bo-sung-thoi-han").one()
    assert "Đã cập nhật: 2" in bc.noi_dung and "123/GP-UBND" in bc.noi_dung
    assert db.session.query(NhatKy).filter_by(bang="gpmt", hanh_dong="sua").count() == 2
