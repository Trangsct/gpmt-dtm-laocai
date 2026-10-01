"""Các thao tác dùng chung cho lệnh CLI và trang web — để người dùng không chuyên làm được mọi việc
trên trình duyệt, không phải gõ lệnh.
"""
import io
import logging
import os
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from .extensions import db
from .models import TaiKhoan

log = logging.getLogger(__name__)

THU_MUC_BAN_GHI = Path(__file__).resolve().parent / "ban_ghi_doi_chieu"


# ---------------------------------------------------------------- Tự khởi tạo khi chạy lần đầu

def khoi_tao_tu_dong(app):
    """Tạo bảng còn thiếu; tạo hoặc CẤP LẠI tài khoản quản trị từ biến môi trường QUAN_TRI_EMAIL +
    QUAN_TRI_MAT_KHAU (đặt trên Vercel). Lỗi kết nối không làm sập ứng dụng."""
    try:
        with app.app_context():
            db.create_all()
            cap_quan_tri_tu_bien_moi_truong()
            dong_bo_ban_ghi_moi()
    except Exception:  # CSDL chưa sẵn sàng: vẫn cho ứng dụng chạy, trang /suc-khoe sẽ báo lỗi
        log.exception("Không khởi tạo được CSDL")


def cap_quan_tri_tu_bien_moi_truong():
    """Cấp lại quyền vào khi quên mật khẩu / đổi máy (Bạn yêu cầu 28/9/2026). Chỉ người giữ tài khoản Vercel
    mới đặt được biến nên an toàn hơn mọi nút "quên mật khẩu" trên trang công khai.
    - Chưa có tài khoản email đó: tạo mới, vai trò quản trị.
    - Đã có: đặt lại mật khẩu, bật hoạt động, nâng lên quản trị (chỉ khi mật khẩu đang khác, để khởi động lại
      không ghi CSDL vô ích). Vào được rồi thì xóa hai biến trên Vercel, nếu không mật khẩu đổi trên web sẽ bị
      đặt lại ở lần khởi động sau. Trả "tao" / "dat-lai" / None."""
    email = os.environ.get("QUAN_TRI_EMAIL", "").strip().lower()
    mk = os.environ.get("QUAN_TRI_MAT_KHAU", "")
    if not email or len(mk) < 10:
        return None
    tk = db.session.query(TaiKhoan).filter(db.func.lower(TaiKhoan.email) == email).first()
    if tk is None:
        tk = TaiKhoan(email=email, ho_ten=os.environ.get("QUAN_TRI_HO_TEN", "").strip() or "Quản trị viên",
                      vai_tro="quan_tri", hoat_dong=True)
        tk.dat_mat_khau(mk)
        db.session.add(tk)
        db.session.commit()
        log.warning("Đã tạo tài khoản quản trị từ biến môi trường: %s", email)
        return "tao"
    if tk.kiem_mat_khau(mk) and tk.hoat_dong and tk.vai_tro == "quan_tri":
        return None
    tk.dat_mat_khau(mk)
    tk.hoat_dong = True
    tk.vai_tro = "quan_tri"
    db.session.commit()
    log.warning("Đã cấp lại mật khẩu quản trị từ biến môi trường: %s", email)
    return "dat-lai"


# ---------------------------------------------------------------- Nhập sổ Excel + bản ghi đối chiếu tay

def da_co_du_lieu_so():
    from .models import Gpmt
    return db.session.query(Gpmt.id).filter(Gpmt.nguon_du_lieu.like("excel:%")).first() is not None


def _mo_ta(obj):
    from .models import Dtm, Gpmt
    if isinstance(obj, Gpmt):
        return f"GPMT {obj} — {obj.trang_thai}"
    if isinstance(obj, Dtm):
        return f"QĐ phê duyệt ĐTM {obj.so_qd}: {obj.co_so.ten if obj.co_so else ''}"
    return f"Hồ sơ {obj.loai}: {obj.co_so.ten if obj.co_so else ''} — {obj.trang_thai}"


