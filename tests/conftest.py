import re
from pathlib import Path

import pytest

from gpmt import create_app
from gpmt.extensions import db as _db

GOC = Path(__file__).resolve().parent.parent
TEP_SO = GOC / "du-lieu-goc" / "So_theo_doi_cap_GPMT_hang_nam_Lao_Cai.xls"
TEP_2519 = GOC / "du-lieu-goc" / "ban-ghi-doi-chieu" / "2519_GPMT-UBND.json"


@pytest.fixture()
def app(tmp_path):
    app = create_app({"SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'thu.sqlite3'}",
                      "TESTING": True, "SECRET_KEY": "khoa-thu", "PDF_DIR": str(GOC / "du-lieu-goc")})
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def du_lieu_that(app):
    """CSDL đã nhập sổ Excel thật + GP 2519 đối chiếu tay."""
    from gpmt.nhap_ban_ghi import nhap_tep_json
    from gpmt.nhap_excel import doc_so_theo_doi, nhap_vao_csdl
    bc = nhap_vao_csdl(doc_so_theo_doi(TEP_SO))
    nhap_tep_json(TEP_2519)
    return bc


def tao_tai_khoan(db, email, vai_tro, **kw):
    from gpmt.models import TaiKhoan
    tk = TaiKhoan(email=email, ho_ten=email.split("@")[0], vai_tro=vai_tro, **kw)
    tk.dat_mat_khau("matkhau-thu-123")
    db.session.add(tk)
    db.session.commit()
    return tk


def dang_nhap(client, email):
    r = client.get("/dang-nhap")
    tok = re.search(r'name="_csrf" value="([^"]+)"', r.text).group(1)
    r = client.post("/dang-nhap", data={"_csrf": tok, "email": email, "mat_khau": "matkhau-thu-123"})
    assert r.status_code == 302
    # Đăng nhập làm mới phiên (chống cố định phiên) nên token CSRF cũ hết hiệu lực — lấy token mới
    r = client.get("/doi-mat-khau")
    return re.search(r'name="_csrf" value="([^"]+)"', r.text).group(1)
