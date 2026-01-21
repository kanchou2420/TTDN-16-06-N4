# BÁO CÁO PHÂN TÍCH NGHIỆP VỤ - HỆ THỐNG QUẢN LÝ TÀI CHÍNH HÀ HÀNH CHÍNH

**Ngày phân tích:** 21/01/2026  
**Phiên bản:** 1.0  
**Phân tích bởi:** Business Analyst & Software Engineer  

---

## I. TỔNG QUAN HỆ THỐNG

### 1.1 Các Module Chính
```
┌─────────────────────────────────────────────────────────────────┐
│ HỆ THỐNG QUẢN LÝ TÀI CHÍNH & HÀNH CHÍNH                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Quản Lý Ngân Sách │  │Quản Lý Tài Sản   │  │Quản Lý Văn Bản│ │
│  │ (quan_ly_ngan_sach)│ (quan_ly_tai_san) │  │(quan_ly_van_ban)│ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│           ▲                      ▲                   ▲            │
│           │                      │                   │            │
│           └──────────────────────┼───────────────────┘            │
│                                  │                                │
│                   ┌──────────────┴──────────────┐                │
│                   ▼                             ▼                │
│           ┌──────────────────┐        ┌──────────────────┐      │
│           │ Thu Chi & Công Nợ│        │  Nhân Sự         │      │
│           │(quanly_thuchi_   │        │  (nhan_su)       │      │
│           │ congno)          │        │  [External]      │      │
│           └──────────────────┘        └──────────────────┘      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Mô tả Tóm Tắt

| Module | Chức Năng Chính | Trạng Thái Code |
|--------|-----------------|-----------------|
| **Quản Lý Ngân Sách** | Lập KH ngân sách, phân bổ, theo dõi thực hiện | ✅ Cấu trúc tốt |
| **Quản Lý Tài Sản** | Quản lý tài sản, khấu hao, luân chuyển, thanh lý | ✅ Chi tiết |
| **Quản Lý Văn Bản** | Quản lý văn bản đi/đến | ⚠️ Quá đơn giản |
| **Thu Chi & Công Nợ** | Phiếu thu/chi, theo dõi công nợ | ✅ Tương đối đầy đủ |

---

## II. PHÂN TÍCH CHI TIẾT TỪNG MODULE

### 2.1 MODULE: QUẢN LÝ NGÂN SÁCH (quan_ly_ngan_sach)

#### 2.1.1 Cấu Trúc Models
```
ngan_sach (Ngân Sách)
├── du_toan_chi (Dự Toán Chi)
├── phan_bo_ngan_sach (Phân Bổ Ngân Sách)
└── theo_doi_thuc_hien_ngan_sach (Theo Dõi Thực Hiện)
```

#### 2.1.2 Phân Tích Logic Chính

**✅ Điểm Tốt:**
1. Phân loại ngân sách rõ ràng (năm, quý, tháng, dự án)
2. Có ràng buộc dữ liệu (unique ma_ngan_sach, kiểm tra ngày)
3. Theo dõi người lập, người duyệt
4. Tính toán tự động: tổng phân bổ, còn lại

**⚠️ VẤN ĐỀ PHÁT HIỆN:**

| # | Vấn Đề | Mức Độ | Ảnh Hưởng |
|---|--------|--------|----------|
| 1 | Không có trường `description` để giải thích ngân sách | Thấp | Dễ hiểu sai |
| 2 | Không có số tiền chi tiết theo dự toán trong ngân sách | Cao | Không theo dõi được chi tiêu thực tế so với kế hoạch |
| 3 | Thiếu phép tính: "Đã chi thực tế" vs "Dự toán chi được duyệt" | Cao | Không biết vượt hay tiết kiệm được bao nhiêu |
| 4 | Trường `quy`, `thang` không bắt buộc khi loại_ngan_sach = 'quy'/'thang' | Cao | Dữ liệu không nhất quán |
| 5 | Không có kiểm tra: tổng phan_bo không được vượt tong_ngan_sach | Cao | Có thể phân bổ quá mức |
| 6 | Không lưu lịch sử thay đổi trạng thái (khi nào duyệt, hủy) | Trung | Khó audit |
| 7 | Không có liên kết trực tiếp tới phiếu chi để kiểm tra vượt ngân sách | Cao | Không cảnh báo khi chi vượt |

**🔴 LOGIC LỖI TRONG DỰ TOÁN CHI:**
- Dự toán chi có 2 trường tiền: `so_tien_du_kien` vs `so_tien_duyet`
- Nhưng **không có trường lưu "đã chi thực tế"** → không biết tình trạng thực hiện
- Trạng thái = 'hoan_thanh' nhưng không kiểm tra đã chi hết chưa

---

### 2.2 MODULE: QUẢN LÝ TÀI SẢN (quan_ly_tai_san)

#### 2.2.1 Cấu Trúc Models
```
tai_san (Tài Sản)
├── danh_muc_tai_san (Danh Mục)
├── phan_bo_tai_san (Phân Bổ)
├── lich_su_khau_hao (Lịch Sử Khấu Hao)
├── kich_ke_tai_san (Kiểm Kê)
├── luan_chuyen_tai_san (Luân Chuyển)
├── thanh_ly_tai_san (Thanh Lý)
└── lich_su_ky_thuat (Lịch Sử Kỹ Thuật)
```

#### 2.2.2 Phân Tích

**✅ Điểm Tốt:**
1. Chi tiết tài sản: giá trị, khấu hao, lịch sử sử dụng
2. Theo dõi nhiều khía cạnh: kỹ thuật, khấu hao, kiểm kê, luân chuyển
3. Hình ảnh & giấy tờ liên quan
4. Tính trạng thái tự động (chua_phan_bo, da_phan_bo, da_thanh_ly)

**⚠️ VẤN ĐỀ:**

| # | Vấn Đề | Mức Độ | 
|---|--------|--------|
| 1 | **THIẾU LIÊN KẾT NGÂN SÁCH:** Không lưu tài sản được mua từ dự toán/phiếu chi nào | Cao |
| 2 | **THIẾU LIÊN KẾT THU CHI:** Không liên kết phiếu chi (mua) và phiếu thu (thanh lý) | Cao |
| 3 | Khấu hao tính sai: `gia_tri_hien_tai` nhập thủ công, không tính tự động theo công thức | Cao |
| 4 | Không có trường theo dõi "tình trạng" (hoạt động, bảo dưỡng, hỏng, thanh lý) | Trung |
| 5 | Không kiểm tra: giá trị hiện tại ≥ 0 | Trung |
| 6 | `don_vi_tinh` là Char, không liên kết tới bảng danh mục | Thấp |

**🔴 BUG LOGIC:**
```python
# Dòng 55-60: Tính trạng thái nhưng logic sai
@api.depends('thanh_ly_ids', 'phong_ban_su_dung_ids')
def _compute_trang_thai_thanh_ly(self):
    # Nếu thanh_ly_ids > 0 → 'da_thanh_ly' ✅
    # Elif phong_ban_su_dung_ids > 0 → 'da_phan_bo' ✅
    # Else → 'chua_phan_bo' ❌ (nhưng tài sản mới vào kho cũng có trạng thái này)