def nhap_ban_ghi_doi_chieu(chi_ban_ghi_moi=False):
    """Nạp các bản ghi trong gpmt/ban_ghi_doi_chieu/*.json (GP đối chiếu tay, hồ sơ lấy từ Data360X).
    chi_ban_ghi_moi=True: bỏ qua bản ghi đã có trong CSDL (không ghi đè chỉnh sửa trên web)."""
    from .nhap_ban_ghi import da_co, doc_tep_json, nhap_mot
    tb = []
    for p in sorted(THU_MUC_BAN_GHI.glob("*.json")):
        for x in doc_tep_json(p):
            if chi_ban_ghi_moi and da_co(x):
                continue
            obj, ds = nhap_mot(x)
            tb.append(f"{_mo_ta(obj)} ({p.name})")
            tb += [f"  - {y}" for y in ds]
    return tb


def dong_bo_ban_ghi_moi(tai_khoan_id=None):
    """Chạy mỗi lần ứng dụng khởi động: nạp bản ghi mới thêm vào kho mã (sau khi đã nhập sổ Excel).
    Có bản ghi mới thì lưu báo cáo 'Đồng bộ bản ghi mới' để người dùng thấy ở trang Nhập dữ liệu."""
    from .models import BaoCaoNhapLuu
    if not da_co_du_lieu_so():
        return []
    db.session.info["tat_nhat_ky"] = True
    try:
        tb = nhap_ban_ghi_doi_chieu(chi_ban_ghi_moi=True)
    finally:
        db.session.info.pop("tat_nhat_ky", None)
    if tb:
        so = sum(1 for x in tb if not x.startswith(" "))
        db.session.add(BaoCaoNhapLuu(
            loai="dong-bo", tai_khoan_id=tai_khoan_id, ten_tep="gpmt/ban_ghi_doi_chieu/",
            tom_tat=f"Nạp {so} bản ghi mới", noi_dung=f"# Đồng bộ bản ghi mới — {date.today().strftime('%d/%m/%Y')}\n\n"
            + "\n".join(f"- {x}" if not x.startswith(" ") else x for x in tb) + "\n"))
        db.session.commit()
    return tb


def nhap_so(duong_dan=None, noi_dung=None, ten_tep="", tai_khoan_id=None):
    """Nhập sổ theo dõi + các bản ghi đối chiếu tay; lưu báo cáo vào CSDL. Trả BaoCaoNhapLuu."""
    from .models import BaoCaoNhapLuu, Gpmt
    from .nhap_excel import doc_so_theo_doi, nhap_vao_csdl, viet_bao_cao
    du_lieu = doc_so_theo_doi(duong_dan, noi_dung=noi_dung)
    # Nhập hàng loạt: không ghi nhật ký từng dòng — báo cáo nhập bên dưới là bản lưu vết
    db.session.info["tat_nhat_ky"] = True
    try:
        bc = nhap_vao_csdl(du_lieu)
        tb = nhap_ban_ghi_doi_chieu()
    finally:
        db.session.info.pop("tat_nhat_ky", None)
    md = viet_bao_cao(bc, ten_tep or Path(str(duong_dan)).name)
    if tb:
        md += "\n## 7. Giấy phép đã đối chiếu tay với bản gốc PDF\n\n" + "\n".join(f"- {x}" if not x.startswith(" ")
                                                                           else x for x in tb) + "\n"
    so_ra_soat = db.session.query(Gpmt).filter(Gpmt.can_ra_soat.is_(True)).count()
    tong = db.session.query(Gpmt).count()
    luu = BaoCaoNhapLuu(loai="so-excel", ten_tep=ten_tep, tai_khoan_id=tai_khoan_id, noi_dung=md,
                        tom_tat=f"{tong} giấy phép; {so_ra_soat} bản ghi cần rà soát; "
                                f"{len(bc.canh_bao)} cảnh báo đã tự xử lý")
    db.session.add(luu)
    db.session.commit()
    return luu


