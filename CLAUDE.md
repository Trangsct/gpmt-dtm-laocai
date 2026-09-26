# CLAUDE.md — quy ước cho các phiên làm việc sau

Ứng dụng quản lý GPMT và ĐTM của Sở NN&MT tỉnh Lào Cai. Yêu cầu gốc: `HUONG_DAN.md` (đọc trước khi làm).
Cách chạy, triển khai: `README.md`.

## Nguyên tắc bắt buộc

- **Dự án đứng độc lập**: không dùng chung, không liên kết, không chép dữ liệu/mã từ kho khác.
- **Kho riêng tư, dữ liệu nội bộ**: không đưa sổ theo dõi, CSDL, PDF, báo cáo nhập lên nơi công khai. Không commit
  mật khẩu, khóa, chuỗi kết nối CSDL, email cá nhân — để trong biến môi trường (`.env.example`).
- **Không bịa số, ngày, tên.** Không chắc thì để trống, gắn `can_ra_soat` + lý do (`Gpmt.them_ly_do`), liệt kê
  trong báo cáo. Không tự đoán loại văn bản (`QĐ-UBND`, `GPTN-UBND`, `GPTNMT-UBND` → "chưa rõ", gắn cờ — Bạn chốt
  26/9/2026).
- **PDF ký số**: số/ngày điền qua trường ký số; lớp chữ để trống. Đọc trên ảnh trang 1 (PyMuPDF render hoặc
  `pdftoppm`) hoặc theo tọa độ dòng "Số:". Ký hiệu lấy theo trang bìa, không theo phụ lục.
- **Không cứng hóa quy định pháp luật vào code.** Thời hạn GP đọc từ Điều 3 của chính GP; không suy từ nhóm dự
  án. Trạng thái GP luôn tính lại (`gpmt/trang_thai.py`), không lưu cứng.
- Quan hệ **thay thế** (`thay_the_gpmt_id`) chỉ gắn khi GP mới ghi rõ GP cũ hết hiệu lực. **Điều chỉnh**
  (`dieu_chinh_gpmt_id`) không làm GP cũ hết hiệu lực.
- Số liệu: `*_goc` giữ nguyên văn; `*_so`/`*_don_vi` chỉ điền khi chắc chắn; quy đổi kg/năm chỉ từ kg/năm, tấn/năm.

## Quy trình

- Giao tiếp, giao diện, comment, commit message: **tiếng Việt**, ghi rõ lý do.
- Làm trên nhánh làm việc, mở PR vào `main` và **merge ngay, không cần hỏi** (Bạn chốt 26/9/2026, áp dụng
  vĩnh viễn — thay cho quy định "hỏi trước khi merge" ở mục 8 HUONG_DAN.md). Kiểm thử phải xanh trước khi merge.
- Làm theo giai đoạn: xong giai đoạn 1 → chạy thử, gửi ảnh màn hình + báo cáo nhập, **chờ duyệt** rồi mới sang
  giai đoạn 2.
- Trước khi commit: `python3 -m pytest -q` phải xanh.
- Báo cáo cuối phiên: đã làm gì, đường dẫn chạy thử, danh sách dòng cần rà, việc còn treo.

## Quyết định đã chốt (26–27/9/2026)

- **27/9/2026 — Công khai**: dữ liệu GPMT không bí mật, cần công khai cho người dân và doanh nghiệp → xem không
  cần đăng nhập (`CONG_KHAI`, mặc định bật; khách = `KhachXem` trong `auth.py`, dùng decorator `can_xem`).
  Vẫn chỉ cán bộ đăng nhập mới thấy hồ sơ đang giải quyết, lý do rà soát, nhật ký, ghi chú nội bộ (mục 7
  HUONG_DAN.md: công khai chỉ các trường đã công khai) — hỏi Bạn trước khi mở thêm.
- **27/9/2026 — Tài khoản quản trị đơn giản**: trang `/cai-dat` tạo quản trị đầu tiên khi CSDL chưa có tài khoản
  nào, tạo xong tự khóa; không bắt đặt biến trên Vercel.

- Người dùng: Sở + BQL các KCN + UBND xã. Tài khoản bên ngoài = vai trò `ben_ngoai`, giới hạn theo
  `pham_vi_xa` / `pham_vi_kcn`, không thấy thông tin nội bộ (hồ sơ, ghi chú, lý do rà soát, nhật ký).
- CSDL chạy thử: **Neon** (PostgreSQL miễn phí) + Vercel.
- Phạm vi: GPMT + ĐTM + **đăng ký môi trường** (bảng `dang_ky_moi_truong` có từ giai đoạn 1, giao diện đầy đủ ở
  giai đoạn 2).
- Chưa chốt: nơi triển khai chính thức, tên miền `….laocai.gov.vn` (không chặn giai đoạn 1).

## Ghi chú kỹ thuật

- Flask + SQLAlchemy + Jinja2, không bundler. Cấu hình đọc từ biến môi trường (`gpmt/config.py`).
- Không có migration tool: `flask khoi-tao-csdl` chỉ tạo bảng thiếu. Đổi cột trên CSDL đã có dữ liệu → viết lệnh
  ALTER riêng hoặc thêm Alembic khi cần.
- Nhật ký: `gpmt/nhat_ky.py` bắt sự kiện flush của SQLAlchemy, chỉ ghi khi có người dùng đăng nhập. Nhập sổ hàng
  loạt (CLI hoặc web) tắt nhật ký từng dòng qua `session.info["tat_nhat_ky"]`; bản lưu vết là báo cáo nhập trong
  bảng `bao_cao_nhap`.
- Người dùng không chuyên (Bạn chốt 26/9/2026): việc gì làm được trên web thì làm trên web, không bắt gõ lệnh.
  Hướng dẫn cho người dùng: `HUONG_DAN_TRIEN_KHAI.md` — cập nhật khi thêm/đổi bước.
- CSDL: SQLAlchemy 2.1 mặc định `postgresql://` dùng psycopg 3; `config.py` đổi sang `postgresql+psycopg2://`.
  Đã chạy thử trên PostgreSQL 16 thật (26/9/2026).
- GP đọc từ PDF đã đối chiếu tay: thêm tệp JSON vào `gpmt/ban_ghi_doi_chieu/` (theo mẫu 2519) — tự nạp khi
  nhập sổ.
- Sổ Excel: sheet "GPMT tỉnh YB cũ" có 61 dòng đánh số + 5 dòng không số TT (vẫn là dữ liệu thật). Sổ có 8 văn bản
  `QĐ-UBND` (bài giao việc ghi 9). Số hiệu 1827/GPMT-UBND ngày 16/9/2024 ghi cho 2 cơ sở khác nhau → cả hai gắn cờ.
