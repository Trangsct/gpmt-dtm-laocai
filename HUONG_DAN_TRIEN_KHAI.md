# Hướng dẫn từng bước đưa trang GPMT–ĐTM vào sử dụng

Dành cho người **không chuyên kỹ thuật**. Mọi việc làm trên trình duyệt (Chrome/Edge), không phải gõ lệnh.
Tên nút trên các trang GitHub, Vercel, Neon đôi khi đổi chút ít — cứ tìm nút có nghĩa tương tự.

Ký hiệu: 🙋 **bạn làm** · 🤖 **Claude tự làm** khi bạn nhắn trong phiên làm việc.

| # | Việc | Ai làm | Mất khoảng |
|---|---|---|---|
| 1 | Tạo kho GitHub riêng tư, cấp quyền cho Claude | 🙋 | 5 phút |
| 2 | Đẩy mã lên kho, mở yêu cầu gộp (PR), gộp khi bạn đồng ý | 🤖 | — |
| 3 | Tạo dự án Vercel từ kho | 🙋 | 5 phút |
| 4 | Tạo CSDL Neon ngay trong Vercel | 🙋 | 3 phút |
| 5 | Đặt tài khoản quản trị đầu tiên (3 biến) rồi triển khai lại | 🙋 | 3 phút |
| 6 | Đăng nhập, tải sổ Excel lên | 🙋 | 2 phút |
| 7 | Cấp tài khoản cho đồng nghiệp, BQL các KCN, UBND xã | 🙋 | tùy số người |
| 8 | Rà soát 29 bản ghi gắn cờ | 🙋 (Claude hỗ trợ đọc văn bản) | vài buổi |
| 9 | Bổ sung thời hạn cho 146 GP (qua mẫu Excel) | 🙋 | theo tiến độ tìm được GP gốc |
| 10 | Nhập dữ liệu ĐTM | 🙋 | theo hồ sơ |
| 11 | Chỗ đặt PDF gốc trên mạng | 🤖 (giai đoạn 2) | — |
| 12 | Triển khai chính thức, tên miền `….laocai.gov.vn` | Sở quyết | để sau |

---

## Bước 1. Tạo kho GitHub riêng tư 🙋

1. Mở **https://github.com/new** (đăng nhập tài khoản GitHub của bạn nếu được hỏi).
2. Ô **Repository name**: gõ đúng `gpmt-dtm-laocai`.
3. Chọn **Private** (riêng tư). *Không* tích ô **Add a README file**; hai ô *.gitignore*, *license* để **None**.
4. Bấm nút xanh **Create repository**. Xong — trang hiện hướng dẫn dòng lệnh, **bỏ qua**, không cần làm gì thêm.
5. Cấp quyền cho Claude vào kho mới: mở **https://github.com/apps/claude/installations/select_target** → chọn
   tài khoản của bạn → mục **Repository access**: chọn *Only select repositories* → thêm `gpmt-dtm-laocai`
   (giữ nguyên các kho đã chọn trước) → **Save**.
   Nếu Claude báo vẫn không vào được: mở **https://claude.ai/connect-github** để kết nối lại GitHub.
6. Nhắn cho Claude: **"đã tạo kho"**.

## Bước 2. Đẩy mã lên, gộp vào nhánh chính 🤖

Claude đẩy mã lên nhánh làm việc, mở PR vào `main` và gửi bạn đường dẫn. Bạn xem, rồi:
- nhắn **"merge đi"** → Claude gộp giúp; hoặc
- tự gộp: mở đường dẫn PR → kéo xuống → **Merge pull request** → **Confirm merge**.

Vercel chỉ lấy mã ở nhánh `main`, nên phải gộp xong mới sang bước 3.

## Bước 3. Tạo dự án trên Vercel 🙋

1. Mở **https://vercel.com/signup** → chọn gói **Hobby** → **Continue with GitHub** (đăng nhập bằng GitHub,
   không phải tạo mật khẩu mới).