```

---

### 2.3 MODULE: QUẢN LÝ VĂN BẢN (quan_ly_van_ban)

#### 2.3.1 Phân Tích

**🔴 VẤN ĐỀ NGHIÊM TRỌNG:**

Văn bản đi hiện tại chỉ có 1 trường: `ten_van_ban`

**Thiếu các trường quan trọng:**
- Mã văn bản (unique)
- Ngày ban hành / Ngày hiệu lực
- Người ký / Người phê duyệt
- Phòng ban liên quan / Đối tác liên quan
- Trạng thái (Nháp, Ban hành, Hủy)
- Nội dung / File đính kèm
- Phân loại văn bản (Thông báo, Quyết định, Hợp đồng, v.v)

**Thiếu liên kết:**
- ❌ Không liên kết với phòng ban / nhân viên
- ❌ Không liên kết với dự án / hoạt động
- ❌ Không liên kết với ngân sách / tài sản khi là quyết định phê duyệt

---

### 2.4 MODULE: QUẢN LÝ THU CHI & CÔNG NỢ (quanly_thuchi_congno)

#### 2.4.1 Cấu Trúc
```
phieu_thu (Phiếu Thu)
phieu_chi (Phiếu Chi)
├── cong_no_phai_thu (Công Nợ Phải Thu)
└── cong_no_phai_tra (Công Nợ Phải Trả) [Chưa thấy model này]
```

#### 2.4.2 Phân Tích Phiếu Chi

**✅ Điểm Tốt:**
1. Liên kết công nợ, ngân sách, tài sản
2. Workflow rõ ràng: draft → confirmed → approved → posted
3. Theo dõi người duyệt
4. Kiểm tra vượt ngân sách

**⚠️ VẤN ĐỀ:**

| # | Vấn Đề | Mức Độ |
|---|--------|--------|
| 1 | `loai_chi` = 'chi_cong_no' nhưng không bắt buộc có `cong_no_id` | Cao |
| 2 | Không cập nhật `cong_no_phai_tra` nếu chi trả công nợ | Cao |
| 3 | `nhan_vien_id` (từ model nhan_su) chưa có trong hệ thống | Cao |
| 4 | Khi chi mua sắm (`chi_mua_sam`), không tự động tạo tài sản | Cao |
| 5 | Không kiểm tra: nếu chi vượt ngân sách thì không cho phép (chỉ tính cảnh báo) | Trung |
| 6 | Trường `theo_doi_ngan_sach_id` readonly nhưng không có logic tạo nó | Cao |

**🔴 LOGIC THIẾU:**
```python
# Khi action_post, cần:
✅ Cập nhật cong_no_phai_tra (giảm số tiền còn nợ)
❌ Cập nhật theo_doi_thuc_hien (chi thực tế)
❌ Trừ từ ngân sách phân bổ
❌ Tạo tài sản nếu loai_chi = 'chi_mua_sam'
```

#### 2.4.3 Phân Tích Công Nợ Phải Thu

**✅ Tốt:**
1. Tính toán tự động: paid_amount, residual
2. Cảnh báo quá hạn
3. Liên kết phiếu thu

**⚠️ VẤN ĐỀ:**
1. Không có model `cong_no_phai_tra` (chỉ có phải thu)
2. Không có kiểm tra: công nợ phải trả khi chi trả

---

## III. PHÂN TÍCH QUAN HỆ GIỮA CÁC MODULE

### 3.1 Luồng Dữ Liệu Mong Đợi

```
┌─────────────────────────────────────────────────────────────────┐
│ LUỒNG NGÂN SÁCH ĐẦY ĐỦ                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 1. Lập Ngân Sách (ngan_sach)                                   │
│    ├─ Phân Bổ (phan_bo_ngan_sach)                             │
│    └─ Dự Toán Chi (du_toan_chi) - Duyệt                      │
│                                                                  │
│ 2. Lập Phiếu Chi (phieu_chi)                                   │
│    ├─ Kiểm Tra Ngân Sách (con_lai - amount ≥ 0?)            │
│    ├─ Cập Nhật Dự Toán (đã_chi ↑)                            │
│    ├─ Cập Nhật Công Nợ Phải Trả (con_no ↓) [THIẾU!]         │
│    └─ Tạo Tài Sản (nếu mua sắm) [THIẾU!]                    │
│                                                                  │
│ 3. Lập Phiếu Thu (phieu_thu)                                   │
│    ├─ Cập Nhật Công Nợ Phải Thu (con_no ↓)                  │
│    └─ Cập Nhật Theo Dõi Ngân Sách (thu thực tế ↑) [THIẾU!]  │
│                                                                  │
│ 4. Thanh Lý Tài Sản (thanh_ly_tai_san)                        │
│    ├─ Phiếu Thu (tự động từ thanh_ly)                        │
│    └─ Cập Nhật Tài Sản (trang_thai = 'da_thanh_ly')         │
│                                                                  │
│ 5. Báo Cáo & Theo Dõi                                         │
│    ├─ Theo Dõi Ngân Sách (theo_doi_thuc_hien)                │
│    ├─ So Sánh Dự Toán vs Thực Tế                             │
│    └─ Cảnh Báo Vượt Ngân Sách                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Các Lỗi Liên Kết Phát Hiện

