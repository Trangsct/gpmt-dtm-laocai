# GIAO VIỆC: XÂY DỰNG TRANG WEB QUẢN LÝ GIẤY PHÉP MÔI TRƯỜNG (GPMT) VÀ BÁO CÁO ĐTM
## Đơn vị sử dụng: Sở Nông nghiệp và Môi trường tỉnh Lào Cai

> **Cách dùng:** dán toàn bộ bài này vào phiên chat mới với Claude Code và **đính kèm 2 tệp**:
> 1. `Danh_sach_theo_doi_cap_GPMT_hang_nam__Lao_Cai.xls`: sổ theo dõi GPMT hằng năm;
> 2. `GPMT_NMSX_cac_san_pham_nhom_va_SP_nhua_...pdf`: một GPMT mẫu (số 2519/GPMT-UBND ngày 22/7/2026).
>
> **Kho GitHub:** dự án làm trong kho **riêng tư** `gpmt-dtm-laocai` (kho tạm trên tài khoản người giao việc; sau này
> chuyển sang tài khoản của Sở, không phải sửa code). Nếu phiên chưa có kho này: thử tạo kho riêng tư bằng công cụ
> GitHub; không có quyền tạo thì hướng dẫn người giao việc tạo trên github.com (Private, không tích "Add README")
> rồi gắn kho vào phiên (`add_repo`), sau đó mới làm tiếp.
>
> **Việc đầu tiên trong kho:** lưu 2 tệp đính kèm vào `du-lieu-goc/So_theo_doi_cap_GPMT_hang_nam_Lao_Cai.xls` và
> `du-lieu-goc/2519_GPMT-UBND.pdf`, lưu bài này thành `HUONG_DAN.md`, tạo `README.md` + `CLAUDE.md`, commit, push.
>
> Dự án đứng độc lập: **không** dùng chung, **không** liên kết, **không** chép dữ liệu hay mã từ kho nào khác.
> Giao tiếp, giao diện, comment và commit message viết bằng **tiếng Việt**.

---

## 1. Mục tiêu

Xây ứng dụng web nội bộ cho Sở Nông nghiệp và Môi trường (Sở NN&MT) để:

1. **Lưu và tra cứu toàn bộ GPMT** trên địa bàn tỉnh Lào Cai (tỉnh mới, gồm cả địa bàn Yên Bái cũ), gồm GP do
   UBND tỉnh cấp, do UBND tỉnh Yên Bái cũ cấp, do UBND cấp huyện cũ cấp và do Bộ (TN&MT trước đây, NN&MT hiện nay)
   cấp cho cơ sở nằm trên địa bàn.
2. **Lưu và tra cứu các quyết định phê duyệt kết quả thẩm định báo cáo ĐTM**, liên kết với GPMT của cùng dự án.
3. **Theo dõi hồ sơ đang giải quyết**: tiếp nhận hồ sơ → đoàn kiểm tra hoặc hội đồng thẩm định → chủ cơ sở chỉnh sửa,
   bổ sung → tờ trình của Sở → GP hoặc QĐ được ký.
4. **Theo dõi vòng đời GP**: cấp mới → cấp điều chỉnh → cấp lại (GP cũ hết hiệu lực) → hết hạn. Theo dõi vận hành
   thử nghiệm (VHTN) và báo cáo công tác BVMT định kỳ.
5. **Cảnh báo**: GPMT sắp hết hạn, VHTN quá hạn, GP đã bị thay thế, dữ liệu còn thiếu.
6. **Thống kê và xuất báo cáo** theo năm, cơ quan cấp, loại hình sản xuất, xã/phường, KCN/CCN; xuất lại bảng theo
   mẫu "Phụ lục 6.4" như sổ Excel đang dùng.

## 2. Khung pháp lý chi phối thiết kế dữ liệu

Phần này chỉ tóm tắt để thiết kế dữ liệu. Khi áp dụng vào nghiệp vụ phải đối chiếu văn bản gốc hoặc văn bản hợp
nhất, và **không cứng hóa quy định vào code**: căn cứ pháp lý thay đổi liên tục.