def xoa_du_lieu_nghiep_vu():
    """Xóa GPMT, cơ sở, chủ thể, VHTN, ĐTM, hồ sơ, ĐKMT để nhập lại từ đầu. Giữ tài khoản, nhật ký, báo cáo."""
    from .models import (BaoCaoBvmt, ChuThe, CoSoDuAn, DangKyMoiTruong, Dtm, Gpmt, GpmtChatThai, GpmtXaThai,
                         HoSo, KiemTra, Vhtn)
    for m in (GpmtXaThai, GpmtChatThai, Vhtn, HoSo, DangKyMoiTruong, BaoCaoBvmt, KiemTra):
        db.session.query(m).delete()
    db.session.query(Gpmt).update({Gpmt.thay_the_gpmt_id: None, Gpmt.dieu_chinh_gpmt_id: None})
    for m in (Gpmt, Dtm, CoSoDuAn, ChuThe):
        db.session.query(m).delete()
    db.session.commit()


# ---------------------------------------------------------------- Mẫu Excel bổ sung thời hạn / ngày ký

COT_MAU = ["Mã (không sửa)", "Số hiệu", "Ngày ký (dd/mm/yyyy)", "Cơ sở / dự án", "Cơ quan cấp",
           "Thời hạn (năm) — đọc tại Điều 3 của GP", "Ngày hết hạn ghi trong GP (nếu có, dd/mm/yyyy)",
           "Trạng thái hiện tại"]


