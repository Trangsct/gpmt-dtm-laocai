"""Trang công khai 'Thủ tục hành chính' (Bạn yêu cầu 27/9/2026)."""
import json

from gpmt.views.cong_bo import TEP_DU_LIEU, THU_MUC_PDF


def test_trang_cong_khai_khong_can_dang_nhap(app, db):
    r = app.test_client().get("/thu-tuc-hanh-chinh")
    assert r.status_code == 200
    for x in ("463/QĐ-UBND", "736/QĐ-UBND", "13/02/2026", "19/03/2026", "1.010727", "Cấp giấy phép môi trường",
              "Cấp đổi giấy phép môi trường", "26/6/2026"):
        assert x in r.text, x
    assert r.text.count("Đang áp dụng") == 2 and r.text.count("Đã bỏ theo QĐ ngày 26/6/2026") == 3


def test_tep_pdf_ton_tai_va_tai_duoc(app, db):
    du_lieu = json.loads(TEP_DU_LIEU.read_text(encoding="utf-8"))
    c = app.test_client()
    for vb in du_lieu["van_ban"]:
        p = THU_MUC_PDF / vb["tep"]
        assert p.is_file() and p.stat().st_size < 4.5 * 1024 * 1024   # giới hạn phản hồi của Vercel
        r = c.get(f"/cong-bo/{vb['tep']}")
        assert r.status_code == 200 and r.data[:4] == b"%PDF"
        r.close()
    assert c.get("/cong-bo/../gpmt/config.py").status_code == 404
