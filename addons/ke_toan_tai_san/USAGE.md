# Hướng Dẫn Sử Dụng Module Kế Toán Tài Sản

## ✅ Module Đã Hoàn Thành

Module `ke_toan_tai_san` đã được cài đặt thành công với các tính năng:

### 1. **Models Chính**
- `khau_hao_tai_san` - Quản lý khấu hao tài sản
- `tai_khoan_khau_hao` - Cấu hình tài khoản khấu hao
- `so_tai_san` - Sổ tài sản (bảng cân đối)
- `ke_toan.dashboard` - Dashboard kế toán

### 2. **Views**
- **Khấu Hao**: List view, Form view, Search view
- **Cấu Hình Tài Khoản**: List view, Form view
- **Sổ Tài Sản**: List view, Form view
- **Dashboard**: Form view hiển thị thống kê

### 3. **Menu**
- Kế Toán Tài Sản (Parent Menu)
  - Dashboard
  - Khấu Hao Tài Sản
  - Sổ Tài Sản
  - Cấu Hình > Cấu Hình Tài Khoản

## 🚀 Cách Sử Dụng

### Bước 1: Cấu Hình Tài Khoản
1. Vào **Kế Toán Tài Sản → Cấu Hình → Cấu Hình Tài Khoản**
2. Tạo cấu hình cho từng loại tài sản
3. Chọn sổ nhật ký kế toán (General Journal)
4. Chọn các tài khoản tương ứng

### Bước 2: Quản Lý Khấu Hao
1. Vào **Kế Toán Tài Sản → Khấu Hao Tài Sản**
2. Tạo bản ghi khấu hao mới
3. Nhập thông tin tài sản, số tiền khấu hao
4. Nhấn "Ghi sổ" để ghi nhận vào sổ cái

### Bước 3: Xem Sổ Tài Sản
1. Vào **Kế Toán Tài Sản → Sổ Tài Sản**
2. Tạo bản ghi sổ cho tháng/năm
3. Xem bảng cân đối: Giá trị ban đầu → Khấu hao → Giá trị còn lại

### Bước 4: Xem Dashboard
1. Vào **Kế Toán Tài Sản → Dashboard**
2. Xem thống kê tài sản và chi phí khấu hao

## 📊 Dashboard CSS Thống Nhất

Tất cả 4 module sử dụng file CSS chung: `dashboard_common.css`
- **quan_ly_tai_san**
- **quan_ly_ngan_sach**
- **quanly_thuchi_congno**
- **ke_toan_tai_san** (mới)

### Bảng Màu:
- **Primary**: Xanh đậm (#0066cc)
- **Success**: Xanh lá (#28a745)
- **Warning**: Vàng (#ffc107)
- **Danger**: Đỏ (#dc3545)
- **Info**: Xanh nhạt (#17a2b8)

## 🔌 API Dự Báo Dòng Tiền

### Endpoint
```
POST /api/du_bao_thu_chi
```

### Yêu Cầu
```json
{
    "thang": 1,
    "nam": 2026
}
```

### Phản Hồi
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

## ✨ Các Tính Năng

- ✅ Khấu hao tài sản tự động
- ✅ Tích hợp sổ cái kế toán
- ✅ Bảng cân đối tài sản
- ✅ Dashboard kế toán
- ✅ API dự báo dòng tiền
- ✅ Responsive design
- ✅ CSS thống nhất với các module khác

## 📝 Ghi Chú

- Module đã được đơn giản hóa để tránh lỗi search view
- Cron Jobs tạm thời disabled (set active=False) - có thể bật sau nếu cần
- Tất cả models, views, menus đã hoàn thành
- API controller sẵn sàng để tích hợp dự báo AI

## 🔧 Troubleshooting

Nếu gặp lỗi:
1. Xóa database và tạo lại
2. Cài đặt lại module: `python3 odoo-bin.py -c odoo.conf -u ke_toan_tai_san`
3. Kiểm tra logs: `tail -f /var/log/odoo/odoo.log`

---

**Ngày tạo**: 26/01/2026
**Phiên bản**: 1.0
**Tác giả**: TTDN-16-06-N4
