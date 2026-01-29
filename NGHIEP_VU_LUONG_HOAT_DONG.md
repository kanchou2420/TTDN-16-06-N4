# 📋 MÔ TẢ NGHIỆP VỤ VÀ LUỒNG HOẠT ĐỘNG HỆ THỐNG

## Tổng quan hệ thống

Hệ thống quản lý tổng hợp bao gồm **5 module chính** liên kết chặt chẽ với nhau:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           NHÂN SỰ (nhan_su)                             │
│                    Quản lý thông tin nhân viên, chức vụ                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────────┐  ┌─────────────────────┐  ┌─────────────────────────┐
│   QUẢN LÝ TÀI SẢN │  │  QUẢN LÝ NGÂN SÁCH  │  │  THU CHI CÔNG NỢ        │
│   (quan_ly_tai_san)│  │ (quan_ly_ngan_sach) │  │ (quanly_thuchi_congno)  │
└─────────┬─────────┘  └──────────┬──────────┘  └────────────┬────────────┘
          │                       │                          │
          └───────────────────────┼──────────────────────────┘
                                  ▼
                    ┌─────────────────────────┐
                    │   KẾ TOÁN TÀI SẢN &     │
                    │   DỰ BÁO AI             │
                    │   (ke_toan_tai_san)     │
                    └─────────────────────────┘
```

---

## 1️⃣ MODULE NHÂN SỰ (nhan_su)

### 📌 Mục đích
Quản lý thông tin nhân sự làm nền tảng cho toàn bộ hệ thống.

### 📊 Các đối tượng quản lý

| Model | Mô tả | Vai trò |
|-------|-------|---------|
| `nhan_vien` | Nhân viên | Chứa thông tin cá nhân, chức vụ, phòng ban |
| `chuc_vu` | Chức vụ | Phân loại vai trò: Nhân viên, Trưởng phòng, Giám đốc, Chủ tịch |
| `phong_ban` | Phòng ban | Đơn vị tổ chức trong doanh nghiệp |
| `lich_su_cong_tac` | Lịch sử công tác | Theo dõi quá trình làm việc |

### 🔑 Logic quan trọng: Phân quyền lãnh đạo

```python
# Field is_lanh_dao tự động tính toán
lanh_dao_keywords = ['chủ tịch', 'giám đốc', 'director', 'president', 'ceo']
is_lanh_dao = any(keyword in ten_chuc_vu.lower() for keyword in lanh_dao_keywords)
```

**Ý nghĩa**: Chỉ nhân sự có `is_lanh_dao = True` mới được phép:
- ✅ Duyệt ngân sách
- ✅ Duyệt phiếu chi
- ✅ Duyệt phiếu thu

### 📈 Luồng nghiệp vụ

```
[Tạo nhân viên] ──► [Chọn chức vụ BẮT BUỘC] ──► [Gán phòng ban] ──► [Lưu lịch sử công tác]
                           │
                           ▼
                  [Tự động tính is_lanh_dao]
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              [Lãnh đạo]    [Nhân viên]
                    │             │
                    ▼             ▼
            [Quyền duyệt]  [Quyền thao tác]
