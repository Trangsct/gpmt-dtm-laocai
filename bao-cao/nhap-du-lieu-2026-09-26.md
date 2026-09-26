# Báo cáo nhập sổ theo dõi GPMT — 26/09/2026

Tệp nguồn: `So_theo_doi_cap_GPMT_hang_nam_Lao_Cai.xls`

## 1. Số dòng đã đọc

| Sheet | Dòng dữ liệu | Theo nhóm năm của sổ |
|---|---:|---|
| GPMT Tinh cap | 80 | 2022: 3, 2023: 37, 2024: 26, 2025: 14 |
| GPMT tỉnh YB cũ | 66 | 2022: 10, 2023: 26, 2024: 18, 2025: 12 |
| GPMT cấp huyện cũ | 1 | không có nhóm: 1 |
| VHTN | 144 |  |

Trong đó **5 dòng không có số TT** nhưng có đủ dữ liệu, vẫn nhập (vì vậy số dòng đọc được có thể lớn hơn số TT cuối cùng của sheet):

- GPMT tỉnh YB cũ, dòng 25: Nhà máy chế biến đá vôi của Công ty Liên doanh canxi cacbonat YBB
- GPMT tỉnh YB cũ, dòng 40: Trang trại chăn nuôi lợn sinh sản chất lượng cao, xã Nghĩa Lộ, thị xã Nghĩa Lộ của Công ty
- GPMT tỉnh YB cũ, dòng 41: Trang trại chăn nuôi lợn sinh sản chất lượng cao tại thị trấn nông trường Trần Phú, huyện 
- GPMT tỉnh YB cũ, dòng 45: Dự án đầu tư Nhà máy chế biến dăm gỗ và viên nén gỗ của Công ty TNHH gỗ Kiệt Lâm YB
- GPMT tỉnh YB cũ, dòng 60: Cơ sở sản xuất giấy đế tại thôn Cửa Hốc, xã An Lạc, huyện Lục Yên, tỉnh Yên Bái của Công t

## 2. Kết quả trong CSDL

- Bản ghi GPMT: **147**
- Cơ sở/dự án: 146; chủ cơ sở: 127
- Bản ghi VHTN có nội dung: 15
- Dòng sheet VHTN ghép vào GPMT: theo số hiệu: 142, theo tên (sổ chính không ghi số): 2, tạo mới (chỉ có trong sheet VHTN): 1
- Dòng trùng đã gộp: 2

## 3. Bản ghi gắn cờ `can_ra_soat`: 29

### Nhóm lý do

| Lý do | Số bản ghi |
|---|---:|
| Ký hiệu … chưa rõ là loại văn bản gì … — cần xác nhận | 12 |
| Năm ký … khác nhóm năm của sổ … — kiểm tra lại ngày ký | 5 |
| Sổ không ghi ngày ký — cần bổ sung | 2 |
| Số GP lấy từ sheet VHTN dòng …, ghép với sổ chính theo tên gần đúng — cần duyệt | 2 |
| Ô … chứa … giấy phép — đã tách thành … bản ghi, cần xác nhận | 2 |
| Trùng số hiệu và ngày ký với bản ghi khác nhưng khác cơ sở … — cần đối chiếu bản gốc | 2 |
| Sổ không ghi số giấy phép | 1 |
| Ô nước thải ghi … — nghi nhập nhầm năm vào cột số liệu | 1 |
| Sổ ghi … nhưng không ghi GP bị thay thế — cần xác định GP cũ | 1 |
| GP cấp huyện cũ: sổ không ghi UBND huyện nào — cần xác nhận cơ quan cấp | 1 |
| Ghi chú sổ: … — cần xác nhận lựa chọn chuyển tiếp | 1 |
| Ngày ký sau khi hợp nhất tỉnh … nhưng nằm ở sheet … — cần xác nhận cơ quan cấp | 1 |
| Chỉ có trong sheet VHTN, không có ở … sheet GPMT — cần bổ sung thông tin và cơ quan cấp | 1 |

