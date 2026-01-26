# Module Kế Toán Tài Sản & Khấu Hao (ke_toan_tai_san)

## Mô tả
Module này cung cấp giải pháp toàn diện quản lý khấu hao tài sản và tích hợp sổ cái kế toán, với khả năng dự báo dòng tiền bằng AI.

## Chức năng chính

### 1. **Khấu Hao Tài Sản Tự Động**
- Tính toán khấu hao tự động hàng tháng thông qua Cron Jobs
- Hỗ trợ 3 phương pháp khấu hao:
  - **Tuyến tính (Straight-line)**: Khấu hao đều hàng tháng
  - **Giảm dần (Degressive)**: Khấu hao cao ở đầu, giảm dần
  - **Đơn vị sản xuất (Units)**: Khấu hao dựa trên sản lượng

### 2. **Tích Hợp Sổ Cái Kế Toán**
- Tự động tạo bút toán (Journal Entries) cho mỗi lần khấu hao
- Định cấu hình tài khoản kế toán theo loại tài sản:
  - TK Tài sản cố định (Fixed Assets)
  - TK Khấu hao tích lũy (Accumulated Depreciation)
  - TK Chi phí khấu hao (Depreciation Expense)

### 3. **Bảng Cân Đối Tài Sản (Asset Register)**
- Sổ tài sản chi tiết theo tháng/năm
- Thể hiện: Giá trị ban đầu → Khấu hao tích lũy → Giá trị còn lại
- Tính toán tự động dựa trên dữ liệu khấu hao đã ghi sổ

### 4. **Dashboard Kế Toán**
- Hiển thị thống kê tài sản:
  - Tổng số tài sản
  - Tổng giá trị ban đầu
  - Khấu hao tích lũy
  - Giá trị còn lại
- Chi phí khấu hao theo tháng và năm
- Giao diện thống nhất với các module khác

### 5. **API Dự Báo Dòng Tiền (AI)**
- API REST: `/api/du_bao_thu_chi`
- Dự báo dòng tiền dựa trên lịch sử
- Tính toán ảnh hưởng của khấu hao tới dòng tiền

## Cấu Trúc Dữ Liệu

### Models Chính

#### 1. **khau_hao_tai_san** - Chi tiết khấu hao
```
- ma_khau_hao: Mã khấu hao (tự động sinh)
- tai_san_id: Liên kết tài sản
- ngay_khau_hao: Ngày khấu hao
- gia_tri_con_lai: Giá trị trước khấu hao
- so_tien_khau_hao: Số tiền khấu hao
- gia_tri_sau_khau_hao: Giá trị sau khấu hao (tính toán)
- pp_khau_hao: Phương pháp khấu hao
- journal_entry_id: Bút toán sổ cái
- trang_thai: Trạng thái (draft, posted, cancelled)
```

#### 2. **tai_khoan_khau_hao** - Cấu hình tài khoản
```
- loai_tai_san_id: Loại tài sản
- journal_id: Sổ nhật ký kế toán
- account_asset_id: TK Tài sản cố định
- account_accumulated_depreciation_id: TK Khấu hao tích lũy
- account_depreciation_expense_id: TK Chi phí khấu hao
- thoi_gian_su_dung: Thời gian sử dụng (năm)
- ty_le_khau_hao: Tỷ lệ khấu hao (%)
```

#### 3. **so_tai_san** - Sổ tài sản
```
- thang: Tháng
- nam: Năm
- tai_san_ids: Chi tiết tài sản (One2many)
- tong_gia_tri_ban_dau: Tổng giá trị ban đầu
- tong_khau_hao_luy_ke: Tổng khấu hao lũy kế
- tong_gia_tri_con_lai: Tổng giá trị còn lại
```