```

---

## 2️⃣ MODULE QUẢN LÝ TÀI SẢN (quan_ly_tai_san)

### 📌 Mục đích
Quản lý vòng đời tài sản từ khi mua đến khi thanh lý.

### 📊 Các đối tượng quản lý

| Model | Mô tả | Trạng thái |
|-------|-------|------------|
| `tai_san` | Tài sản | Chưa phân bổ → Đã phân bổ → Đã thanh lý |
| `danh_muc_tai_san` | Danh mục/Loại tài sản | Máy tính, Xe cộ, Máy móc... |
| `phan_bo_tai_san` | Phân bổ tài sản | Đang sử dụng / Không sử dụng |
| `muon_tra_tai_san` | Mượn trả tài sản | Đang mượn → Đã trả |
| `don_muon_tai_san` | Đơn xin mượn | Chờ duyệt → Đã duyệt → Từ chối |
| `luan_chuyen_tai_san` | Luân chuyển tài sản | Chuyển giữa các phòng ban |
| `kiem_ke_tai_san` | Kiểm kê tài sản | Chưa kiểm kê → Đã kiểm kê |
| `thanh_ly_tai_san` | Thanh lý tài sản | Bán / Tiêu hủy |
| `lich_su_khau_hao` | Lịch sử khấu hao | Ghi nhận khấu hao theo thời gian |
| `lich_su_ky_thuat` | Tình trạng kỹ thuật | Theo dõi bảo trì, sửa chữa |

### 🔄 Luồng vòng đời tài sản

```
                    ┌─────────────────┐
                    │    MUA TÀI SẢN  │
                    │  (Tạo tai_san)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   PHÂN BỔ       │
                    │ (phan_bo_tai_san)│
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   SỬ DỤNG       │ │   MƯỢN TRẢ      │ │   LUÂN CHUYỂN   │
│  (phòng ban)    │ │(muon_tra_tai_san)│ │(luan_chuyen)   │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   KIỂM KÊ       │
                    │(kiem_ke_tai_san)│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   KHẤU HAO      │
                    │(lich_su_khau_hao)│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   THANH LÝ      │
                    │(thanh_ly_tai_san)│
                    │  Bán / Hủy      │
                    └─────────────────┘
```

### 📋 Chi tiết luồng nghiệp vụ

#### A. Nhập tài sản mới
```
1. Tạo tài sản mới:
   - Mã tài sản (unique)
   - Tên tài sản
   - Ngày mua
   - Giá trị ban đầu = Giá trị hiện tại
   - Loại tài sản (danh_muc_tai_san)
   - Phương pháp khấu hao (Tuyến tính / Giảm dần / Không)
   
2. Trạng thái: "Chưa phân bổ"
```

#### B. Phân bổ tài sản cho phòng ban
```
1. Chọn tài sản cần phân bổ
2. Chọn phòng ban sử dụng
3. Chọn nhân viên sử dụng (nếu có)
4. Nhập vị trí đặt tài sản
5. Xác nhận phân bổ

→ Trạng thái tài sản: "Đã phân bổ"
→ Tạo bản ghi phan_bo_tai_san
```

#### C. Mượn trả tài sản
```
1. Nhân viên tạo Đơn mượn tài sản:
   - Chọn phòng ban cho mượn
   - Chọn tài sản cần mượn
   - Thời gian mượn - trả dự kiến
   
2. Người phụ trách DUYỆT đơn mượn:
   - Tạo phiếu Mượn trả tài sản
   - Trạng thái đơn: "Đã duyệt"
   
3. Khi trả tài sản:
   - Cập nhật trạng thái: "Đã trả"
   - Ghi chú tình trạng tài sản
```

#### D. Luân chuyển tài sản
```
1. Tạo phiếu luân chuyển:
   - Bộ phận nguồn (hiện tại)
   - Bộ phận đích (chuyển tới)
   - Danh sách tài sản cần chuyển
   - Lý do luân chuyển
   
2. Khi xác nhận:
   → Tự động cập nhật phong_ban_id của phan_bo_tai_san
   → Cập nhật vị trí mới
   → Ghi chú lịch sử
```

#### E. Kiểm kê tài sản
```
1. Tạo phiếu kiểm kê:
   - Chọn phòng ban cần kiểm kê
   - Nhân viên thực hiện kiểm kê
   
2. Thực hiện kiểm kê:
   - Hệ thống load danh sách tài sản của phòng ban
   - Kiểm tra từng tài sản:
     + Có tồn tại không?
     + Tình trạng kỹ thuật?
     + Vị trí đúng không?
   
3. Hoàn thành:
   - Ghi nhận kết quả
   - Trạng thái phiếu: "Đã kiểm kê"
```

#### F. Thanh lý tài sản
```
1. Chọn tài sản cần thanh lý
2. Chọn hình thức:
   - BÁN: Nhập giá bán → Tạo phiếu thu thanh lý
   - HỦY: Ghi nhận tiêu hủy
   