def xuat_mau_bo_sung(ds_gpmt) -> io.BytesIO:
    """Bảng để cán bộ điền thời hạn/ngày ký còn thiếu rồi tải lên lại. Cột vàng là cột được điền."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Bo sung"
    ws.append(COT_MAU)
    vang = PatternFill("solid", fgColor="FFF4D6")
    for i in range(1, len(COT_MAU) + 1):
        ws.cell(1, i).font = Font(bold=True)
    for gp in ds_gpmt:
        ws.append([gp.id, gp.so_hieu or "(chưa có số)",
                   gp.ngay_ky.strftime("%d/%m/%Y") if gp.ngay_ky else None,
                   gp.co_so.ten if gp.co_so else "", gp.co_quan_cap or "",
                   gp.thoi_han_nam,
                   gp.ngay_het_han_nhap_tay.strftime("%d/%m/%Y") if gp.ngay_het_han_nhap_tay else None,
                   gp.trang_thai])
    for r in range(2, ws.max_row + 1):
        for c in (3, 6, 7):
            ws.cell(r, c).fill = vang
    for i, w in enumerate([10, 20, 18, 60, 26, 22, 24, 26], 1):
        ws.column_dimensions[chr(64 + i)].width = w
    dv = DataValidation(type="decimal", operator="between", formula1="0.5", formula2="50", allow_blank=True,
                        error="Thời hạn là số năm, từ 0,5 đến 50.")
    ws.add_data_validation(dv)
    dv.add(f"F2:F{max(ws.max_row, 2)}")
    ws.freeze_panes = "A2"
    hd = wb.create_sheet("Huong dan")
    for dong in [
        "Cách dùng mẫu bổ sung:",
        "1. Mở từng GP (PDF), đọc Điều 3 'Thời hạn của Giấy phép' → ghi số năm vào cột F (vd 10, 7, 5).",
        "2. GP thiếu ngày ký: đọc dòng 'Lào Cai, ngày … tháng … năm …' trên trang 1 (PDF ký số: nhìn ảnh, không dựa vào chữ copy ra).",
        "3. Chỉ điền ô màu vàng. Không sửa cột 'Mã'. Ô để trống = giữ nguyên dữ liệu hiện có.",
        "4. Lưu tệp (.xlsx), vào trang 'Nhập dữ liệu' → 'Tải lên mẫu bổ sung'.",
        "Không chắc thì để trống — không suy thời hạn từ nhóm dự án.",
    ]:
        hd.append([dong])
    hd.column_dimensions["A"].width = 120
    tep = io.BytesIO()
    wb.save(tep)
    tep.seek(0)
    return tep


def _doc_ngay(v):
    if v in (None, ""):
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    for dinh_dang in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, dinh_dang).date()
        except ValueError:
            pass
    raise ValueError(f"ngày '{s}' không đúng dạng dd/mm/yyyy")


def _doc_so(v):
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).strip().replace(",", "."))


def nhap_mau_bo_sung(noi_dung: bytes, ten_tep="", tai_khoan_id=None):
    """Đọc mẫu đã điền; chỉ ghi ô có giá trị khác dữ liệu hiện có. Trả BaoCaoNhapLuu."""
    from .models import BaoCaoNhapLuu, Gpmt
    wb = load_workbook(io.BytesIO(noi_dung), data_only=True)
    ws = wb["Bo sung"] if "Bo sung" in wb.sheetnames else wb.active
    doi, loi = [], []
    for r in range(2, ws.max_row + 1):
        ma = ws.cell(r, 1).value
        if ma in (None, ""):
            continue
        try:
            gp = db.session.get(Gpmt, int(ma))
        except (TypeError, ValueError):
            gp = None
        if gp is None:
            loi.append(f"Dòng {r}: mã '{ma}' không có trong CSDL — bỏ qua")
            continue
        try:
            ngay_ky = _doc_ngay(ws.cell(r, 3).value)
            thoi_han = _doc_so(ws.cell(r, 6).value)
            het_han = _doc_ngay(ws.cell(r, 7).value)
            if thoi_han is not None and not 0.5 <= thoi_han <= 50:
                raise ValueError(f"thời hạn {thoi_han:g} năm không hợp lý (0,5–50)")
        except ValueError as e:
            loi.append(f"Dòng {r} ({gp.so_hieu}): {e} — bỏ qua cả dòng")
            continue
        thay = []
        if ngay_ky and ngay_ky != gp.ngay_ky:
            thay.append(f"ngày ký {gp.ngay_ky.strftime('%d/%m/%Y') if gp.ngay_ky else '∅'} → "
                        f"{ngay_ky.strftime('%d/%m/%Y')}")
            gp.ngay_ky, gp.nam_cap = ngay_ky, ngay_ky.year
        if thoi_han is not None and thoi_han != gp.thoi_han_nam:
            thay.append(f"thời hạn {gp.thoi_han_nam or '∅'} → {thoi_han:g} năm")
            gp.thoi_han_nam = thoi_han
        if het_han and het_han != gp.ngay_het_han_nhap_tay:
            thay.append(f"ngày hết hạn ghi trong GP → {het_han.strftime('%d/%m/%Y')}")
            gp.ngay_het_han_nhap_tay = het_han
        if thay:
            doi.append(f"{gp.so_hieu or '(chưa có số)'} (mã {gp.id}): " + "; ".join(thay)
                       + f" → trạng thái: {gp.trang_thai}")
    md = [f"# Bổ sung thời hạn / ngày ký — {date.today().strftime('%d/%m/%Y')}", "",
          f"Tệp: `{ten_tep}`", "", f"## Đã cập nhật: {len(doi)} giấy phép", ""]
    md += [f"- {x}" for x in doi] or ["(không có thay đổi)"]
    md += ["", f"## Dòng lỗi, bỏ qua: {len(loi)}", ""] + ([f"- {x}" for x in loi] or ["(không có)"])
    luu = BaoCaoNhapLuu(loai="bo-sung-thoi-han", ten_tep=ten_tep, tai_khoan_id=tai_khoan_id,
                        noi_dung="\n".join(md) + "\n", tom_tat=f"Cập nhật {len(doi)} GP; {len(loi)} dòng lỗi")
    db.session.add(luu)
    db.session.commit()
    return luu