| Lỗi | Module A | Module B | Vấn Đề |
|-----|----------|----------|--------|
| 1 | Phiếu Chi | Công Nợ Phải Trả | ❌ Không cập nhật con_no khi chi |
| 2 | Phiếu Chi | Tài Sản | ❌ Không tạo tài sản khi mua sắm |
| 3 | Phiếu Chi | Dự Toán Chi | ❌ Không cập nhật "đã chi" trong dự toán |
| 4 | Phiếu Thu | Theo Dõi Ngân Sách | ❌ Không tạo bản ghi theo dõi |
| 5 | Tài Sản | Ngân Sách | ❌ Không liên kết tài sản với phiếu chi/dự toán mua |
| 6 | Văn Bản | Tất cả | ❌ Hoàn toàn không liên kết |

---

## IV. PHÁT HIỆN LỖI LOGIC & KHÔNG NHẤT QUÁN

### 4.1 Trạng Thái (Status) Không Nhất Quán

**Vấn Đề:** Các module dùng tên trạng thái khác nhau

```python
# ngan_sach
state = ['nhap', 'duyet', 'dang_thuc_hien', 'ket_thuc', 'huy']

# phieu_chi
state = ['draft', 'confirmed', 'approved', 'posted', 'cancel']

# cong_no_phai_thu
state = ['draft', 'open', 'partial', 'paid', 'cancel']

# tai_san
trang_thai_thanh_ly = ['chua_phan_bo', 'da_phan_bo', 'chua_thanh_ly', 'da_thanh_ly']
```