- **Chuỗi văn bản** (theo phần căn cứ của GPMT mẫu):
  - Luật Bảo vệ môi trường 72/2020/QH14, sửa đổi bởi Luật 146/2025/QH15 (hiệu lực 01/01/2026).
  - NĐ 08/2022/NĐ-CP, sửa đổi bởi NĐ 05/2025/NĐ-CP và NĐ 48/2026/NĐ-CP ngày 29/01/2026.
  - TT 02/2022/TT-BTNMT, sửa đổi bởi TT 07/2025/TT-BTNMT, TT 07/2025/TT-BNNMT và TT 09/2026/TT-BNNMT.
- **Nhóm dự án I / II / III / IV**. GPMT áp dụng cho nhóm I, II, III có phát sinh nước thải, bụi, khí thải phải xử lý
  (hoặc nhập khẩu phế liệu, xử lý CTNH). Nhóm IV không thuộc đối tượng GPMT.
- **ĐTM** áp dụng cho nhóm I và một phần nhóm II. Một dự án có thể **vừa** phải ĐTM **vừa** phải GPMT, và ĐTM không
  thay được GPMT. Vì vậy phải có hai bảng riêng, liên kết với nhau qua dự án/cơ sở.
- **Thẩm quyền cấp GPMT** hiện nay: Bộ NN&MT, UBND/Chủ tịch UBND cấp tỉnh. Cấp huyện không còn; cấp xã chỉ tiếp nhận
  **đăng ký môi trường**. Danh mục cơ quan cấp vẫn phải giữ cả cơ quan cũ (UBND tỉnh Yên Bái, UBND huyện cũ,
  Bộ TN&MT) để lưu lịch sử.
- **Cấp điều chỉnh / cấp lại**: GP mới ghi rõ GP cũ hết hiệu lực. Ví dụ 2519/GPMT-UBND ngày 22/7/2026 của UBND tỉnh
  Lào Cai thay 1439/GPMT-UBND ngày 22/8/2022 của UBND tỉnh Yên Bái. Cần quan hệ "thay thế" giữa hai bản ghi.
- **Thời hạn** ghi tại Điều 3 của GP, tính **từ ngày ký** (GP mẫu: 10 năm). Ngày hết hạn = ngày ký + thời hạn đọc từ
  chính GP. Không đọc được thì để trống và gắn cờ "cần nhập tay"; **không tự suy ra thời hạn từ nhóm dự án**.
- **VHTN** kéo dài không quá 06 tháng, được gia hạn một lần không quá 06 tháng. Một số công trình không phải VHTN
  (nước thải đấu nối vào hệ thống xử lý tập trung; công trình xử lý bụi, khí thải công suất dưới 5.000 m³/giờ).
- **Chuyển tiếp theo NĐ 48/2026**: cơ sở đã có GPMT nhưng theo quy định mới không còn thuộc đối tượng GPMT được chọn
  dùng tiếp GP đến hết hạn hoặc chuyển sang đăng ký môi trường. Cần trường ghi lựa chọn này.
- Tên "Bộ/Sở Tài nguyên và Môi trường" là tên **cũ**; nay là Bộ/Sở Nông nghiệp và Môi trường.

## 3. Dữ liệu đầu vào

### 3.1. Sổ theo dõi `Danh_sach_theo_doi_cap_GPMT_hang_nam__Lao_Cai.xls`

Tệp Excel 97, đọc bằng `xlrd`.

| Sheet | Nội dung | Số dòng dữ liệu |
|---|---|---|
| `GPMT Tinh cap` | "Phụ lục 6.4. Tổng hợp GPMT do UBND tỉnh cấp hoặc ủy quyền cấp" (Lào Cai cũ) | 80 (2022: 3; 2023: 37; 2024: 26; 2025: 14) |
| `GPMT tỉnh YB cũ` | GPMT của tỉnh Yên Bái cũ và vài GP do Bộ cấp | 61 (2022: 10; 2023: 23; 2024: 16; 2025: 12) |
| `GPMT cấp huyện cũ` | GPMT cấp huyện cũ | 1 (các dòng còn lại trống) |
| `VHTN` | Danh sách cơ sở, GP và tình trạng vận hành thử nghiệm | 144 (phần lớn cột VHTN còn trống) |