2. Vercel hỏi quyền đọc kho GitHub → chọn *Only select repositories* → `gpmt-dtm-laocai` → **Install**.
3. Ở trang **Import Git Repository** bấm **Import** cạnh `gpmt-dtm-laocai`.
4. Ô **Project Name**: gõ `gpmt-dtm-laocai` (Vercel báo tên đã có người dùng thì gõ `gpmt-laocai`).
   **Framework Preset**: để *Other*. Các mục khác để nguyên.
5. Bấm **Deploy**. Chờ 1–2 phút. Lần này trang chưa có CSDL nên chưa dùng được — bình thường, làm tiếp bước 4.

## Bước 4. Tạo CSDL Neon ngay trong Vercel 🙋

1. Trong dự án vừa tạo, bấm thẻ **Storage** (hàng thẻ trên cùng).
2. **Create Database** → chọn **Neon** (Serverless Postgres) → **Continue**.
3. Nếu được hỏi: chấp nhận điều khoản Neon; **Region** chọn **Singapore** (gần Việt Nam nhất); gói **Free**;
   tên CSDL để mặc định → **Create**.
4. Màn hình **Connect Project**: chọn dự án `gpmt-dtm-laocai`, tích cả 3 môi trường (Development, Preview,
   Production) → **Connect**.

Vercel tự thêm biến `DATABASE_URL` vào dự án — **bạn không phải sao chép chuỗi kết nối**. Ứng dụng tự tạo các bảng
ở lần chạy đầu. Tài khoản Neon do bạn giữ (đăng nhập qua Vercel).

## Bước 5. Đặt tài khoản quản trị đầu tiên rồi triển khai lại 🙋

1. Thẻ **Settings** → **Environment Variables**.
2. Thêm lần lượt 3 biến (mỗi biến: gõ **Key**, gõ **Value**, để tích cả 3 môi trường, bấm **Save**):

   | Key | Value |
   |---|---|
   | `QUAN_TRI_EMAIL` | email bạn dùng để đăng nhập trang |
   | `QUAN_TRI_MAT_KHAU` | mật khẩu **ít nhất 10 ký tự** (chỉ dùng cho lần đầu, sau đó đổi ngay trên trang) |
   | `QUAN_TRI_HO_TEN` | họ tên hiển thị, vd `Trần Trọng Trang` |

3. Thẻ **Deployments** → dòng trên cùng → nút **⋯** → **Redeploy** → **Redeploy**. Chờ 1–2 phút.

Ứng dụng chỉ tạo tài khoản này khi CSDL **chưa có tài khoản nào**, nên để nguyên 3 biến cũng không sao; đổi mật
khẩu trên trang thì biến cũ không còn tác dụng. Không cần đặt `SECRET_KEY` hay cấu hình HTTPS — ứng dụng tự xử lý.

## Bước 6. Đăng nhập và tải sổ Excel lên 🙋

1. Mở **https://gpmt-dtm-laocai.vercel.app** (hoặc `gpmt-laocai…` nếu đổi tên ở bước 3).
   Kiểm tra nhanh: mở `…/suc-khoe` phải thấy `{"trang_thai":"ok"}`.
2. Đăng nhập bằng email + mật khẩu ở bước 5 → bấm **Đổi mật khẩu** (góc phải trên) → đặt mật khẩu mới.
3. Menu **Nhập dữ liệu** → mục 1 → **Choose File** → chọn tệp `Danh_sach_theo_doi_cap_GPMT_hang_nam__Lao_Cai.xls`
   → **Nhập sổ**. Chờ vài giây → hiện báo cáo nhập (148 giấy phép, 29 bản ghi cần rà soát).

GP 2519/GPMT-UBND đã đối chiếu tay được nhập kèm tự động; GP 1439/GPMT-UBND tự chuyển *Hết hiệu lực — bị thay thế*.

## Bước 7. Cấp tài khoản cho người khác 🙋