**Đề Xuất:** Thống nhất convention:
```python
# Tiêu chuẩn cho tất cả
state = [
    ('draft', 'Nháp'),           # Mới tạo
    ('confirmed', 'Đã xác nhận'), # Xác nhận
    ('approved', 'Đã duyệt'),    # Quản lý duyệt
    ('posted', 'Đã ghi sổ'),     # Kế toán ghi sổ
    ('cancelled', 'Đã hủy'),     # Hủy
]
```

### 4.2 Thiếu Ràng Buộc Dữ Liệu Quan Trọng

```python
# ❌ LỖI 1: phan_bo_ngan_sach không kiểm tra tổng không vượt quá ngan_sach.tong_ngan_sach
@api.constrains('so_tien')
def _check_tong_phan_bo(self):
    # ❌ KHÔNG CÓ logic này!
    pass

# ✅ PHẢI SỬA:
@api.constrains('so_tien')
def _check_phan_bo_not_exceed_budget(self):
    for record in self:
        total = record.ngan_sach_id.tong_phan_bo
        if total > record.ngan_sach_id.tong_ngan_sach:
            raise ValidationError(
                f'Tổng phân bổ ({total}) vượt quá ngân sách ({record.ngan_sach_id.tong_ngan_sach})'
            )
```

### 4.3 Thiếu "Đã Chi Thực Tế"

Trong dự toán chi:
```python
# Hiện tại chỉ có:
so_tien_du_kien = 100,000    # Dự kiến chi
so_tien_duyet = 80,000        # Được duyệt chi

# ❌ THIẾU:
# da_chi_thuc_te = ?           # Đã chi bao nhiêu? (liên kết từ phieu_chi)
# con_lai = so_tien_duyet - da_chi_thuc_te  # Còn lại bao nhiêu?
```

**Hậu quả:** Không biết dự toán chi đã thực hiện bao nhiêu %.

---

## V. ĐỀ XUẤT GIẢI PHÁP