### Danh sách chi tiết

| Số hiệu | Cơ sở | Nguồn | Lý do |
|---|---|---|---|
| 1869/GPMT-UBND | Dự án XD Trung tâm Y tế huyện Si Ma Cai | excel:GPMT Tinh cap:dòng 26 | Sổ không ghi ngày ký — cần bổ sung |
| 2010/QĐ-UBND | Dự án khai thác cát, sỏi làm VLXDTT trên sông Hồng | excel:GPMT Tinh cap:dòng 28 | Ký hiệu 'QĐ-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 1616/GPMT-UBND | Dự án thuỷ điện Nậm Lúc | excel:GPMT Tinh cap:dòng 29 | Số GP lấy từ sheet VHTN dòng 24, ghép với sổ chính theo tên gần đúng — cần duyệt |
| 512/GPMT-UBND | Dự án Hệ thống xử lý nước thải khu công nghiệp Tằng Loỏng (giai đoạn 2) | excel:GPMT Tinh cap:dòng 30 | Số GP lấy từ sheet VHTN dòng 25, ghép với sổ chính theo tên gần đúng — cần duyệt |
| 2341/GPTNMT-UBND | Dự án khu nghỉ dưỡng Đồi Con Gái Sa Pa | excel:GPMT Tinh cap:dòng 35 | Ký hiệu 'GPTNMT-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 2451/QĐ-UBND | Dự án tòa nhà Phú Hưng | excel:GPMT Tinh cap:dòng 37 | Ký hiệu 'QĐ-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 2603/QĐ-UBND | Hệ thống xử lý nước thải (giai đoạn 1) | excel:GPMT Tinh cap:dòng 38 | Ký hiệu 'QĐ-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| (chưa có số) | dự án Khai thác, chế biến đá xây dựng tại mỏ đá thôn Toòng Già, thị trấn Phong H | excel:GPMT Tinh cap:dòng 39 | Sổ không ghi số giấy phép |
| 3010/QĐ-UBND | Dự án Nhà máy tuyển quặng Apatit loại III | excel:GPMT Tinh cap:dòng 41 | Ký hiệu 'QĐ-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 3234/GPTN-UBND | dự án thủy điện Móng Sến, thị xã Sa Pa, tỉnh Lào Cai | excel:GPMT Tinh cap:dòng 46 | Ký hiệu 'GPTN-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 266/QĐ-UBND | Nhà máy sản xuất hàng may mặc xuất khẩu | excel:GPMT Tinh cap:dòng 53 | Ký hiệu 'QĐ-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 227/QĐ-UBND | Khu xử lý rác thải sinh hoạt hợp vệ sinh huyện Bảo Yên | excel:GPMT Tinh cap:dòng 54 | Ký hiệu 'QĐ-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận<br>Năm ký (2025) khác nhóm năm của sổ (2024) — kiểm tra lại ngày ký |
| 3014/QĐ-UBND | Cơ sở cai nghiên số 1 - Xuân Quang Bảo Thắng | excel:GPMT Tinh cap:dòng 55 | Ký hiệu 'QĐ-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận<br>Năm ký (2023) khác nhóm năm của sổ (2024) — kiểm tra lại ngày ký |
| 1947/GP-UBND | Dự án khai thác, chế biến khoáng sản đá làm VLXDTT | excel:GPMT Tinh cap:dòng 67 | Ô nước thải ghi '2023' — nghi nhập nhầm năm vào cột số liệu |
| 1498/GPMT-UBND | Bệnh viên đa khoa huyện Bảo Thắng (cấp lại) | excel:GPMT Tinh cap:dòng 88 | Sổ ghi 'cấp lại' nhưng không ghi GP bị thay thế — cần xác định GP cũ |
| 1723/GPMT-UBND | Dự án nhà máy sản xuất các sản phẩm gỗ và ván lát sàn SPC Thiên Hòa | excel:GPMT cấp huyện cũ:dòng 4 | GP cấp huyện cũ: sổ không ghi UBND huyện nào — cần xác nhận cơ quan cấp |
| 2568/GPMT-UBND | Trang trại chăn nuôi lợn khép kín công nghệ cao | excel:GPMT tỉnh YB cũ:dòng 12 | Ô 'Giấy phép số' chứa 2 giấy phép — đã tách thành 2 bản ghi, cần xác nhận |
| 1827/GPMT-UBND | Trang trại chăn nuôi lợn khép kín công nghệ cao | excel:GPMT tỉnh YB cũ:dòng 12 | Ô 'Giấy phép số' chứa 2 giấy phép — đã tách thành 2 bản ghi, cần xác nhận<br>Trùng số hiệu và ngày ký với bản ghi khác nhưng khác cơ sở ('Trang trại chăn nuôi lợn khép kín công nghệ cao, thôn An Kha' / 'Công trình thuỷ điện Văn Chấn') — cần đối chiếu bản gốc |
| 861/GPMT-UBND | Dự án Trung tâm Đăng kiểm phương tiện cơ giới đường bộ | excel:GPMT tỉnh YB cũ:dòng 19 | Ghi chú sổ: 'Đơn vị dã thực hiện ĐKMT' — cần xác nhận lựa chọn chuyển tiếp |
| 2517/GPTN-UBND | Dự án Xây dựng Khu đô thị Bách Lẫm B | excel:GPMT tỉnh YB cũ:dòng 22 | Ký hiệu 'GPTN-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 2054/QĐ-UBND | Dự án đầu tư xây dựng công trình Lò đốt chất thải rắn sinh hoạt tại Xã Cảm Nhân, | excel:GPMT tỉnh YB cũ:dòng 33 | Ký hiệu 'QĐ-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 122/GPTN-UBND | Dự án Xây dựng Khu đô thị Bách Lẫm A (giai đoạn 2) | excel:GPMT tỉnh YB cũ:dòng 47 | Ký hiệu 'GPTN-UBND' chưa rõ là loại văn bản gì (GPMT hay văn bản khác) — cần xác nhận |
| 1827/GPMT-UBND | Công trình thuỷ điện Văn Chấn | excel:GPMT tỉnh YB cũ:dòng 59 | Trùng số hiệu và ngày ký với bản ghi khác nhưng khác cơ sở ('Trang trại chăn nuôi lợn khép kín công nghệ cao, thôn An Kha' / 'Công trình thuỷ điện Văn Chấn') — cần đối chiếu bản gốc |
| 752/GPMT-UBND | Xưởng sản xuất bột đá trắng | excel:GPMT tỉnh YB cũ:dòng 62 | Ngày ký sau khi hợp nhất tỉnh (01/7/2025) nhưng nằm ở sheet 'GPMT tỉnh YB cũ' — cần xác nhận cơ quan cấp |
| 412/GPMT-BTNMT | Nhà máy sản xuất dung dịch thủy tinh hữu cơ - MMA (giai đoạn 1) | excel:GPMT tỉnh YB cũ:dòng 70 | Năm ký (2022) khác nhóm năm của sổ (2025) — kiểm tra lại ngày ký |
| 22/GPMT-BTNMT | Mỏ khai thác và chế biến đá hoa | excel:GPMT tỉnh YB cũ:dòng 71 | Năm ký (2024) khác nhóm năm của sổ (2025) — kiểm tra lại ngày ký |
| 129/GPMT-BTNMT | Mỏ khai thác đá hoa trắng khu vực Bản Nghè | excel:GPMT tỉnh YB cũ:dòng 73 | Năm ký (2023) khác nhóm năm của sổ (2025) — kiểm tra lại ngày ký |
| 150/GPMT-BTNMT | Mỏ chì kẽm Xã Xà Hồ | excel:GPMT tỉnh YB cũ:dòng 74 | Sổ không ghi ngày ký — cần bổ sung |
| 938/GPMT-UBND | Nhà máy sản xuất ván ép Sunrise YB (giai đoạn 1) | excel:VHTN:dòng 140 | Chỉ có trong sheet VHTN, không có ở 3 sheet GPMT — cần bổ sung thông tin và cơ quan cấp |