Cột chung của 3 sheet GPMT: `TT | Tên cơ sở (/Chủ cơ sở) | Địa chỉ | Loại hình sản xuất | Giấy phép số | Công suất |
Nước thải (m3/ngày đêm) | Khí thải (m3/giờ) | CTR thông thường (kg/năm) | CTNH (kg/năm)`. Sheet YB cũ có thêm
`Ghi chú | Báo cáo việc chấp hành`; sheet huyện có thêm `VHTN`. Tiêu đề chiếm 3 dòng và có ô gộp.

**Các chỗ ghi lộn xộn đã thấy. Script nhập phải xử lý và không được bỏ qua lặng lẽ:**

- **Dòng nhóm năm xen giữa dữ liệu:** `I | 2022`, `II | 2023`, `II | 2024` (số La Mã lặp), `III | Năm 2025`.
  Lấy năm từ các dòng này.
- **Cột "Giấy phép số" gộp cả số lẫn ngày, không theo một kiểu:**
  - `2074/GPMT-UBND 20/09/2022`, `ngày18/07/2022`, `123/GP-UBND ngày 16/01/2023`;
  - có dòng chứa **2 giấy phép**: `2568/GPMT-UBND ngày 27/12/2022, cấp điều chỉnh GPMT số 1827/GPMT-UBND ngày 16/9/2024`;
  - có dòng **thiếu ngày**: `150/GPMT-BTNMT`.
- **Ký hiệu không đồng nhất:** `GPMT-UBND`, `GP-UBND`, `QĐ-UBND` (9 dòng), `GPTN-UBND`, `GPTNMT-UBND`,
  `GPMT-BTNMT`, `GPMT-BNNMT`, và lỗi gõ `GPMT-UNMD`. Các dòng `QĐ-UBND` và `GPTN` **chưa rõ là loại văn bản gì**:
  nhập với cờ `can_ra_soat = true` và liệt kê cho người phụ trách xác nhận, không tự đoán.
- **Cột chất thải lẫn chữ và đơn vị:** `126 m3/ngày đêm`, `NTSH: 09`, `Tuần hoàn`, `1.949 tấn/năm`,
  `15.000m3/năm Đất đá thải; 10 kg/năm CTRSH`, `3074,5m3/năm`. Dấu chấm và phẩy theo kiểu Việt (`1.949` là một
  nghìn chín trăm bốn mươi chín). Lưu thành **hai loại trường**:
  - `*_goc`: nguyên văn như trong sổ;
  - `*_so` và `*_don_vi`: đã chuẩn hóa, chỉ điền khi chắc chắn.
- **Sheet `VHTN`:**
  - cột STT có ký tự `\xa0`;
  - tên cơ sở và chủ cơ sở nằm ở hai cột riêng (khác 3 sheet kia);
  - địa chỉ đã theo **xã/phường mới**, dùng để cập nhật địa chỉ hành chính mới cho bản ghi GPMT.
- **Một cơ sở xuất hiện ở nhiều sheet:** ghép theo **số GP** trước, theo tên cơ sở sau (so khớp gần đúng, có bước
  duyệt tay).

### 3.2. GPMT mẫu (PDF 19 trang, ký số)

⚠ **Số và ngày được điền qua trường ký số.** Lớp chữ trả về "2519" và "22" ở cuối trang 1, còn dòng
"Số: /GPMT-UBND" thì để trống. Muốn biết số và ngày phải:

- lấy theo tọa độ trên trang 1 (dòng "Số:", y≈96–109), hoặc
- render trang thành ảnh để đọc (PyMuPDF hoặc `pdftoppm`).

Không được kết luận "chưa có số" chỉ vì lớp chữ để trống. Các phụ lục ghi `/GP-UBND` trong khi trang bìa ghi
`/GPMT-UBND`: lấy ký hiệu theo **trang bìa**.