3. Người thực hiện: Nhân viên từ module nhan_su
4. Xác nhận thanh lý

→ Trạng thái tài sản: "Đã thanh lý"
→ Nếu bán: Liên kết với phiếu thu (loại: thu_thanh_ly)
```

---

## 3️⃣ MODULE QUẢN LÝ NGÂN SÁCH (quan_ly_ngan_sach)

### 📌 Mục đích
Lập kế hoạch, phân bổ và theo dõi thực hiện ngân sách.

### 📊 Các đối tượng quản lý

| Model | Mô tả | Trạng thái |
|-------|-------|------------|
| `ngan_sach` | Ngân sách | Nháp → Đã duyệt → Đang thực hiện → Kết thúc / Hủy |
| `du_toan_chi` | Dự toán chi | Đề xuất → Duyệt → Từ chối |
| `phan_bo_ngan_sach` | Phân bổ ngân sách | Chưa sử dụng → Đang sử dụng → Đã hết / Hết hạn |
| `theo_doi_thuc_hien_ngan_sach` | Theo dõi thực hiện | Đang xử lý → Hoàn thành → Hủy |

### 🔄 Luồng quản lý ngân sách

```
┌─────────────────────────────────────────────────────────────────┐
│                    LẬP NGÂN SÁCH                                │
│  1. Tạo ngân sách (năm/quý/tháng/dự án)                        │
│  2. Nhập tổng ngân sách                                         │
│  3. Người lập: Nhân viên (nhan_su)                             │
│  4. Trạng thái: NHÁP                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DUYỆT NGÂN SÁCH                              │
│  ⚠️ CHỈ CHỦ TỊCH HOẶC GIÁM ĐỐC (is_lanh_dao = True)            │
│  - Người duyệt chọn từ danh sách lãnh đạo                       │
│  - Xác nhận duyệt                                               │
│  → Trạng thái: ĐÃ DUYỆT                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TẠO DỰ TOÁN CHI                              │
│  - Nhân viên đề xuất chi tiêu                                   │
│  - Người đề xuất: từ nhan_su                                    │
│  - Hạng mục chi: Mua tài sản, Sửa chữa, Văn phòng phẩm...      │
│  - Số tiền dự kiến                                              │
│  → Người duyệt: CHỈ LÃNH ĐẠO                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHÂN BỔ NGÂN SÁCH                            │
│  Phân bổ theo:                                                  │
│  - Phòng ban                                                    │
│  - Danh mục tài sản                                             │
│  - Dự án                                                        │
│  - Hoạt động                                                    │
│                                                                 │
│  ⚠️ Ràng buộc: Tổng phân bổ ≤ Tổng ngân sách                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 THEO DÕI THỰC HIỆN                              │
│  Ghi nhận mỗi giao dịch chi tiêu:                              │
│  - Loại giao dịch: Chi tiêu / Thu nhập                         │
│  - Số tiền thực tế                                              │
│  - Người thực hiện: từ nhan_su                                  │
│  - Người duyệt: CHỈ LÃNH ĐẠO                                   │
│                                                                 │
│  → Tự động cập nhật:                                           │
│    + Số tiền đã sử dụng                                         │
│    + Số tiền còn lại                                            │
│    + Tỷ lệ sử dụng %                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 🧮 Công thức tính toán tự động

```python
# Ngân sách
tong_phan_bo = sum(phan_bo_ids.mapped('so_tien'))
con_lai = tong_ngan_sach - tong_phan_bo

# Phân bổ ngân sách
so_tien_da_su_dung = sum(theo_doi_ids.mapped('so_tien_thuc_te'))
so_tien_con_lai = so_tien - so_tien_da_su_dung
ty_le_su_dung = (so_tien_da_su_dung / so_tien) * 100
```

---

## 4️⃣ MODULE THU CHI CÔNG NỢ (quanly_thuchi_congno)

### 📌 Mục đích
Quản lý dòng tiền, ghi nhận thu chi và theo dõi công nợ.