## 4. Dòng trùng đã gộp: 2

| Số hiệu | Giữ | Gộp vào |
|---|---|---|
| 2609/GP-UBND | excel:GPMT Tinh cap:dòng 71 | excel:GPMT Tinh cap:dòng 74 |
| 2279/GPMT-UBND | excel:GPMT tỉnh YB cũ:dòng 37 | excel:GPMT tỉnh YB cũ:dòng 41 |

## 5. Cảnh báo đã tự xử lý (không gắn cờ, chỉ liệt kê): 25

| Nguồn | Số hiệu | Nội dung |
|---|---|---|
| excel:GPMT Tinh cap:dòng 12 | 147/GP-UBND | CTR thông thường (sổ): '15.000m3/năm Đất đá thải; 10 kg/năm Chất thải rắn sinh hoạt phát sinh' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT Tinh cap:dòng 18 | 891/GP-UBND | nước thải: 'Dòng nước thải số 1: 42 m3/ngày đêm. - Dòng nước thải số 2: 16 m3/ngày đêm - Dòng nước thải số 3: 1,2 m3/ngày đêm' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT Tinh cap:dòng 19 | 970/GP-UBND | CTR thông thường (sổ): '110 kg/năm Chất thải rắn sinh hoạt phát sinh; 20.000 m3/nămBùn thải (nạo vét từ lòng hồ)' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT Tinh cap:dòng 20 | 1051/GP-UBND | Ngày có dấu '/' thừa '05/5//2023' |
| excel:GPMT Tinh cap:dòng 20 | 1051/GP-UBND | CTR thông thường (sổ): '936 kg/năm Chất thải rắn sinh hoạt phát sinh; 17.750 m3/năm.Bùn thải (nạo vét từ lòng hồ)' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT Tinh cap:dòng 21 | 1069/GP-UBND | CTR thông thường (sổ): '842 kg/năm Chất thải rắn sinh hoạt phát sinh 550 m3/năm Bùn thải (nạo vét từ lòng hồ)' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT Tinh cap:dòng 22 | 1079/GP-UBND | CTNH: '798,6 +35' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT Tinh cap:dòng 23 | 1663/GP-UBND | Ngày ghi sai định dạng '007/7/2023' |
| excel:GPMT Tinh cap:dòng 86 | 866/GPMT-UBND | Ký hiệu có dấu cách thừa 'GPMT- UBND' |
| excel:GPMT tỉnh YB cũ:dòng 13 | 1256/GPMT-UBND | CTNH: '180-300' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT tỉnh YB cũ:dòng 16 | 768/GPMT-UBND | Ký hiệu gõ lỗi 'GPMT-UNMD', đã sửa thành 'GPMT-UBND' |
| excel:GPMT tỉnh YB cũ:dòng 25 | 22/GPMT-UBND | CTR thông thường (sổ): '200-1060 tấn/năm' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT tỉnh YB cũ:dòng 27 | 111/GPMT-UBND | nước thải: '0.7 m3/ngày đêm NTSH; 80 m3/ngày đêm NTSX' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT tỉnh YB cũ:dòng 27 | 111/GPMT-UBND | CTR thông thường (sổ): 'phân 0,5 tấn/ngày' giữ nguyên văn (có chữ mô tả kèm theo, cần đọc tay) |
| excel:GPMT tỉnh YB cũ:dòng 29 | 1104/GPMT-UBND | nước thải: '5 m3/ngày đêm NTSH; 54 m3/ngày đêm NTSX' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT tỉnh YB cũ:dòng 29 | 1104/GPMT-UBND | CTR thông thường (sổ): 'phân:0,9 tấn/ngày' giữ nguyên văn (có chữ mô tả kèm theo, cần đọc tay) |
| excel:GPMT tỉnh YB cũ:dòng 40 | 2085/GPMT-UBND | nước thải: '5m3/ngày đêm NTSH; 75 m3/ngày đêm NTSX' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT tỉnh YB cũ:dòng 40 | 2085/GPMT-UBND | CTR thông thường (sổ): 'phân 9 tấn/ngày' giữ nguyên văn (có chữ mô tả kèm theo, cần đọc tay) |
| excel:GPMT tỉnh YB cũ:dòng 49 | 1616/GPMT-UBND | nước thải: '20 m3/ngày đêm NTSH; 16m3/ngày đêm NTSX' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT tỉnh YB cũ:dòng 51 | 59/GPMT-UBND | CTR thông thường (sổ): '30-50 kg cỏ khô/01 hố golf' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT tỉnh YB cũ:dòng 51 | 59/GPMT-UBND | CTNH: '280-319' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT tỉnh YB cũ:dòng 60 | 1388/GPMT-UBND | nước thải: '2,3 m3/ngày đêm NTSH; 195 m3/ngày đêm NTSX' giữ nguyên văn (nhiều số liệu trong một ô) |
| excel:GPMT Tinh cap:dòng 74 | 2609/GPMT-UBND | Dòng trùng ghi ký hiệu khác ('2609/GPMT-UBND' so với '2609/GP-UBND') |
| excel:VHTN:dòng 114 | (chưa có số) | Địa chỉ 'Phương Nghĩa Lộ, tỉnh Lào Cai' viết 'Phương', đã hiểu là 'Phường' |
| excel:VHTN:dòng 22 | (chưa có số) | Tên cơ sở bị xuống dòng, đã nối vào dòng 21 |

