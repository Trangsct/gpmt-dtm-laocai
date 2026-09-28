# Quản lý Giấy phép môi trường (GPMT) và báo cáo ĐTM — Sở NN&MT tỉnh Lào Cai

Ứng dụng web nội bộ để lưu, tra cứu GPMT và quyết định phê duyệt ĐTM trên địa bàn tỉnh Lào Cai (gồm cả địa bàn
Yên Bái cũ); theo dõi vòng đời GP (cấp mới → điều chỉnh → cấp lại → hết hạn), VHTN, hồ sơ đang giải quyết; cảnh
báo và xuất báo cáo theo mẫu Phụ lục 6.4. Yêu cầu đầy đủ: [`HUONG_DAN.md`](HUONG_DAN.md).

**Kho riêng tư.** Sổ theo dõi, CSDL, PDF và báo cáo nhập là thông tin nội bộ — không đưa lên nơi công khai.

## Trạng thái: giai đoạn 1 (MVP)

| Chức năng | Tình trạng |
|---|---|
| Nhập sổ Excel + báo cáo nhập (dòng đã vào, dòng gắn cờ `can_ra_soat` và lý do) — trên web (menu **Nhập dữ liệu**) hoặc lệnh | xong |
| Bổ sung thời hạn/ngày ký hàng loạt qua mẫu Excel tải về – điền – tải lên | xong |
| Danh sách GPMT: tìm theo số hiệu, cơ sở, chủ cơ sở, MST; lọc năm, cơ quan cấp, địa bàn cũ, xã/phường, loại hình, nhóm, KCN/CCN, trạng thái | xong |
| Chi tiết GPMT: thông tin chung, xả thải, chất thải, VHTN, chuỗi thay thế, mở PDF gốc | xong |
| Chi tiết cơ sở: dòng thời gian GPMT, ĐTM, VHTN, ĐKMT, hồ sơ | xong |
| Bảng điều khiển: GP theo năm/cơ quan cấp, sắp hết hạn, VHTN quá hạn, hồ sơ đang giải quyết, cần rà soát | xong |
| Nhập/sửa tay qua biểu mẫu, đăng nhập, phân quyền, nhật ký mọi thay đổi | xong |
| Xuất Excel mẫu Phụ lục 6.4 (theo bộ lọc đang chọn) | xong |
| ĐTM, hồ sơ đang giải quyết, đăng ký môi trường: nhập tay cơ bản | xong (đầy đủ ở giai đoạn 2) |
| Tải PDF → đọc tự động → duyệt; module ĐTM đầy đủ; bản đồ; báo cáo BVMT định kỳ | giai đoạn 2 |

## Chạy cục bộ

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
export FLASK_APP=gpmt                      # không đặt DATABASE_URL → dùng SQLite gpmt-local.sqlite3

flask khoi-tao-csdl
flask nhap-excel du-lieu-goc/So_theo_doi_cap_GPMT_hang_nam_Lao_Cai.xls
flask nhap-ban-ghi gpmt/ban_ghi_doi_chieu/2519_GPMT-UBND.json
flask tao-tai-khoan --email <email> --ho-ten "<Họ tên>" --vai-tro quan_tri   # hỏi mật khẩu
flask run                                  # http://127.0.0.1:5000
```

Kiểm thử: `python3 -m pytest -q`.

## Nhập dữ liệu

- **Sổ Excel** (`flask nhap-excel <tệp.xls>`): đọc 3 sheet GPMT + sheet VHTN, tách số/ngày từ cột "Giấy phép số",
  chuẩn hóa số liệu chất thải (giữ nguyên văn ở `*_goc`, chỉ điền `*_so` khi chắc chắn), ghép sheet VHTN theo số
  GP rồi theo tên, gộp dòng trùng, gắn cờ mọi chỗ chưa chắc. Chỉ chạy trên CSDL chưa có dữ liệu sổ; muốn nhập lại:
  `flask xoa-du-lieu-nhap` (giữ tài khoản, nhật ký).
- **GP đã đối chiếu tay** (`flask nhap-ban-ghi <tệp.json>`): dùng cho GP đọc từ PDF khi chưa có bộ đọc tự động.
  Có trường `thay_the` thì GP cũ tự chuyển "Hết hiệu lực — bị thay thế". Chạy lại không sinh bản trùng.
- **Nhập tay trên web**: tài khoản Biên tập/Quản trị.
- **PDF ký số**: số và ngày điền qua trường ký số, lớp chữ để trống → đọc trên ảnh trang 1. Không kết luận "chưa
  có số" từ lớp chữ. Ký hiệu lấy theo trang bìa.

## Người dùng và phân quyền

**Công khai** (Bạn chốt 27/9/2026, biến `CONG_KHAI`, mặc định bật): ai cũng xem, tìm, xuất Excel được GPMT, ĐTM,
cơ sở, đăng ký môi trường mà không cần đăng nhập — quyền như vai trò "Xem giới hạn" không giới hạn phạm vi.

| Vai trò | Quyền |
|---|---|
| Quản trị | sửa dữ liệu, xóa, cấp tài khoản |
| Biên tập | nhập, sửa dữ liệu |
| Chỉ xem (trong Sở) | xem tất cả, kể cả hồ sơ đang giải quyết, ghi chú, lý do rà soát, nhật ký |
| Xem giới hạn (BQL các KCN / UBND xã) | chỉ xem GPMT, ĐTM, cơ sở trong phạm vi: theo xã/phường (`pham_vi_xa`) hoặc chỉ cơ sở trong KCN/CCN (`pham_vi_kcn`); không thấy thông tin nội bộ |

Tài khoản do quản trị cấp (trang **Tài khoản** hoặc lệnh `flask tao-tai-khoan`); không có trang tự đăng ký.

## Triển khai chạy thử: Vercel + Neon

Hướng dẫn từng bước cho người không chuyên: **[`HUONG_DAN_TRIEN_KHAI.md`](HUONG_DAN_TRIEN_KHAI.md)**. Tóm tắt:

1. Vercel: Import kho (Private), tên dự án `gpmt-dtm-laocai` → `https://gpmt-dtm-laocai.vercel.app`
   (tên đã có người dùng thì `gpmt-laocai`).