Cấu trúc cố định của GPMT, dùng để viết bộ đọc tự động:

- **Trang 1:**
  - các căn cứ;
  - QĐ thành lập đoàn kiểm tra của Sở NN&MT (mẫu: 293/QĐ-SNNMT ngày 20/04/2026);
  - văn bản đề nghị và văn bản bổ sung hồ sơ của chủ cơ sở;
  - tờ trình của Sở (mẫu: 573/TTr-SNNMT ngày 07/7/2026).
- **Điều 1:**
  - mục 1 "Thông tin chung": 1.1 tên cơ sở; 1.2 địa điểm; 1.3 GCN đăng ký doanh nghiệp; 1.4 mã số thuế;
    1.5 loại hình; 1.6 phạm vi, quy mô (diện tích đất, nhóm theo đầu tư công, **nhóm I/II/III theo Luật BVMT**,
    công suất từng dây chuyền);
  - mục 2: nội dung cấp phép, chi tiết ở 5 phụ lục;
  - mục 3: phân loại xanh.
- **Điều 2:** quyền và nghĩa vụ.
- **Điều 3:** **thời hạn**. Câu "Giấy phép môi trường số … hết hiệu lực kể từ …" cho biết quan hệ thay thế.
- **Điều 4:** giao kiểm tra. Sau đó là Nơi nhận và người ký (KT. CHỦ TỊCH …).
- **Phụ lục 1 (nước thải):**
  - nguồn phát sinh, dòng xả;
  - **lưu lượng xả lớn nhất** (mẫu: 9 m³/ngày đêm);
  - quy chuẩn (QCVN 14:2025/BTNMT …);
  - tọa độ điểm xả VN-2000;
  - công trình xử lý (mẫu: 15 m³/ngày đêm);
  - kế hoạch VHTN.
- **Phụ lục 2 (khí thải):**
  - từng dòng khí thải;
  - **lưu lượng xả lớn nhất** (mẫu: 127.000 m³/giờ);
  - quy chuẩn QCVN 19:2024/BTNMT;
  - tọa độ;
  - công trình xử lý;
  - kế hoạch VHTN.
- **Phụ lục 3:** tiếng ồn, độ rung.
- **Phụ lục 4 (chất thải):**
  - CTNH (mẫu: 4.680 kg/năm);
  - CTR công nghiệp thông thường (7,8 tấn/năm);
  - CTR sinh hoạt (~18 tấn/năm);
  - phòng ngừa, ứng phó sự cố.
- **Phụ lục 5:** cải tạo phục hồi môi trường, bồi hoàn đa dạng sinh học, các yêu cầu khác.

Bản ghi mẫu dùng làm **ca kiểm thử đầu tiên** (số và ngày đã đối chiếu với ảnh trang 1):

```
so_hieu: 2519/GPMT-UBND | ngay_ky: 2026-07-22 | co_quan_cap: UBND tỉnh Lào Cai | nguoi_ky: KT. Chủ tịch – PCT Phan Trung Bá
loai_cap: cấp lại | thay_the: 1439/GPMT-UBND ngày 22/8/2022 (UBND tỉnh Yên Bái) | thoi_han: 10 năm
chu_co_so: Công ty CP đầu tư và phát triển nhựa gỗ Châu Âu | MST: 0107094917
co_so: Nhà máy sản xuất các sản phẩm nhôm và các sản phẩm nhựa Eurostark
dia_diem: Lô CN-24, KCN phía Nam, phường Văn Phú, tỉnh Lào Cai | dien_tich: 48.113,5 m2 | nhom: II
cong_suat: tấm nhựa gỗ 300.000 m2/năm; compound nhựa gỗ 20.000 tấn/năm; nguyên liệu nhôm 60.000 tấn/năm
qd_doan_kiem_tra: 293/QĐ-SNNMT ngày 20/04/2026 | to_trinh: 573/TTr-SNNMT ngày 07/7/2026
```

