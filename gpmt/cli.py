"""Lệnh quản trị: `flask --app gpmt <lệnh>` (xem README.md)."""
import os
from datetime import date
from pathlib import Path

import click

from .extensions import db
from .models import VAI_TRO, TaiKhoan


def dang_ky_lenh(app):

    @app.cli.command("khoi-tao-csdl")
    def khoi_tao_csdl():
        """Tạo các bảng còn thiếu (không xóa dữ liệu có sẵn)."""
        db.create_all()
        click.echo(f"Đã tạo bảng trên {db.engine.url.render_as_string(hide_password=True)}")

    @app.cli.command("tao-tai-khoan")
    @click.option("--email", required=True)
    @click.option("--ho-ten", required=True)
    @click.option("--vai-tro", type=click.Choice(list(VAI_TRO)), default="chi_xem", show_default=True)
    @click.option("--don-vi", default=None, help="Phòng … / BQL các KCN / UBND xã …")
    @click.option("--pham-vi-xa", default=None, help="Tài khoản UBND xã: chỉ thấy cơ sở trên địa bàn xã này")
    @click.option("--pham-vi-kcn", is_flag=True, help="Tài khoản BQL các KCN: chỉ thấy cơ sở trong KCN/CCN")
    def tao_tai_khoan(email, ho_ten, vai_tro, don_vi, pham_vi_xa, pham_vi_kcn):
        """Tạo hoặc cập nhật tài khoản. Mật khẩu lấy từ biến MAT_KHAU hoặc nhập khi được hỏi."""
        mk = os.environ.get("MAT_KHAU") or click.prompt("Mật khẩu", hide_input=True, confirmation_prompt=True)
        if len(mk) < 10:
            raise click.ClickException("Mật khẩu phải có ít nhất 10 ký tự.")
        email = email.strip().lower()
        tk = db.session.query(TaiKhoan).filter_by(email=email).first() or TaiKhoan(email=email)
        tk.ho_ten, tk.vai_tro, tk.don_vi = ho_ten, vai_tro, don_vi
        tk.pham_vi_xa, tk.pham_vi_kcn, tk.hoat_dong = pham_vi_xa, pham_vi_kcn, True
        tk.dat_mat_khau(mk)
        db.session.add(tk)
        db.session.commit()
        click.echo(f"Đã lưu tài khoản {email} ({VAI_TRO[vai_tro]})")

    @app.cli.command("nhap-excel")
    @click.argument("tep_xls", type=click.Path(exists=True, dir_okay=False))
    @click.option("--bao-cao", "tep_bao_cao", default=None,
                  help="Nơi ghi báo cáo nhập (mặc định bao-cao/nhap-du-lieu-<ngày>.md)")
    def nhap_excel(tep_xls, tep_bao_cao):
        """Nhập sổ theo dõi GPMT (.xls) vào CSDL và ghi báo cáo nhập."""
        from .nhap_excel import doc_so_theo_doi, nhap_vao_csdl, viet_bao_cao
        db.create_all()
        du_lieu = doc_so_theo_doi(tep_xls)
        bc = nhap_vao_csdl(du_lieu)
        noi_dung = viet_bao_cao(bc, Path(tep_xls).name)
        tep_bao_cao = Path(tep_bao_cao or f"bao-cao/nhap-du-lieu-{date.today().isoformat()}.md")
        tep_bao_cao.parent.mkdir(parents=True, exist_ok=True)
        tep_bao_cao.write_text(noi_dung, encoding="utf-8")
        from .models import Gpmt
        so_ra_soat = db.session.query(Gpmt).filter(Gpmt.can_ra_soat.is_(True)).count()
        click.echo(f"Đã nhập {bc.so_gpmt_tao} GPMT, {bc.so_co_so} cơ sở; {so_ra_soat} bản ghi cần rà soát; "
                   f"{len(bc.canh_bao)} cảnh báo. Báo cáo: {tep_bao_cao}")

    @app.cli.command("nhap-ban-ghi")
    @click.argument("tep_json", type=click.Path(exists=True, dir_okay=False))
    def nhap_ban_ghi(tep_json):
        """Nhập một GPMT đã đối chiếu tay (JSON), vd du-lieu-goc/ban-ghi-doi-chieu/2519_GPMT-UBND.json."""
        from .nhap_ban_ghi import nhap_tep_json
        db.create_all()
        gp, tb = nhap_tep_json(tep_json)
        click.echo(f"Đã lưu {gp}. Trạng thái: {gp.trang_thai}")
        for x in tb:
            click.echo(f"  - {x}")

    @app.cli.command("xoa-du-lieu-nhap")
    @click.confirmation_option(prompt="Xóa TOÀN BỘ GPMT, cơ sở, chủ thể, VHTN, ĐTM, hồ sơ? (tài khoản và nhật ký giữ nguyên)")
    def xoa_du_lieu_nhap():
        """Xóa dữ liệu nghiệp vụ để nhập lại sổ từ đầu (giữ tài khoản, nhật ký)."""
        from .models import (BaoCaoBvmt, ChuThe, CoSoDuAn, DangKyMoiTruong, Dtm, Gpmt, GpmtChatThai,
                             GpmtXaThai, HoSo, KiemTra, Vhtn)
        for m in (GpmtXaThai, GpmtChatThai, Vhtn, HoSo, DangKyMoiTruong, BaoCaoBvmt, KiemTra):
            db.session.query(m).delete()
        db.session.query(Gpmt).update({Gpmt.thay_the_gpmt_id: None, Gpmt.dieu_chinh_gpmt_id: None})
        for m in (Gpmt, Dtm, CoSoDuAn, ChuThe):
            db.session.query(m).delete()
        db.session.commit()
        click.echo("Đã xóa dữ liệu nghiệp vụ.")