### 📊 Các đối tượng quản lý

| Model | Mô tả | Trạng thái |
|-------|-------|------------|
| `phieu_thu` | Phiếu thu | Nháp → Xác nhận → Ghi sổ → Hủy |
| `phieu_chi` | Phiếu chi | Nháp → Xác nhận → Duyệt → Ghi sổ → Hủy |
| `cong_no_phai_thu` | Công nợ phải thu | Nháp → Đang nợ → Thu một phần → Đã thu đủ |
| `cong_no_phai_tra` | Công nợ phải trả | Nháp → Đang nợ → Trả một phần → Đã trả đủ |

### 🔄 Luồng phiếu thu

```
┌─────────────────────────────────────────────────────────────────┐
│                       TẠO PHIẾU THU                             │
│  Loại thu:                                                      │
│  - Thu công nợ: Liên kết cong_no_phai_thu                      │
│  - Thu hoàn tạm ứng: Từ nhân viên                              │
│  - Thu thanh lý tài sản: Liên kết thanh_ly_tai_san             │
│  - Thu khác                                                     │
│                                                                 │
│  Thông tin:                                                     │
│  - Số tiền, Phương thức (Tiền mặt/CK/Thẻ)                      │
│  - Liên kết ngân sách (nếu có)                                  │
│  - Người lập: từ nhan_su                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       XÁC NHẬN                                  │
│  Trạng thái: CONFIRMED                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       GHI SỔ                                    │
│  ⚠️ Người duyệt: CHỈ LÃNH ĐẠO (is_lanh_dao = True)             │
│  → Trạng thái: POSTED                                          │
│  → Nếu thu công nợ: Cập nhật cong_no_phai_thu                  │
│  → Tạo theo_doi_thuc_hien_ngan_sach (nếu liên kết ngân sách)   │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 Luồng phiếu chi

```
┌─────────────────────────────────────────────────────────────────┐
│                       TẠO PHIẾU CHI                             │
│  Loại chi:                                                      │
│  - Chi trả công nợ: Liên kết cong_no_phai_tra                  │
│  - Chi tạm ứng: Cho nhân viên                                   │
│  - Chi mua sắm tài sản: Liên kết tai_san                       │
│  - Chi lương                                                    │
│  - Chi văn phòng phẩm                                           │
│  - Chi khác                                                     │
│                                                                 │
│  ⚠️ Kiểm tra vượt ngân sách tự động                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       XÁC NHẬN                                  │
│  Người xác nhận ghi nhận                                        │
│  Trạng thái: CONFIRMED                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DUYỆT CHI                                 │
│  ⚠️ CHỈ CHỦ TỊCH HOẶC GIÁM ĐỐC (is_lanh_dao = True)            │
│  → Trạng thái: APPROVED                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       GHI SỔ                                    │
│  → Trạng thái: POSTED                                          │
│  → Nếu chi công nợ: Cập nhật cong_no_phai_tra                  │
│  → Tạo theo_doi_thuc_hien_ngan_sach                            │
│  → Trừ ngân sách đã phân bổ                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 💰 Quản lý công nợ

```
                    ┌─────────────────┐
                    │   TẠO CÔNG NỢ   │
                    │  (Phải thu/trả) │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   XÁC NHẬN      │
                    │   State: OPEN   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼                             ▼
    ┌─────────────────┐            ┌─────────────────┐
    │ THANH TOÁN      │            │   QUÁ HẠN       │
    │ (Phiếu thu/chi) │            │  is_overdue=True│
    └────────┬────────┘            └─────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌─────────┐     ┌─────────┐
│ PARTIAL │     │  PAID   │
│(1 phần) │     │(Đủ tiền)│
└─────────┘     └─────────┘
```

---

## 5️⃣ MODULE KẾ TOÁN TÀI SẢN & DỰ BÁO AI (ke_toan_tai_san)

### 📌 Mục đích
- Quản lý khấu hao tài sản
- Tổng hợp dữ liệu tài chính
- Dự báo AI thu chi, chi phí