Bản ghi 1439/GPMT-UBND đã có trong sheet `GPMT tỉnh YB cũ`. Sau khi nhập PDF, bản ghi đó phải tự chuyển sang
"Hết hiệu lực — bị thay thế bởi 2519/GPMT-UBND". Đây là một tiêu chí nghiệm thu.

### 3.3. Dữ liệu còn thiếu

- Sổ Excel mới chỉ có GPMT. **Chưa có dữ liệu ĐTM.**
- Dữ liệu ĐTM và các GPMT còn thiếu lấy từ hồ sơ lưu của Sở và từ trang công khai GPMT/ĐTM trên Cổng Thông tin điện
  tử tỉnh. Người phụ trách tải lên hoặc nhập tay.
- Ứng dụng cần một **chức năng tải PDF lên → đọc tự động → người duyệt xác nhận** (xem mục 5).
- Không bịa số, ngày; PDF ký số phải đọc theo cách ở mục 3.2.

## 4. Mô hình dữ liệu đề xuất

```
chu_the         (id, ten, ma_so_thue, dia_chi_tru_so, loai: doanh nghiệp/ban QLDA/đơn vị sự nghiệp…)
co_so_du_an     (id, ten, chu_the_id, dia_diem, xa_phuong_moi, dia_ban_cu (LC/YB), kcn_ccn, loai_hinh,
                 nhom_du_an I/II/III, dien_tich, cong_suat_goc, toa_do_lat/lng (tùy chọn), ghi_chu)
ho_so           (id, co_so_du_an_id, loai: GPMT mới/điều chỉnh/cấp lại/ĐTM, van_ban_de_nghi, ngay_tiep_nhan,
                 qd_doan_kiem_tra_hoac_hoi_dong, van_ban_bo_sung, to_trinh, trang_thai, can_bo_thu_ly,
                 ket_qua_id)                                    -- hồ sơ đang giải quyết
gpmt            (id, so_hieu, so, ky_hieu, ngay_ky, co_quan_cap, nguoi_ky, loai_cap: mới/điều chỉnh/cấp lại,
                 co_so_du_an_id, thoi_han_nam, ngay_het_han, thay_the_gpmt_id, trang_thai (tính tự động),
                 lua_chon_chuyen_tiep (dùng tiếp GP / chuyển ĐKMT), nguon_du_lieu: excel-sheet-dòng / pdf / nhập tay,
                 can_ra_soat, ghi_chu_goc, tep_pdf)
gpmt_xa_thai    (gpmt_id, loai: nước thải/khí thải/ồn-rung, ten_dong, luu_luong_max, don_vi, quy_chuan,
                 nguon_tiep_nhan, toa_do_vn2000, cong_trinh_xu_ly)
gpmt_chat_thai  (gpmt_id, loai: CTNH/CTRCNTT/CTRSH/khác, khoi_luong_goc, khoi_luong_kg_nam)
vhtn            (gpmt_id, cong_trinh, bat_dau, ket_thuc_du_kien, gia_han_den, trang_thai:
                 chưa/đang/đã xong/không phải VHTN, van_ban_thong_bao, ghi_chu_goc)
dtm             (id, so_qd, ngay_qd, co_quan_phe_duyet, co_so_du_an_id, nhom_du_an, qd_thanh_lap_hoi_dong,
                 tep_pdf, can_ra_soat)
bao_cao_bvmt    (co_so_du_an_id, nam, da_nop, ngay_nop, ghi_chu)          -- giai đoạn 2
kiem_tra        (co_so_du_an_id, ngay, co_quan, ket_luan, van_ban)        -- giai đoạn 2
tai_khoan       (id, ho_ten, email, vai_tro: quản trị/biên tập/chỉ xem)
nhat_ky         (tai_khoan_id, thoi_diem, bang, ban_ghi, thay_doi)        -- lưu vết mọi lần sửa
```

Trạng thái GPMT tính tự động, gồm một trong các giá trị sau:

- *Còn hiệu lực*
- *Sắp hết hạn* (≤ 12 tháng)
- *Hết hạn*
- *Hết hiệu lực — bị thay thế*
- *Chưa xác định* (thiếu ngày hoặc thời hạn)