### 5.1 Ưu Tiên Cao (PHẢI SỬA NGAY)

#### 5.1.1 Thêm Model: `cong_no_phai_tra`

```python
class CongNoPhaiTra(models.Model):
    _name = 'cong_no_phai_tra'
    _description = 'Công nợ phải trả (nhân viên, nhà cung cấp, v.v)'
    
    name = fields.Char('Mã', default='New')
    partner_id = fields.Many2one('res.partner', required=True)
    
    amount = fields.Monetary('Số tiền gốc', required=True)
    paid_amount = fields.Monetary('Đã trả', compute='_compute_paid')
    residual = fields.Monetary('Còn nợ', compute='_compute_residual')
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('open', 'Đang nợ'),
        ('partial', 'Trả một phần'),
        ('paid', 'Đã trả đủ'),
        ('cancelled', 'Hủy'),
    ], default='draft')
    
    # Liên kết với phiếu chi
    phieu_chi_ids = fields.One2many('phieu_chi', 'cong_no_phai_tra_id')
```

#### 5.1.2 Cập Nhật `phieu_chi` Khi Ghi Sổ

```python
def action_post(self):
    """Ghi sổ phiếu chi"""
    for rec in self:
        # ✅ THÊM: Cập nhật công nợ phải trả
        if rec.loai_chi == 'chi_cong_no' and rec.cong_no_phai_tra_id:
            rec.cong_no_phai_tra_id._update_payment(rec.amount, rec.id)
        
        # ✅ THÊM: Cập nhật dự toán chi
        if rec.du_toan_chi_id:
            rec.du_toan_chi_id.write({
                'da_chi_thuc_te': rec.du_toan_chi_id.da_chi_thuc_te + rec.amount
            })
        
        # ✅ THÊM: Tạo tài sản nếu mua sắm
        if rec.loai_chi == 'chi_mua_sam':
            self._create_tai_san_from_purchase(rec)
```

#### 5.1.3 Thêm "Đã Chi" trong Dự Toán Chi

```python
# Trong du_toan_chi.py
da_chi_thuc_te = fields.Monetary('Đã chi thực tế', default=0)
con_lai_chi = fields.Monetary('Còn lại chi', compute='_compute_con_lai_chi')

@api.depends('so_tien_duyet', 'da_chi_thuc_te')
def _compute_con_lai_chi(self):
    for rec in self:
        rec.con_lai_chi = rec.so_tien_duyet - rec.da_chi_thuc_te
```

### 5.2 Ưu Tiên Trung (NÊN SỬA)

#### 5.2.1 Hoàn Thiện Module Văn Bản

```python
# quan_ly_van_ban/models/van_ban_di.py

class VanBanDi(models.Model):
    _name = 'van_ban_di'
    _description = 'Văn bản đi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_ban_hanh desc'
    
    ma_van_ban = fields.Char('Mã', required=True, unique=True)
    ten_van_ban = fields.Char('Tên', required=True)
    
    # Thêm các trường thiếu
    loai_van_ban = fields.Selection([
        ('thong_bao', 'Thông báo'),
        ('quyet_dinh', 'Quyết định'),
        ('hop_dong', 'Hợp đồng'),
        ('thoathuan', 'Thỏa thuận'),
        ('chi_thi', 'Chỉ thị'),
        ('khac', 'Khác'),
    ], required=True)
    
    noi_dung = fields.Html('Nội dung')
    file_dinh_kem = fields.Binary('File', attachment=True)
    
    ngay_ban_hanh = fields.Date('Ngày ban hành', required=True)
    ngay_hieu_luc = fields.Date('Ngày hiệu lực')
    
    nguoi_ky = fields.Many2one('res.users', 'Người ký')
    phong_ban_id = fields.Many2one('phong_ban', 'Phòng ban phát hành')
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('issued', 'Đã ban hành'),
        ('cancelled', 'Đã hủy'),
    ], default='draft')
    
    # Liên kết với ngân sách, tài sản nếu cần
    ngan_sach_id = fields.Many2one('ngan_sach', 'Ngân sách liên quan')
    tai_san_ids = fields.Many2many('tai_san', 'Tài sản liên quan')
```