### 📊 Các đối tượng quản lý

| Model | Mô tả | Vai trò |
|-------|-------|---------|
| `khau_hao_tai_san` | Khấu hao tài sản | Ghi nhận khấu hao hàng kỳ |
| `but_toan_khau_hao` | Bút toán khấu hao | Nội bộ, không cần account module |
| `tai_khoan_khau_hao` | Cấu hình tài khoản | Mã TK theo loại tài sản |
| `so_tai_san` | Sổ tài sản | Bảng tổng hợp tài sản |
| `ai_forecast` | Dự báo AI | Phân tích và dự đoán |
| `ke_toan.dashboard` | Dashboard | Tổng hợp tài chính |

### 🔄 Luồng khấu hao tài sản

```
┌─────────────────────────────────────────────────────────────────┐
│                    CẤU HÌNH KHẤU HAO                            │
│  Theo từng loại tài sản (danh_muc_tai_san):                    │
│  - Mã TK Tài sản cố định (211)                                 │
│  - Mã TK Khấu hao lũy kế (2141)                                │
│  - Mã TK Chi phí khấu hao (6274)                               │
│  - Thời gian sử dụng (năm)                                     │
│  - Tỷ lệ khấu hao (%)                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TÍNH KHẤU HAO                                │
│  Từ tài sản → Tính số tiền khấu hao:                           │
│                                                                 │
│  Phương pháp TUYẾN TÍNH:                                       │
│    khau_hao = gia_tri_ban_dau / thoi_gian_toi_da               │
│                                                                 │
│  Phương pháp GIẢM DẦN:                                         │
│    khau_hao = gia_tri_hien_tai × (ty_le_khau_hao / 100)        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TẠO BẢN GHI KHẤU HAO                         │
│  - Mã khấu hao tự động                                         │
│  - Liên kết tài sản                                             │
│  - Giá trị trước khấu hao                                       │
│  - Số tiền khấu hao                                             │
│  - Giá trị sau khấu hao                                         │
│  → Trạng thái: DRAFT                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GHI SỔ KHẤU HAO                              │
│  → Tạo bút toán nội bộ (but_toan_khau_hao)                     │
│  → Cập nhật giá trị tài sản                                     │
│  → Trạng thái: POSTED                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 🤖 Dự báo AI

```
┌─────────────────────────────────────────────────────────────────┐
│                    TẠO DỰ BÁO MỚI                               │
│  - Tên dự báo                                                   │
│  - Loại dự báo: Thu chi / Khấu hao / Ngân sách / Tổng hợp      │
│  - Kỳ dự báo: 1/3/6/12 tháng                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               🤖 TÍNH TOÁN DỰ BÁO AI                           │
│                                                                 │
│  DỰ BÁO THU CHI:                                               │
│  - Lấy 12 tháng dữ liệu từ phieu_thu, phieu_chi                │
│  - Tính trung bình và xu hướng                                  │
│  - Dự đoán thu chi các tháng tới                               │
│                                                                 │
│  DỰ BÁO KHẤU HAO:                                              │
│  - Lấy danh sách tài sản đang hoạt động                        │
│  - Tính khấu hao theo cấu hình                                  │
│  - Độ tin cậy: 95% (ổn định)                                   │
│                                                                 │
│  DỰ BÁO NGÂN SÁCH:                                             │
│  - Lấy ngân sách đang thực hiện                                 │
│  - Tính tốc độ sử dụng từ theo_doi_thuc_hien                   │
│  - Dự đoán thời điểm hết ngân sách                             │
│                                                                 │
│  DỰ BÁO TỔNG HỢP:                                              │
│  - Kết hợp tất cả dữ liệu trên                                  │
│  - Cân đối = Thu - Chi - Khấu hao                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KẾT QUẢ DỰ BÁO                               │
│  - Dự báo thu: X VNĐ                                           │
│  - Dự báo chi: Y VNĐ                                           │
│  - Dự báo khấu hao: Z VNĐ                                      │
│  - Cân đối: X - Y - Z VNĐ                                      │
│  - Độ tin cậy: %                                               │
│  - Chi tiết theo tháng (JSON)                                   │
│  - Khuyến nghị AI                                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    XÁC NHẬN DỰ BÁO                              │
│  → Lưu làm tham khảo cho quyết định                            │
│  → Trạng thái: CONFIRMED                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 LIÊN KẾT GIỮA CÁC MODULE

