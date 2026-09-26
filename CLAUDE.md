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
- **27/9/2026 — Tab "Thủ tục hành chính"** (`/thu-tuc-hanh-chinh`, công khai): QĐ 463/QĐ-UBND ngày 13/02/2026
  (công bố danh mục TTHC) và QĐ 736/QĐ-UBND ngày 19/3/2026 (quy trình nội bộ). Nội dung ở `gpmt/cong_bo.json`,
  PDF gốc (giữ nguyên chữ ký số, không nén) ở `public/cong-bo/`. Theo Sở: TTHC số 1, 2, 5 đã bỏ theo QĐ ngày
  26/6/2026 — **chưa có số hiệu/toàn văn**, khi có thì cập nhật. Thêm văn bản mới: thêm PDF + một mục JSON.
- **27/9/2026 — Nguồn Data360X** (Bạn yêu cầu): GPMT, ĐTM và hồ sơ đang giải quyết lấy từ văn bản đến Sở NN&MT gửi
  Sở Công Thương, qua bot Data360X (skill `data360x-sct-vn` ở kho skill-sct: tra `theo-doi/danh-muc-2026.json`
  của kho vlncn-laocai trước, thiếu bản gốc thì gọi workflow `lay-van-ban.yml`). Kết quả viết thành JSON trong
  `gpmt/ban_ghi_doi_chieu/` (`"loai": "gpmt"` hoặc `"ho_so"`, nhiều bản ghi: `{"ban_ghi": [...]}`); ứng dụng tự
  nạp bản ghi CHƯA CÓ mỗi lần khởi động (`dong_bo_ban_ghi_moi`), không ghi đè chỉnh sửa trên web. Mới có mục lục
  (chưa bản gốc) thì gắn `ly_do_ra_soat`. Số/ngày lấy từ mục lục/đầu tệp `.md`, không từ lớp chữ PDF.
- **27/9/2026 — Trang chủ giới thiệu, quảng bá Sở** (`/`, `trang_chu.html`; thống kê chuyển sang `/thong-ke`):
  số liệu lấy trực tiếp từ CSDL; quy trình 5 chặng tóm tắt QĐ 736/QĐ-UBND; nơi nộp hồ sơ theo QĐ 463/QĐ-UBND.
  Thông tin liên hệ của Sở ở `gpmt/gioi_thieu.json` — chép nguyên văn chân trang Cổng TTĐT snnmt.laocai.gov.vn
  (ảnh Bạn gửi 27/9/2026; máy phiên không truy cập được trang đó). Chỉ sửa khi có nguồn chính thức.
- **27/9/2026 — Giao diện "khoa học kỹ thuật"** (Bạn chốt, tham khảo vlncn-laocai.vercel.app; thay cho chế độ
  trình chiếu hội nghị — đã BỎ nút Cỡ chữ A/A+/A++ và nút Toàn màn hình vì "không phù hợp"): menu dọc bên trái
  (`base.html`, nhóm Tổng quan / Tra cứu / Nghiệp vụ / Quản trị; trên điện thoại thu vào nút ☰), thanh trên có ô tra
  cứu nhanh, thẻ trắng bo góc, ô biểu tượng màu nhạt, số liệu lớn. Biểu tượng nét vẽ tay ở `_bieu_tuong.html`
  (macro `bt`), không tải thư viện ngoài. Trang chủ: băng đầu + ô tra cứu, 5 thẻ số liệu, GP cấp gần đây, biểu đồ
  theo năm + thanh tình trạng hiệu lực, quy trình 5 chặng, giới thiệu Sở + liên hệ. Cán bộ đăng nhập thấy thêm
  khối **"Việc cần làm"** tính từ CSDL (nhập sổ, rà soát, bổ sung thời hạn, cấp tài khoản, hồ sơ tồn, GP sắp hết
  hạn). Kiểm ảnh ở 1366×768 và 390px. Biểu trưng `static/logo.svg` là hình chung, không phải logo chính thức.
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