## 6. Dòng bỏ qua: 17

| Sheet | Dòng | Lý do |
|---|---:|---|
| GPMT tỉnh YB cũ | 68 | dòng nhãn nhóm 'GPMT do Bộ cấp' (dùng làm nhãn cho các dòng sau) |
| GPMT cấp huyện cũ | 5 | chỉ có số thứ tự '2', các cột khác trống |
| GPMT cấp huyện cũ | 6 | chỉ có số thứ tự '3', các cột khác trống |
| GPMT cấp huyện cũ | 7 | chỉ có số thứ tự '4', các cột khác trống |
| GPMT cấp huyện cũ | 8 | chỉ có số thứ tự '5', các cột khác trống |
| GPMT cấp huyện cũ | 9 | chỉ có số thứ tự '6', các cột khác trống |
| GPMT cấp huyện cũ | 10 | chỉ có số thứ tự '7', các cột khác trống |
| GPMT cấp huyện cũ | 11 | chỉ có số thứ tự '8', các cột khác trống |
| GPMT cấp huyện cũ | 12 | chỉ có số thứ tự '9', các cột khác trống |
| GPMT cấp huyện cũ | 13 | chỉ có số thứ tự '10', các cột khác trống |
| GPMT cấp huyện cũ | 14 | chỉ có số thứ tự '11', các cột khác trống |
| GPMT cấp huyện cũ | 15 | chỉ có số thứ tự '12', các cột khác trống |
| GPMT cấp huyện cũ | 16 | chỉ có số thứ tự '13', các cột khác trống |
| GPMT cấp huyện cũ | 17 | chỉ có số thứ tự '14', các cột khác trống |
| GPMT cấp huyện cũ | 18 | chỉ có số thứ tự '15', các cột khác trống |
| GPMT cấp huyện cũ | 19 | chỉ có số thứ tự '16', các cột khác trống |
| GPMT cấp huyện cũ | 20 | chỉ có số thứ tự '17', các cột khác trống |

## 7. Giấy phép đã đối chiếu tay với bản gốc PDF

- 2519/GPMT-UBND ngày 22/07/2026 (2519_GPMT-UBND.json): Còn hiệu lực
  - 1439/GPMT-UBND → Hết hiệu lực — bị thay thế bởi 2519/GPMT-UBND