## 5. Chức năng

**Giai đoạn 1 (MVP): làm trước, nghiệm thu xong mới sang giai đoạn 2**

1. **Nhập sổ Excel vào CSDL**, kèm **báo cáo nhập**: bao nhiêu dòng đã vào, bao nhiêu dòng bị gắn cờ `can_ra_soat` và
   lý do.
2. **Danh sách GPMT:**
   - tìm theo số hiệu, tên cơ sở, chủ cơ sở, mã số thuế;
   - lọc theo năm, cơ quan cấp, địa bàn cũ (LC/YB), xã/phường, loại hình, nhóm, trạng thái.
3. **Trang chi tiết GPMT:** thông tin chung, xả thải, chất thải, VHTN, chuỗi thay thế (GP trước ↔ GP sau), nút mở
   PDF gốc.
4. **Trang chi tiết cơ sở/dự án:** gom mọi hồ sơ, GPMT, ĐTM, VHTN của cơ sở theo dòng thời gian.
5. **Bảng điều khiển:**
   - số GP theo năm và theo cơ quan cấp;
   - GP sắp hết hạn;
   - VHTN quá hạn;
   - hồ sơ đang giải quyết;
   - danh sách dòng "cần rà soát".
6. **Nhập và sửa tay qua biểu mẫu:** phải đăng nhập, phân quyền theo vai trò, mọi thay đổi ghi vào `nhat_ky`.
7. **Xuất Excel** theo mẫu "Phụ lục 6.4".

**Giai đoạn 2**

8. **Tải PDF GPMT/QĐ ĐTM lên, đọc tự động** (PyMuPDF), điền sẵn biểu mẫu để cán bộ duyệt.
   **Chưa duyệt thì không tự lưu.** Ca thử là GP 2519.
9. **Module ĐTM** đầy đủ, kèm theo dõi hội đồng thẩm định.
10. **Bản đồ cơ sở** (Leaflet), hiển thị theo tọa độ điểm xả hoặc tọa độ cơ sở.
11. **Theo dõi báo cáo công tác BVMT định kỳ** và kết quả kiểm tra.

## 6. Kiến trúc kỹ thuật (đã chốt, trừ chỗ ghi "hỏi")

- **Mã nguồn:** Python **Flask + SQLAlchemy + Jinja2**; giao diện HTML/CSS theo phong cách hành chính; không cần
  bundler.
- **CSDL:** chạy thử cục bộ bằng SQLite; bản chạy thật dùng **PostgreSQL**, vì cần sửa trên web và giữ dữ liệu lâu
  dài. Lưu ý: nền tảng serverless (Vercel…) không giữ được tệp SQLite ghi lúc chạy.
- **Tệp PDF:** đặt tên theo số hiệu, ví dụ `2519_GPMT-UBND.pdf`.
  - Trùng số giữa các năm: thêm hậu tố năm (`1439_GPMT-UBND_2022.pdf`).
  - Phụ lục: hậu tố `_2`, `_3`.
  - Kiểm MD5 để tránh lưu trùng.
- **Nơi triển khai và tên miền:** hai giai đoạn.
  - *Chạy thử (đã chốt):* **Vercel**, địa chỉ **`https://gpmt-dtm-laocai.vercel.app`** (tên dự án Vercel = tên miền
    con; nếu tên đã có người dùng thì lấy `gpmt-laocai`). Vercel chạy Flask dạng serverless (`vercel.json` +
    `@vercel/python`), hệ tệp chỉ đọc → CSDL phải là **PostgreSQL gói miễn phí** (Neon hoặc Supabase, hỏi ở mục 9),
    chuỗi kết nối để ở biến môi trường `DATABASE_URL` của Vercel. Tệp PDF lưu ở kho GitHub riêng tư hoặc dịch vụ
    lưu tệp, không lưu vào thư mục của ứng dụng.
  - *Chính thức (Sở quyết, hỏi ở mục 9):* máy chủ của Sở hoặc đám mây; tên miền con thuộc tên miền của tỉnh
    (`….laocai.gov.vn`), do Sở đề nghị đơn vị quản lý tên miền của tỉnh cấp và trỏ DNS về nơi triển khai. Không tự
    mua tên miền `.vn`/`.com` cho hệ thống của cơ quan nhà nước khi chưa có ý kiến của Sở.
  - Mã nguồn không gắn cứng tên miền hay nơi triển khai: đọc từ biến môi trường, đổi chỗ chạy không phải sửa code.