Menu **Tài khoản** → **+ Cấp tài khoản** → điền họ tên, email, đơn vị → chọn vai trò:

| Người dùng | Vai trò | Ô cần điền thêm |
|---|---|---|
| Cán bộ được sửa dữ liệu | Biên tập | — |
| Lãnh đạo, cán bộ chỉ xem | Chỉ xem (trong Sở) | — |
| Ban Quản lý các KCN | Xem giới hạn | tích **Chỉ cơ sở trong KCN/CCN** |
| UBND xã/phường | Xem giới hạn | **Giới hạn theo xã/phường**: gõ tên, vd `Văn Phú` |

Bấm **Lưu** → trang hiện **mật khẩu tạm** (chỉ hiện một lần). Gửi riêng cho người đó (điện thoại/Zalo cá nhân),
dặn đổi mật khẩu ngay lần đầu. Quên mật khẩu: mở tài khoản đó → tích **Đặt lại mật khẩu** → Lưu.
Người nghỉ việc/chuyển công tác: bỏ tích **Hoạt động** (không xóa, để giữ nhật ký).

## Bước 8. Rà soát 29 bản ghi gắn cờ 🙋

Menu **Cần rà soát** → bấm số hiệu từng GP → đọc lý do màu đỏ → đối chiếu văn bản gốc (hồ sơ lưu của Sở, Cổng TTĐT
tỉnh) → **Sửa** → sửa ô tương ứng → **Lưu** → bấm **Đã rà soát xong**.

| Lý do | Cách xử lý |
|---|---|
| Ký hiệu `QĐ-UBND` / `GPTN-UBND` / `GPTNMT-UBND` chưa rõ loại văn bản (12 GP) | Xem văn bản gốc. Là GPMT → ô *Loại văn bản* chọn **GPMT**, sửa ký hiệu cho đúng văn bản. Không phải GPMT (vd QĐ phê duyệt ĐTM) → nhập sang menu **ĐTM** rồi xóa bản ghi ở GPMT (nhờ tài khoản Quản trị). |
| Trùng số 1827/GPMT-UBND ngày 16/9/2024 cho trại lợn Anifer và thủy điện Văn Chấn | Xem văn bản gốc để biết số này của cơ sở nào; sửa số/ngày của bản ghi còn lại. |
| Năm ký khác nhóm năm trong sổ (5 GP) | Xem ngày trên văn bản gốc, sửa ô *Ngày ký* nếu sổ ghi sai. |
| Chưa xác định cơ quan cấp (752, 1723, 938) | Xem người ký/cơ quan trên văn bản → ô *Cơ quan cấp*. |
| Sổ không ghi ngày ký (1869, 150/GPMT-BTNMT) / không ghi số (mỏ đá Toòng Già 2023) | Bổ sung theo văn bản gốc. Dòng Toòng Già có thể chính là GP 233/GPMT-UBND năm 2025 — nếu đúng thì xóa dòng trùng. |
| Số GP lấy từ sheet VHTN, ghép theo tên (Nậm Lúc, HTXL nước thải Tằng Loỏng) | Kiểm tra số/ngày và tên cơ sở khớp văn bản gốc. |
| Sổ ghi "cấp lại" nhưng không ghi GP cũ (BV đa khoa Bảo Thắng 1498) | Tìm GP cũ bị thay thế (có thể 617/GP-UBND) → ô *Thay thế GP* chọn GP đó → GP cũ tự chuyển *bị thay thế*. |
| Ghi chú "đã thực hiện ĐKMT" (Trung tâm đăng kiểm 861) | Xác nhận lựa chọn chuyển tiếp; nếu đúng giữ nguyên, nhập thêm ở menu **Đăng ký môi trường**. |

🤖 Có văn bản gốc (PDF) thì gửi cho Claude trong phiên làm việc: Claude đọc số, ngày, cơ quan cấp, thời hạn và
nói bạn cần sửa ô nào (PDF ký số được đọc trên ảnh, không dựa vào chữ copy ra).