### Sơ đồ liên kết dữ liệu

```
                        ┌─────────────┐
                        │   NHÂN SỰ   │
                        │  (nhan_su)  │
                        └──────┬──────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │  TÀI SẢN    │     │  NGÂN SÁCH  │     │  THU CHI    │
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                   │
           │    ┌──────────────┼──────────────┐    │
           │    │              │              │    │
           ▼    ▼              ▼              ▼    ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ Phân bổ TS  │────►│ Phân bổ NS  │◄────│ Phiếu chi   │
    └─────────────┘     └─────────────┘     └─────────────┘
           │                   │                   │
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ Thanh lý TS │────►│ Theo dõi TH │◄────│ Phiếu thu   │
    └─────────────┘     └─────────────┘     └─────────────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   KẾ TOÁN TÀI SẢN   │
                    │    & DỰ BÁO AI      │
                    │                     │
                    │  📊 Dashboard       │
                    │  📈 Dự báo          │
                    │  📋 Báo cáo         │
                    └─────────────────────┘
```

### Các điểm liên kết quan trọng

| Từ Module | Đến Module | Liên kết | Mục đích |
|-----------|------------|----------|----------|
| Thu chi | Tài sản | `thanh_ly_id` | Thu tiền thanh lý tài sản |
| Thu chi | Ngân sách | `ngan_sach_id`, `phan_bo_id` | Theo dõi chi tiêu theo ngân sách |
| Thu chi | Nhân sự | `nguoi_duyet_nhansu_id` | Người duyệt từ nhân sự (is_lanh_dao) |
| Ngân sách | Nhân sự | `nguoi_duyet_id`, `nguoi_lap_id` | Người lập & duyệt ngân sách |
| Ngân sách | Tài sản | `danh_muc_ts_id` | Phân bổ theo danh mục tài sản |
| Tài sản | Nhân sự | `nhan_vien_su_dung_id` | Nhân viên sử dụng tài sản |
| Kế toán | Tài sản | `tai_san_id` | Tính khấu hao tài sản |
| Kế toán | Thu chi | `phieu_thu`, `phieu_chi` | Dữ liệu dự báo AI |
| Kế toán | Ngân sách | `ngan_sach`, `theo_doi` | Dữ liệu dự báo AI |

---

## 📌 QUY TẮC NGHIỆP VỤ QUAN TRỌNG

### 1. Quy tắc phân quyền duyệt
```
┌────────────────────────────────────────────────────────────────┐
│  ⚠️ CHỈ CHỦ TỊCH HOẶC GIÁM ĐỐC được duyệt:                    │
│                                                                │
│  ✅ Ngân sách                                                  │
│  ✅ Dự toán chi                                                │
│  ✅ Phiếu chi                                                  │
│  ✅ Phiếu thu                                                  │
│  ✅ Theo dõi thực hiện ngân sách                               │
│                                                                │
│  Domain áp dụng: [('is_lanh_dao', '=', True)]                 │
└────────────────────────────────────────────────────────────────┘
```

### 2. Quy tắc ràng buộc ngân sách
```
┌────────────────────────────────────────────────────────────────┐
│  ⚠️ KIỂM TRA VƯỢT NGÂN SÁCH:                                  │
│                                                                │
│  - Tổng phân bổ ≤ Tổng ngân sách                              │
│  - Số tiền chi ≤ Số tiền còn lại của phân bổ                  │
│  - Cảnh báo khi chi vượt ngân sách                            │
│                                                                │
│  vuot_ngan_sach = amount > phan_bo_id.so_tien_con_lai         │
└────────────────────────────────────────────────────────────────┘
```

