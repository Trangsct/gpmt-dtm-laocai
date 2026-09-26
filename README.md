# Quản lý Giấy phép môi trường (GPMT) và báo cáo ĐTM — Sở NN&MT tỉnh Lào Cai

Ứng dụng web nội bộ để lưu, tra cứu GPMT và quyết định phê duyệt ĐTM trên địa bàn tỉnh Lào Cai (gồm cả địa bàn
Yên Bái cũ); theo dõi vòng đời GP (cấp mới → điều chỉnh → cấp lại → hết hạn), VHTN, hồ sơ đang giải quyết; cảnh
báo và xuất báo cáo theo mẫu Phụ lục 6.4. Yêu cầu đầy đủ: [`HUONG_DAN.md`](HUONG_DAN.md).

**Kho riêng tư.** Sổ theo dõi, CSDL, PDF và báo cáo nhập là thông tin nội bộ — không đưa lên nơi công khai.

## Trạng thái: giai đoạn 1 (MVP)

| Chức năng | Tình trạng |
|---|---|
| Nhập sổ Excel + báo cáo nhập (dòng đã vào, dòng gắn cờ `can_ra_soat` và lý do) | xong — `bao-cao/nhap-du-lieu-<ngày>.md` |
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
flask nhap-ban-ghi du-lieu-goc/ban-ghi-doi-chieu/2519_GPMT-UBND.json
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

| Vai trò | Quyền |
|---|---|
| Quản trị | sửa dữ liệu, xóa, cấp tài khoản |
| Biên tập | nhập, sửa dữ liệu |
| Chỉ xem (trong Sở) | xem tất cả, kể cả hồ sơ đang giải quyết, ghi chú, lý do rà soát, nhật ký |
| Xem giới hạn (BQL các KCN / UBND xã) | chỉ xem GPMT, ĐTM, cơ sở trong phạm vi: theo xã/phường (`pham_vi_xa`) hoặc chỉ cơ sở trong KCN/CCN (`pham_vi_kcn`); không thấy thông tin nội bộ |

Tài khoản do quản trị cấp (trang **Tài khoản** hoặc lệnh `flask tao-tai-khoan`); không có trang tự đăng ký.

## Triển khai chạy thử: Vercel + Neon

1. **Neon** (Vercel → Storage → Neon, gói miễn phí): tạo CSDL, lấy chuỗi kết nối.
2. **Vercel**: Import kho này (Private). Tên dự án `gpmt-dtm-laocai` → `https://gpmt-dtm-laocai.vercel.app`
   (tên đã có người dùng thì đặt `gpmt-laocai`). Biến môi trường (Settings → Environment Variables):
   - `DATABASE_URL` — chuỗi kết nối Neon (tích hợp Storage tự điền);
   - `SECRET_KEY` — chuỗi ngẫu nhiên dài (`python3 -c "import secrets; print(secrets.token_hex(32))"`);
   - `SESSION_COOKIE_SECURE=1`;
   - `PDF_BASE_URL` — nơi lưu PDF riêng tư (tùy chọn; để trống thì nút "Mở PDF gốc" ẩn).
3. **Khởi tạo và nhập dữ liệu từ máy cục bộ** vào Neon (hệ tệp Vercel chỉ đọc, không chạy lệnh CLI ở đó):
   ```bash
   export DATABASE_URL='<chuỗi kết nối Neon>' FLASK_APP=gpmt
   flask khoi-tao-csdl && flask nhap-excel du-lieu-goc/So_theo_doi_cap_GPMT_hang_nam_Lao_Cai.xls
   flask nhap-ban-ghi du-lieu-goc/ban-ghi-doi-chieu/2519_GPMT-UBND.json
   flask tao-tai-khoan --email <email> --ho-ten "<Họ tên>" --vai-tro quan_tri
   ```
4. `.vercelignore` loại `du-lieu-goc/`, `bao-cao/`, `tests/` khỏi bản triển khai.

Mã nguồn không gắn cứng tên miền/nơi chạy (xem `.env.example`). Khi Sở chuyển sang máy chủ riêng hoặc tên miền
`….laocai.gov.vn`: chạy `gunicorn 'gpmt:create_app()'` sau reverse proxy, đặt cùng các biến môi trường, `PDF_DIR`
trỏ tới thư mục PDF — không phải sửa code.

## Cấu trúc

```
gpmt/
  models.py        mô hình dữ liệu (mục 4 HUONG_DAN.md)
  phan_tich.py     tách số/ngày GP, đọc số kiểu Việt, KCN/CCN
  trang_thai.py    tính ngày hết hạn, trạng thái
  nhap_excel.py    nhập sổ theo dõi + báo cáo nhập
  nhap_ban_ghi.py  nhập GP đã đối chiếu tay (JSON)
  xuat_excel.py    xuất Phụ lục 6.4
  nhat_ky.py       lưu vết thay đổi
  auth.py          đăng nhập, vai trò, CSRF
  views/           các trang web;  templates/, static/
api/index.py       điểm vào Vercel
du-lieu-goc/       sổ Excel, PDF gốc, bản ghi đối chiếu tay (nội bộ)
bao-cao/           báo cáo nhập dữ liệu (nội bộ)
tests/             kiểm thử
```