2. Vercel → Storage → Neon (Free, Singapore) → Connect vào dự án: tự thêm `DATABASE_URL`.
3. Mở `/cai-dat` để tạo tài khoản quản trị đầu tiên (chỉ mở khi CSDL chưa có tài khoản nào; tạo xong tự khóa).
   Cách khác: đặt `QUAN_TRI_EMAIL`, `QUAN_TRI_MAT_KHAU` (≥ 10 ký tự), `QUAN_TRI_HO_TEN` → Redeploy. Cũng là cách cấp lại
   mật khẩu khi quên / vào máy mới (email đã có thì đặt lại mật khẩu); vào được thì xóa biến và Redeploy lại.
   Ứng dụng tự tạo bảng ở lần chạy đầu. `/suc-khoe` tự chẩn đoán cấu hình bằng tiếng Việt.
4. Đăng nhập → **Nhập dữ liệu** → tải sổ `.xls` lên (tự nhập kèm GP đã đối chiếu tay trong
   `gpmt/ban_ghi_doi_chieu/`).

Không bắt buộc: `SECRET_KEY` (không đặt thì suy ra từ chuỗi kết nối CSDL), `SESSION_COOKIE_SECURE` (tự bật trên
Vercel), `PDF_BASE_URL`. Xem `.env.example`. `.vercelignore` loại `du-lieu-goc/`, `bao-cao/`, `tests/`.

Mã nguồn không gắn cứng tên miền/nơi chạy. Khi Sở chuyển sang máy chủ riêng hoặc tên miền `….laocai.gov.vn`:
chạy WSGI `gpmt:create_app()` (vd gunicorn) sau reverse proxy, đặt cùng các biến môi trường, `PDF_DIR` trỏ tới
thư mục PDF — không phải sửa code.

## Cấu trúc

```
gpmt/
  models.py        mô hình dữ liệu (mục 4 HUONG_DAN.md)
  phan_tich.py     tách số/ngày GP, đọc số kiểu Việt, KCN/CCN
  trang_thai.py    tính ngày hết hạn, trạng thái
  nhap_excel.py    nhập sổ theo dõi + báo cáo nhập
  nhap_ban_ghi.py  nhập GP đã đối chiếu tay (JSON trong ban_ghi_doi_chieu/)
  dich_vu.py       tự khởi tạo, nhập sổ qua web, mẫu bổ sung thời hạn (dùng chung CLI + web)
  xuat_excel.py    xuất Phụ lục 6.4
  nhat_ky.py       lưu vết thay đổi
  auth.py          đăng nhập, vai trò, CSRF
  views/           các trang web;  templates/, static/
api/index.py       điểm vào Vercel
du-lieu-goc/       sổ Excel, PDF gốc (nội bộ)
bao-cao/           báo cáo nhập dữ liệu (nội bộ)
tests/             kiểm thử
```