#### 5.2.2 Thống Nhất Tên Trạng Thái

Thay tất cả `trang_thai` → `state` và dùng convention duy nhất.

### 5.3 Ưu Tiên Thấp (CÓ THỂ ĐỢ)

1. Tối ưu hóa báo cáo (dashboard)
2. Thêm lịch sử thay đổi trạng thái (audit log)
3. Thêm phê duyệt nhiều cấp

---

## VI. DANH SÁCH ISSUES & FIXES

### Issue #1: Không Cập Nhật Công Nợ Khi Chi

**File:** `quanly_thuchi_congno/models/phieu_chi.py`

**Dòng:** action_post()

**Sửa:**
```python
def action_post(self):
    for rec in self:
        # ... code cũ ...
        
        # THÊM: Cập nhật công nợ phải trả
        if rec.loai_chi == 'chi_cong_no' and rec.cong_no_phai_tra_id:
            cong_no = rec.cong_no_phai_tra_id
            cong_no._update_payment(rec.amount, rec.name)
            
            # Cập nhật trạng thái công nợ
            if cong_no.residual <= 0:
                cong_no.state = 'paid'
            elif cong_no.residual < cong_no.amount:
                cong_no.state = 'partial'
```

---

## VII. TÓMMỨC YẾU TỐ CHÍNH CẦN CẢI THIỆN

| Yếu Tố | Trạng Thái | Mức Độ Nghiêm Trọng |
|--------|-----------|-------------------|
| Liên kết Phiếu Chi ↔ Công Nợ Phải Trả | ❌ Chưa có | 🔴 Cao |
| Liên kết Phiếu Chi ↔ Tạo Tài Sản | ❌ Chưa có | 🔴 Cao |
| Liên kết Dự Toán ↔ Thực Tế Chi | ❌ Chưa có | 🔴 Cao |
| Kiểm Tra Tổng Phân Bổ ≤ Ngân Sách | ❌ Chưa có | 🟠 Trung |
| Module Văn Bản Quá Đơn Giản | ⚠️ Cơ Bản | 🟠 Trung |
| Thống Nhất Tên Trạng Thái | ❌ Chưa có | 🟡 Thấp |

---

## VIII. KHUYẾN NGHỊ VỀ QUI TRÌNH

### Chu Kỳ Sinh Dữ Liệu - YÊU CẦU THỰC HIỆN ĐẦY ĐỦ

```
[1] Lập Ngân Sách
    ↓
[2] Phân Bổ Ngân Sách & Dự Toán Chi → Duyệt
    ↓
[3] Lập Phiếu Chi
    ├─→ KIỂM TRA: còn_lai_chi - amount ≥ 0?
    ├─→ KIỂM TRA: con_lai_ngan_sach - amount ≥ 0?
    ├─→ Nếu mua sắm: Tạo bản ghi Tài Sản
    └─→ Xác Nhận → Duyệt → Ghi Sổ
        └─→ CẬP NHẬT: du_toan_chi.da_chi_thuc_te ↑
        └─→ CẬP NHẬT: cong_no_phai_tra.residual ↓
        └─→ CẬP NHẬT: theo_doi_thuc_hien_ngan_sach
    ↓
[4] Lập Phiếu Thu (từ Công Nợ Phải Thu hoặc Thanh Lý)
    ├─→ Xác Nhận → Ghi Sổ
    └─→ CẬP NHẬT: cong_no_phai_thu.residual ↓
    └─→ CẬP NHẬT: theo_doi_thuc_hien_ngan_sach
    ↓
[5] Báo Cáo
    ├─ So sánh Dự Toán vs Thực Tế
    ├─ Cảnh báo Vượt Ngân Sách
    ├─ Công Nợ Quá Hạn
    └─ Tình Trạng Tài Sản
```

---

**KẾT THÚC BÁO CÁO**