## Bước 9. Bổ sung thời hạn cho 146 GP 🙋

Sổ theo dõi không ghi thời hạn nên 146 GP đang *Chưa xác định* → cảnh báo sắp hết hạn chưa chạy được.

1. Menu **Nhập dữ liệu** → mục 2 → **Tải mẫu (chỉ GP còn thiếu)** → mở tệp bằng Excel.
2. Với mỗi GP: mở văn bản gốc, đọc **Điều 3 "Thời hạn của Giấy phép"** → gõ số năm vào **ô vàng** cột *Thời hạn*
   (vd `10`). GP thiếu ngày ký thì gõ ngày vào ô vàng cột *Ngày ký* dạng `22/07/2026`. Không chắc → để trống.
3. **Lưu** tệp → quay lại trang → **Tải lên mẫu bổ sung**. Trang hiện báo cáo: GP nào đã cập nhật, dòng nào lỗi.

Làm nhiều lần được, mỗi lần một ít. Ô trống giữ nguyên dữ liệu cũ; mọi thay đổi ghi vào nhật ký.
Giai đoạn 2 sẽ có chức năng tải PDF lên để máy đọc Điều 3 tự động.

## Bước 10. Nhập dữ liệu ĐTM 🙋

Sổ Excel chưa có ĐTM. Menu **ĐTM** → **+ Thêm mới** → chọn cơ sở, số và ngày QĐ phê duyệt, cơ quan phê duyệt,
QĐ thành lập hội đồng → **Lưu**. Cơ sở chưa có trong hệ thống: menu **Cơ sở / dự án** → **+ Thêm cơ sở** trước.
Nhiều QĐ cùng lúc: gửi danh sách (Excel) hoặc các PDF cho Claude để lập bảng nhập hàng loạt 🤖.

## Bước 11. Chỗ đặt PDF gốc 🤖

Trên Vercel, nút **Mở PDF gốc** chưa hoạt động vì máy chủ Vercel không giữ tệp. Giai đoạn 2 sẽ thêm chức năng
tải PDF lên và lưu vào kho tệp riêng tư (Vercel Blob hoặc kho GitHub riêng) — Claude làm khi bạn duyệt giai đoạn 2.

## Bước 12. Triển khai chính thức (để sau, không chặn việc dùng thử)

Khi Sở quyết định dùng lâu dài:
- **Nơi chạy**: máy chủ của Sở hoặc đám mây Sở thuê. Mã nguồn không phải sửa — chỉ đặt lại các biến môi trường.
- **Tên miền**: Sở gửi văn bản đề nghị đơn vị quản lý tên miền của tỉnh cấp tên miền con (vd `gpmt.….laocai.gov.vn`)
  và trỏ về nơi chạy. Không tự mua tên miền `.vn`/`.com` khi chưa có ý kiến của Sở. 🤖 Claude soạn giúp dự thảo
  văn bản đề nghị khi cần.

---

### Khi gặp sự cố

| Hiện tượng | Xử lý |
|---|---|
| Trang báo lỗi 500 ngay khi mở | Vercel → **Storage**: kiểm tra CSDL Neon đã **Connect** vào dự án chưa; rồi **Redeploy**. |
| Không đăng nhập được lần đầu | Kiểm tra 3 biến ở bước 5 (mật khẩu ≥ 10 ký tự) → **Redeploy**. |
| Quên mật khẩu quản trị | Nhờ một quản trị khác đặt lại; nếu chỉ có một quản trị, nhắn Claude để được hướng dẫn. |
| Nhập sổ báo "đã có dữ liệu" | Đúng thiết kế (tránh nhập trùng). Muốn nhập lại: mục 3 trang **Nhập dữ liệu**. |
| Neon báo CSDL "tạm dừng" | Gói miễn phí tự nghỉ khi lâu không dùng và tự thức dậy ở lần truy cập sau (chờ vài giây). |
