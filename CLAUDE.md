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
- Làm trên nhánh làm việc, mở PR vào `main`, **hỏi người giao việc trước khi merge**.
- Làm theo giai đoạn: xong giai đoạn 1 → chạy thử, gửi ảnh màn hình + báo cáo nhập, **chờ duyệt** rồi mới sang
  giai đoạn 2.
- Trước khi commit: `python3 -m pytest -q` phải xanh.
- Báo cáo cuối phiên: đã làm gì, đường dẫn chạy thử, danh sách dòng cần rà, việc còn treo.

## Quyết định đã chốt (26/9/2026)

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
- Nhật ký: `gpmt/nhat_ky.py` bắt sự kiện flush của SQLAlchemy, chỉ ghi khi có người dùng đăng nhập (lệnh CLI
  không ghi nhật ký; nhập hàng loạt đã có báo cáo nhập).
- Sổ Excel: sheet "GPMT tỉnh YB cũ" có 61 dòng đánh số + 5 dòng không số TT (vẫn là dữ liệu thật). Sổ có 8 văn bản
  `QĐ-UBND` (bài giao việc ghi 9). Số hiệu 1827/GPMT-UBND ngày 16/9/2024 ghi cho 2 cơ sở khác nhau → cả hai gắn cờ.