#### 4. **ke_toan.dashboard** - Dashboard
```
- tong_tai_san: Tổng số tài sản
- tong_gia_tri_tai_san: Tổng giá trị
- tong_khau_hao: Khấu hao tích lũy
- gia_tri_con_lai: Giá trị còn lại
- chi_phi_khau_hao_thang_nay: Chi phí tháng này
- chi_phi_khau_hao_nam_nay: Chi phí năm nay
```

## Qui Trình Sử Dụng

### Bước 1: Cấu Hình Tài Khoản
1. Vào **Kế Toán Tài Sản → Cấu Hình → Cấu Hình Tài Khoản**
2. Tạo cấu hình cho từng loại tài sản
3. Chọn sổ nhật ký và tài khoản kế toán tương ứng

### Bước 2: Tính Khấu Hao
**Cách 1: Tự động (Cron Job)**
- Hệ thống sẽ tự động tính khấu hao vào ngày 1 hàng tháng
- Khấu hao được ghi sổ tự động

**Cách 2: Thủ công**
1. Vào **Kế Toán Tài Sản → Sổ Tài Sản**
2. Tạo bản ghi mới cho tháng/năm
3. Nhấn nút **"Tính khấu hao"**
4. Hệ thống sẽ tính khấu hao cho tất cả tài sản

### Bước 3: Ghi Sổ Kế Toán
1. Vào **Kế Toán Tài Sản → Khấu Hao Tài Sản**
2. Chọn bản ghi khấu hao (trạng thái "Nháp")
3. Nhấn **"Ghi sổ"**
4. Bút toán sẽ được tạo trong sổ nhật ký

### Bước 4: Xem Báo Cáo
1. **Dashboard**: Xem tổng quan giá trị tài sản
2. **Sổ Tài Sản**: Xem bảng cân đối chi tiết
3. **Danh sách Khấu Hao**: Xem lịch sử khấu hao

## API Dự Báo Dòng Tiền

### Endpoint
```
POST /api/du_bao_thu_chi
```

### Request
```json
{
    "thang": 1,
    "nam": 2026
}
```

### Response
```json
{
    "status": "success",
    "data": {
        "thang": 1,
        "nam": 2026,
        "du_bao_thu": 50000000,
        "du_bao_chi": 40000000,
        "du_bao_khau_hao": 5000000,
        "dong_tien_rong": 10000000,
        "mo_ta": "Dự báo dòng tiền tháng 1/2026"
    }
}
```

## Dashboard CSS Thống Nhất

Module sử dụng file CSS chung `dashboard_common.css` với:
- Bảng màu tiêu chuẩn (Primary, Success, Warning, Danger, Info)
- Gradient backgrounds cho các card
- Responsive design
- Transition effects
- Thiết kế modern

## Cron Jobs

### 1. Khấu hao tự động (Hàng tháng)
- **Tên**: "Khấu hao tài sản - Tự động hàng tháng"
- **Tần suất**: 1 tháng 1 lần
- **Chức năng**: Tính và ghi sổ khấu hao cho tất cả tài sản

### 2. Cập nhật dự báo (Hàng tuần)
- **Tên**: "Dự báo dòng tiền - Hàng tuần"
- **Tần suất**: 1 tuần 1 lần
- **Chức năng**: Cập nhật dữ liệu dự báo trên dashboard

## Tích Hợp Với Các Module Khác

- **quan_ly_tai_san**: Lấy dữ liệu tài sản, phương pháp khấu hao
- **quan_ly_ngan_sach**: Theo dõi chi phí khấu hao trong ngân sách
- **quanly_thuchi_congno**: Ghi nhận giao dịch liên quan đến tài sản
- **account** (Odoo): Sổ cái kế toán

## Quyền Truy Cập

- **Người dùng (user)**: Xem dashboard, danh sách khấu hao
- **Quản lý kế toán (account_manager)**: Quản lý, tạo, sửa, xóa khấu hao và sổ tài sản

## Thông Tin Liên Hệ

- **Tác giả**: TTDN-16-06-N4
- **Phiên bản**: 1.0
- **Giấy phép**: LGPL-3
