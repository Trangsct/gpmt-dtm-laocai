"""Giới hạn dữ liệu theo tài khoản (mục 7 HUONG_DAN.md).

Tài khoản bên ngoài (BQL các KCN, UBND xã) chỉ thấy cơ sở trong phạm vi của mình và không thấy
thông tin nội bộ (hồ sơ đang giải quyết, ghi chú, lý do rà soát, nhật ký).
"""
from flask import abort
from flask_login import current_user

from ..models import CoSoDuAn


def loc_co_so(q):
    """Áp phạm vi lên một truy vấn đã join CoSoDuAn."""
    if current_user.noi_bo:
        return q
    if current_user.pham_vi_xa:
        q = q.filter(CoSoDuAn.xa_phuong_moi.ilike(f"%{current_user.pham_vi_xa}%"))
    if current_user.pham_vi_kcn:
        q = q.filter(CoSoDuAn.kcn_ccn.isnot(None))
    return q


def duoc_xem_co_so(cs):
    if cs is None or current_user.noi_bo:
        return True
    if current_user.pham_vi_xa and current_user.pham_vi_xa.lower() not in (cs.xa_phuong_moi or "").lower():
        return False
    if current_user.pham_vi_kcn and not cs.kcn_ccn:
        return False
    return True


def kiem_co_so(cs):
    if not duoc_xem_co_so(cs):
        abort(403)
