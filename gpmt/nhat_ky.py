"""Lưu vết mọi lần thêm/sửa/xóa qua web vào bảng `nhat_ky` (mục 5.6 HUONG_DAN.md).

Chỉ ghi khi có người dùng đăng nhập trong request; lệnh nhập dữ liệu hàng loạt (CLI) ghi
báo cáo nhập riêng nên không làm phình nhật ký.
"""
import json
from datetime import date, datetime

from flask import has_request_context
from flask_login import current_user
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session


BANG_KHONG_GHI = {"nhat_ky"}


def _gt(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v


def _nguoi_dung_id():
    if not has_request_context():
        return None
    try:
        return current_user.id if current_user.is_authenticated else None
    except Exception:
        return None


def _truong(obj):
    return [c.key for c in inspect(obj).mapper.column_attrs]


def _before_flush(session, flush_context, instances):
    uid = _nguoi_dung_id()
    if uid is None:
        return
    ghi = []
    for obj in session.new:
        if getattr(obj, "__tablename__", None) in BANG_KHONG_GHI or not hasattr(obj, "__tablename__"):
            continue
        ghi.append((obj, "them", {k: [None, _gt(getattr(obj, k))] for k in _truong(obj)
                                   if getattr(obj, k) is not None}))
    for obj in session.dirty:
        if getattr(obj, "__tablename__", None) in BANG_KHONG_GHI or not session.is_modified(obj):
            continue
        tt = inspect(obj)
        doi = {}
        for k in _truong(obj):
            h = tt.attrs[k].history
            if h.has_changes():
                cu = h.deleted[0] if h.deleted else None
                moi = h.added[0] if h.added else None
                if cu != moi:
                    doi[k] = [_gt(cu), _gt(moi)]
        if doi:
            ghi.append((obj, "sua", doi))
    for obj in session.deleted:
        if getattr(obj, "__tablename__", None) in BANG_KHONG_GHI:
            continue
        ghi.append((obj, "xoa", {k: [_gt(getattr(obj, k)), None] for k in _truong(obj)}))
    session.info.setdefault("nhat_ky_cho", []).extend((o, h, d, uid) for o, h, d in ghi)


def _after_flush(session, flush_context):
    cho = session.info.pop("nhat_ky_cho", [])
    if not cho:
        return
    from .models import NhatKy
    # Ghi thẳng qua connection của flush hiện tại (không session.add trong lúc flush)
    session.connection().execute(NhatKy.__table__.insert(), [
        dict(tai_khoan_id=uid, thoi_diem=datetime.now(), bang=obj.__tablename__,
             ban_ghi=getattr(obj, "id", None), hanh_dong=hanh_dong,
             thay_doi=json.dumps(doi, ensure_ascii=False, default=str))
        for obj, hanh_dong, doi, uid in cho])


_da_dang_ky = False


def dang_ky_nhat_ky():
    global _da_dang_ky
    if _da_dang_ky:
        return
    event.listen(Session, "before_flush", _before_flush)
    event.listen(Session, "after_flush", _after_flush)
    _da_dang_ky = True
