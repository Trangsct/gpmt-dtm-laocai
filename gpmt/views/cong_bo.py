"""Trang công khai 'Thủ tục hành chính': văn bản công bố TTHC và quy trình nội bộ lĩnh vực môi trường
(Bạn yêu cầu 27/9/2026). Nội dung ở gpmt/cong_bo.json, bản gốc PDF ở public/cong-bo/.

Trên Vercel, tệp trong public/ được máy chủ tĩnh phục vụ trực tiếp (không qua Flask, tránh giới hạn
4,5 MB của hàm serverless); route /cong-bo/ dưới đây dùng khi chạy cục bộ hoặc máy chủ riêng.
"""
import json
from datetime import date
from pathlib import Path

from flask import Blueprint, abort, render_template, send_from_directory

from ..auth import can_xem

bp = Blueprint("cong_bo", __name__)

TEP_DU_LIEU = Path(__file__).resolve().parent.parent / "cong_bo.json"
THU_MUC_PDF = Path(__file__).resolve().parent.parent.parent / "public" / "cong-bo"


def doc_du_lieu():
    du_lieu = json.loads(TEP_DU_LIEU.read_text(encoding="utf-8"))
    for vb in du_lieu["van_ban"]:
        vb["ngay"] = date.fromisoformat(vb["ngay"])
    return du_lieu


@bp.route("/thu-tuc-hanh-chinh")
@can_xem
def trang():
    return render_template("cong_bo.html", **doc_du_lieu())


@bp.route("/cong-bo/<path:ten_tep>")
def tep(ten_tep):
    if not ten_tep.lower().endswith(".pdf"):
        abort(404)
    return send_from_directory(THU_MUC_PDF, ten_tep, mimetype="application/pdf")