- **Kiểm thử:** có thư mục `tests/`, tối thiểu các ca sau:
  - tách số/ngày GP từ các chuỗi lộn xộn ở mục 3.1;
  - bản ghi 2519 làm 1439 chuyển sang "bị thay thế";
  - tính ngày hết hạn;
  - đọc số kiểu Việt (`1.949` = 1949, `3074,5` = 3074.5).
- **Tài liệu:** kho mới có `README.md` (cách chạy cục bộ, cách nhập dữ liệu, cách triển khai) và `CLAUDE.md`
  (quy ước cho các phiên làm việc sau).

## 7. Bảo mật

- Kho mã nguồn và nơi lưu tệp đặt **riêng tư**. Không đẩy sổ theo dõi, CSDL, PDF lên bất kỳ nơi công khai nào.
- Không đưa vào kho: mật khẩu, khóa bí mật, chuỗi kết nối CSDL, email cá nhân. Các thông tin này để trong biến môi
  trường.
- Ứng dụng có đăng nhập. Mặc định chỉ được xem; quyền sửa cấp cho tài khoản được chỉ định.
- GPMT được công khai trên Cổng TTĐT tỉnh (có trong phần "Nơi nhận"), nhưng sổ theo dõi, tình trạng hồ sơ đang giải
  quyết và ghi chú là thông tin nội bộ. Nếu sau này mở trang tra cứu công khai thì chỉ xuất các trường đã công khai.

## 8. Nguyên tắc làm việc

1. **Không bịa số, ngày, tên.** Đọc được gì ghi nấy; không chắc thì gắn cờ `can_ra_soat` và liệt kê ra.
2. Việc làm được ngay thì làm ngay; chỉ hỏi ở những điểm thật sự cần quyết (mục 9).
3. Làm theo giai đoạn. Xong giai đoạn 1 thì chạy thử, gửi ảnh chụp màn hình và báo cáo nhập dữ liệu, chờ duyệt rồi
   mới sang giai đoạn 2.
4. Commit bằng tiếng Việt, ghi rõ lý do. Làm trên nhánh làm việc, mở PR vào `main` và **hỏi người giao việc trước
   khi merge**.
5. Báo cáo cuối phiên gồm: đã làm gì, đường dẫn chạy thử, danh sách dòng dữ liệu cần rà, việc còn treo.

## 9. Các điểm cần hỏi chốt ở đầu phiên (hỏi gộp một lần)

1. **Kho GitHub:** kho riêng tư `gpmt-dtm-laocai` đã có trong phiên chưa; chưa có thì xử lý theo phần "Kho GitHub"
   ở đầu bài.
2. **Người dùng:** phòng nào của Sở dùng, ai được sửa, có chia sẻ cho Ban Quản lý các KCN hoặc UBND xã không.
3. **CSDL:** dùng Neon hay Supabase (gói miễn phí) cho bản chạy thử trên Vercel; ai giữ tài khoản và biến môi trường
   `DATABASE_URL`.
4. **Các dòng ký hiệu `QĐ-UBND`, `GPTN-UBND`, `GPTNMT-UBND`** trong sổ Excel là loại văn bản gì, có đưa vào danh sách
   GPMT không.
5. **Phạm vi:** chỉ GPMT và ĐTM, hay quản lý thêm cả **đăng ký môi trường** (do UBND cấp xã tiếp nhận).
6. **Triển khai chính thức:** máy chủ của Sở hay đám mây; bao giờ xin tên miền con `laocai.gov.vn` (có thể để sau,
   không chặn giai đoạn 1).