### 3. Quy tắc tài sản
```
┌────────────────────────────────────────────────────────────────┐
│  ⚠️ RÀNG BUỘC TÀI SẢN:                                        │
│                                                                │
│  - Mã tài sản phải duy nhất                                    │
│  - Giá trị hiện tại ≤ Giá trị ban đầu                         │
│  - Giá trị không được âm                                       │
│  - Mỗi tài sản chỉ được thanh lý 1 lần                        │
│  - Tài sản đã thanh lý không thể mượn/luân chuyển             │
└────────────────────────────────────────────────────────────────┘
```

### 4. Quy tắc nhân sự
```
┌────────────────────────────────────────────────────────────────┐
│  ⚠️ BẮT BUỘC KHI TẠO NHÂN SỰ:                                 │
│                                                                │
│  - Mã định danh: required                                      │
│  - Họ tên: required                                            │
│  - Chức vụ: required (để xác định is_lanh_dao)                │
└────────────────────────────────────────────────────────────────┘
```

---

## 📊 BÁO CÁO VÀ DASHBOARD

### Dashboard tổng hợp tài chính (ke_toan.dashboard)

```
┌─────────────────────────────────────────────────────────────────┐
│                    📊 DASHBOARD TÀI CHÍNH                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📦 TÀI SẢN & KHẤU HAO                                         │
│  ├── Tổng số tài sản: X                                        │
│  ├── Tổng giá trị: XXX VNĐ                                     │
│  ├── Tổng khấu hao: XXX VNĐ                                    │
│  ├── Giá trị còn lại: XXX VNĐ                                  │
│  ├── Khấu hao tháng này: XXX VNĐ                               │
│  └── Khấu hao năm nay: XXX VNĐ                                 │
│                                                                 │
│  💰 THU CHI                                                     │
│  ├── Tổng thu tháng: XXX VNĐ                                   │
│  ├── Tổng chi tháng: XXX VNĐ                                   │
│  └── Cân đối tháng: XXX VNĐ                                    │
│                                                                 │
│  📋 NGÂN SÁCH                                                   │
│  ├── Tổng ngân sách: XXX VNĐ                                   │
│  ├── Đã chi: XXX VNĐ                                           │
│  └── Còn lại: XXX VNĐ                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 TỔNG HỢP LUỒNG HOẠT ĐỘNG

### Luồng mua sắm tài sản có ngân sách

```
1. [Lập ngân sách] → Duyệt (Lãnh đạo)
                          │
2. [Phân bổ ngân sách cho phòng ban/danh mục]
                          │
3. [Tạo dự toán chi] → Duyệt (Lãnh đạo)
                          │
4. [Tạo phiếu chi mua tài sản] → Xác nhận → Duyệt (Lãnh đạo) → Ghi sổ
                          │                                        │
                          │                    ┌───────────────────┘
                          │                    │
5. [Tạo tài sản mới] ◄────┘              [Trừ ngân sách]
                          │
6. [Phân bổ tài sản cho phòng ban]
                          │
7. [Sử dụng / Mượn trả / Luân chuyển]
                          │
8. [Kiểm kê định kỳ]
                          │
9. [Tính khấu hao hàng kỳ] → Ghi sổ
                          │
10. [Thanh lý khi hết giá trị] → Tạo phiếu thu (nếu bán)
```

### Luồng thu tiền công nợ

```
1. [Tạo công nợ phải thu] → Xác nhận (state: OPEN)
                                   │
2. [Khách hàng thanh toán]         │
                                   │
3. [Tạo phiếu thu công nợ] ◄───────┘
         │
4. [Xác nhận] → [Ghi sổ] (Người duyệt: Lãnh đạo)
                    │
                    ├── Cập nhật công nợ (PARTIAL hoặc PAID)
                    └── Tạo theo dõi thực hiện ngân sách (nếu có)
```

---

*Tài liệu được tạo tự động từ phân tích mã nguồn các module*
*Cập nhật: Tháng 01/2026*
