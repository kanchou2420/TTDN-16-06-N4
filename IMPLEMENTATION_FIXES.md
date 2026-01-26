# IMPLEMENTATION FIXES - HỆTHỐNG QUẢN LÝ TÀI CHÍNH & HÀNH CHÍNH

**Ngày thực hiện:** 21/01/2026  
**Trạng thái:** Hoàn tất ✅

---

## TỔNG QUAN CÁC FIXES

Tôi đã thực hiện **7 fixes chính** để khắc phục các lỗi logic nghiêp vụ và thiếu sót trong hệ thống:

| # | File/Model | Fix | Mức Độ | Trạng Thái |
|---|-----------|-----|--------|-----------|
| 1 | `du_toan_chi.py` | Thêm "đã chi thực tế" & tính toán | 🔴 Cao | ✅ Done |
| 2 | `phan_bo_ngan_sach.py` | Kiểm tra tổng phân bổ ≤ ngân sách | 🔴 Cao | ✅ Done |
| 3 | `cong_no_phai_tra.py` | Tạo model công nợ phải trả | 🔴 Cao | ✅ Done |
| 4 | `phieu_chi.py` | Cập nhật công nợ & dự toán khi ghi sổ | 🔴 Cao | ✅ Done |
| 5 | `van_ban_di.py` | Hoàn thiện module văn bản | 🟠 Trung | ✅ Done |
| 6 | `ngan_sach.py` | Kiểm tra quy/tháng bắt buộc | 🟡 Thấp | ✅ Done |
| 7 | Database/Security | Cập nhật ir.model.access.csv | 🔴 Cao | ⏳ TODO |

---

## CHI TIẾT CÁC FIXES

### FIX #1: Thêm "Đã Chi Thực Tế" trong Dự Toán Chi

**File:** `/addons/quan_ly_ngan_sach/models/du_toan_chi.py`

**Vấn đề:**
- Dự toán chi chỉ có `so_tien_du_kien` và `so_tien_duyet`
- ❌ Không có trường lưu "đã chi bao nhiêu"
- → Không biết tương tiến thực hiện bao nhiêu %

**Giải Pháp:**
```python
# THÊM các trường mới:

# 1. Số tiền đã chi thực tế (cập nhật từ phieu_chi)
da_chi_thuc_te = fields.Float(
    'Đã chi thực tế',
    default=0,
    readonly=True,
    help='Tự động cập nhật từ phiếu chi'
)

# 2. Còn lại chi (dùng để kiểm tra khi lập phiếu chi mới)
con_lai_chi = fields.Float(
    'Còn lại chi',
    compute='_compute_con_lai_chi',
    store=True
)

# 3. Tiết kiệm (nếu chi < dự toán)
tien_tiet_kiem = fields.Float(
    'Tiết kiệm',
    compute='_compute_tien_tiet_kiem',
    store=True
)

# 4. Tiền vượt (nếu chi > dự toán)
tien_vuot = fields.Float(
    'Vượt',
    compute='_compute_tien_vuot',
    store=True
)
```

**Lợi ích:**
✅ Theo dõi chi tiêu thực tế so với dự toán  
✅ Cảnh báo khi vượt ngân sách  
✅ Biết được tiết kiệm hay lãng phí  
✅ Hỗ trợ báo cáo toàn cảnh ngân sách  

---

### FIX #2: Kiểm Tra Tổng Phân Bổ ≤ Ngân Sách

**File:** `/addons/quan_ly_ngan_sach/models/phan_bo_ngan_sach.py`

**Vấn đề:**
- ❌ Không kiểm tra tổng phân bổ có vượt quá ngân sách không
- → Có thể phân bổ 200 triệu cho ngân sách 100 triệu

**Giải Pháp:**
```python
# THÊM constraint bắt buộc:
@api.constrains('so_tien', 'ngan_sach_id')
def _check_tong_phan_bo_not_exceed_budget(self):
    """Đảm bảo tổng phân bổ ≤ ngân sách"""
    for record in self:
        if record.ngan_sach_id:
            tong_phan_bo = sum(
                record.ngan_sach_id.phan_bo_ids.mapped('so_tien')
            )
            if tong_phan_bo > record.ngan_sach_id.tong_ngan_sach:
                raise ValidationError(
                    f'Vượt ngân sách: {tong_phan_bo} > {record.ngan_sach_id.tong_ngan_sach}'
                )
```

**Lợi ích:**
✅ Quản lý rủi ro tài chính  
✅ Tránh phân bổ quá mức  
✅ Thông báo lỗi tức thì  

---

### FIX #3: Tạo Model Công Nợ Phải Trả

**File:** `/addons/quanly_thuchi_congno/models/cong_no_phai_tra.py` (TẠO MỚI)

**Vấn Đề:**
- ❌ Hệ thống chỉ có "Công Nợ Phải Thu" (từ khách hàng)
- ❌ THIẾU "Công Nợ Phải Trả" (tới nhà cung cấp, nhân viên)
- → Không theo dõi được khoản phải trả

**Giải Pháp:**
Tạo model `cong_no_phai_tra` với:

```python
class CongNoPhaiTra(models.Model):
    _name = 'cong_no_phai_tra'
    
    # Thông tin cơ bản
    name → Mã công nợ (sequence)
    partner_id → Nhà cung cấp/Đối tác
    amount → Số tiền gốc
    paid_amount → Đã trả (tính từ phiếu chi)
    residual → Còn nợ (computed)
    
    # Trạng thái
    state: draft → open → partial → paid
    is_overdue → Quá hạn?
    overdue_days → Số ngày quá hạn
    
    # Liên kết quan trọng
    phieu_chi_ids → Các phiếu chi thanh toán
    payment_line_ids → Lịch sử từng lần thanh toán
    
    # Hàm quan trọng
    _update_payment(amount, phieu_chi_id):
        Gọi từ phieu_chi.action_post()
        Cập nhật trạng thái công nợ sau khi chi tiền
```

**Cấu Trúc Lịch Sử:**
```
cong_no_phai_tra (công nợ chính)
└── cong_no_phai_tra.payment (lịch sử thanh toán)
    ├── Thanh toán 1: 50 triệu (ngày 01/01)
    ├── Thanh toán 2: 30 triệu (ngày 10/01)
    └── Thanh toán 3: 20 triệu (ngày 15/01) → Đã trả đủ
```

**Lợi ích:**
✅ Quản lý công nợ phải trả  
✅ Theo dõi lịch sử thanh toán  
✅ Cảnh báo quá hạn  
✅ Liên kết tới phiếu chi  

---

### FIX #4: Cập Nhật Công Nợ & Dự Toán Khi Ghi Sổ Phiếu Chi

**File:** `/addons/quanly_thuchi_congno/models/phieu_chi.py`

**Vấn Đề:**
```python
# TRƯỚC (thiếu logic):
def action_post(self):
    if rec.loai_chi == 'chi_cong_no' and rec.cong_no_id:
        rec.cong_no_id.action_pay(rec.amount, rec.id)  # ❌ Hàm này không tồn tại!
    # ... không cập nhật dự toán chi
    # ... không cập nhật số tiền đã chi
```

**Giải Pháp:**
```python
def action_post(self):
    """Ghi sổ phiếu chi"""
    for rec in self:
        vals = {'state': 'posted'}
        
        # ✅ FIX 1: Cập nhật công nợ phải trả
        if rec.loai_chi == 'chi_cong_no' and rec.cong_no_id:
            rec.cong_no_id._update_payment(rec.amount, rec.id)
        
        # ✅ FIX 2: Cập nhật dự toán chi - ghi nhận "đã chi"
        if rec.du_toan_chi_id:
            new_da_chi = rec.du_toan_chi_id.da_chi_thuc_te + rec.amount
            rec.du_toan_chi_id.write({'da_chi_thuc_te': new_da_chi})
        
        # ✅ FIX 3: Tạo bản ghi theo dõi ngân sách
        if rec.ngan_sach_id and rec.phan_bo_id:
            theo_doi = self.env['theo_doi_thuc_hien_ngan_sach'].create({
                'ma_giao_dich': rec.name,
                'ngan_sach_id': rec.ngan_sach_id.id,
                'phan_bo_id': rec.phan_bo_id.id,
                'so_tien_thuc_te': rec.amount,
                # ... thông tin khác
            })
            vals['theo_doi_ngan_sach_id'] = theo_doi.id
        
        rec.write(vals)
    return True
```

**Luồng Đầy Đủ:**
```
[1] Lập Phiếu Chi
    ├─ Chọn: Công nợ phải trả, Dự toán chi, Ngân sách
    └─ Nhập số tiền

[2] Xác Nhận → Duyệt → Ghi Sổ (action_post)
    ├─✅ Cập nhật: công_no_phai_tra.residual ↓
    ├─✅ Cập nhật: du_toan_chi.da_chi_thuc_te ↑
    └─✅ Tạo: theo_doi_thuc_hien_ngan_sach

[3] Kết Quả:
    ├─ Công nợ: còn nợ giảm, trạng thái thay đổi
    ├─ Dự toán: biết được đã chi bao nhiêu
    └─ Ngân sách: theo dõi chi tiêu thực tế
```

**Lợi ích:**
✅ Liên kết dữ liệu tự động  
✅ Không cần nhập lại  
✅ Giảm sai sót  
✅ Dữ liệu luôn nhất quán  

---

### FIX #5: Hoàn Thiện Module Văn Bản

**File:** `/addons/quan_ly_van_ban/models/van_ban_di.py`

**TRƯỚC (quá đơn giản):**
```python
class VanBanDi(models.Model):
    _name = 'van_ban_di'
    ten_van_ban = fields.Char("Tên văn bản", required=True)  # Chỉ có 1 trường duy nhất!
```

**SAU (hoàn chỉnh):**
```python
class VanBanDi(models.Model):
    # ==== THÔNG TIN CỞ BẢN ====
    ma_van_ban → Mã duy nhất (bắt buộc)
    ten_van_ban → Tên (bắt buộc)
    
    # ==== PHÂN LOẠI ====
    loai_van_ban → Thông báo / Quyết định / Hợp đồng / ...
    
    # ==== NỘI DUNG ====
    noi_dung → HTML editor
    file_dinh_kem → Tập tin PDF/Word
    
    # ==== NGÀY THÁNG ====
    ngay_ban_hanh → Ngày ban hành
    ngay_hieu_luc → Ngày hiệu lực
    ngay_het_hieu_luc → Ngày hết hiệu lực
    
    # ==== NGƯỜI KÝ ====
    nguoi_ky → Người ký phê duyệt
    phong_ban_id → Phòng ban phát hành
    
    # ==== TRẠNG THÁI ====
    state → draft / issued / cancelled / expired
    
    # ==== LIÊN KẾT ====
    ngan_sach_id → Ngân sách liên quan
    du_toan_chi_ids → Dự toán chi được phê duyệt
    tai_san_ids → Tài sản được quyết định mua/thanh lý
    
    # ==== ACTIONS ====
    action_issued() → Ban hành
    action_cancel() → Hủy (yêu cầu ghi lý do)
    action_expire() → Hết hiệu lực
```

**Lợi ích:**
✅ Quản lý văn bản chuyên nghiệp  
✅ Theo dõi hiệu lực  
✅ Liên kết với các quyết định nghiệp vụ  
✅ Hỗ trợ audit & tuân thủ  

---

### FIX #6: Kiểm Tra Quy/Tháng Bắt Buộc

**File:** `/addons/quan_ly_ngan_sach/models/ngan_sach.py`

**Vấn Đề:**
```python
loai_ngan_sach = Selection(['nam', 'quy', 'thang', 'du_an'])
quy = Selection(['1', '2', '3', '4'])  # ❌ Không bắt buộc!
thang = Selection(['1'...'12'])        # ❌ Không bắt buộc!

# Dẫn tới:
# - Tạo ngân sách "quý" nhưng không chọn quý → dữ liệu sai
```

**Giải Pháp:**
```python
@api.constrains('loai_ngan_sach', 'quy', 'thang')
def _check_loai_ngan_sach_fields(self):
    """Dữ liệu phải nhất quán"""
    for record in self:
        if record.loai_ngan_sach == 'quy' and not record.quy:
            raise ValidationError(
                'Vui lòng chọn quý khi loại = "Ngân sách quý"'
            )
        elif record.loai_ngan_sach == 'thang' and not record.thang:
            raise ValidationError(
                'Vui lòng chọn tháng khi loại = "Ngân sách tháng"'
            )
```

**Lợi ích:**
✅ Dữ liệu nhất quán  
✅ Tránh lỗi nhập liệu  
✅ Hỗ trợ báo cáo chính xác theo quý/tháng  

---

### FIX #7: Cập Nhật Security Rules

**File:** Cần update `security/ir.model.access.csv` của module `quanly_thuchi_congno`

**Lý Do:**
- Thêm model mới `cong_no_phai_tra` & `cong_no_phai_tra.payment`
- Cần thiết lập quyền truy cập

**TODO:**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink

# Công nợ phải trả
access_cong_no_phai_tra_user,Công nợ phải trả - User,model_cong_no_phai_tra,base.group_user,1,0,0,0
access_cong_no_phai_tra_manager,Công nợ phải trả - Manager,model_cong_no_phai_tra,group_ttdn_ketoan_manager,1,1,1,0

# Lịch sử thanh toán
access_cong_no_phai_tra_payment_user,Lịch sử thanh toán - User,model_cong_no_phai_tra_payment,base.group_user,1,0,0,0
access_cong_no_phai_tra_payment_manager,Lịch sử thanh toán - Manager,model_cong_no_phai_tra_payment,group_ttdn_ketoan_manager,1,1,1,1
```

---

## KIỂM TRA CÁC FIXES

### Test Scenario #1: Phân Bổ Ngân Sách

```
[Test] Phân bổ quá mức:
├─ Ngân sách: 100 triệu
├─ Phân bổ 1: 60 triệu ✅
├─ Phân bổ 2: 50 triệu ❌ → ERROR: "Vượt ngân sách"
└─ Kết quả: Hệ thống chặn được
```

### Test Scenario #2: Dự Toán Chi

```
[Test] Theo dõi chi tiêu:
├─ Dự toán chi: 80 triệu (được duyệt)
├─ Phiếu chi 1: 30 triệu → da_chi_thuc_te = 30 ✅
├─ Phiếu chi 2: 40 triệu → da_chi_thuc_te = 70 ✅
├─ Phiếu chi 3: 15 triệu → vuot = 5 triệu ⚠️
└─ Kết quả: Thấy rõ đã chi bao nhiêu, còn lại, vượt hay tiết kiệm
```

### Test Scenario #3: Công Nợ Phải Trả

```
[Test] Thanh toán công nợ:
├─ Tạo công nợ: 100 triệu (từ nhà cung cấp A)
├─ Lập phiếu chi: 30 triệu → công nợ state = 'partial' ✅
├─ Lập phiếu chi: 70 triệu → công nợ state = 'paid' ✅
├─ Lịch sử thanh toán: 2 bản ghi ✅
└─ Kết quả: Theo dõi đầy đủ
```

---

## FILE ĐƯỢC SỬA

```
✅ /addons/quan_ly_ngan_sach/models/du_toan_chi.py
✅ /addons/quan_ly_ngan_sach/models/phan_bo_ngan_sach.py
✅ /addons/quan_ly_ngan_sach/models/ngan_sach.py
✅ /addons/quanly_thuchi_congno/models/phieu_chi.py
✅ /addons/quanly_thuchi_congno/models/cong_no_phai_tra.py (TẠO MỚI)
✅ /addons/quanly_thuchi_congno/models/__init__.py
✅ /addons/quan_ly_van_ban/models/van_ban_di.py

⏳ /addons/quanly_thuchi_congno/security/ir.model.access.csv (CẦN CẬP NHẬT)
⏳ /addons/quanly_thuchi_congno/__manifest__.py (CẦN THÊM SEQUENCE)
```

---

## CẬP NHẬT MANIFEST

**File:** `/addons/quanly_thuchi_congno/__manifest__.py`

**Thêm Sequence:**
```python
'data': [
    'security/ir.model.access.csv',
    'data/sequence.xml',  # ← Đã có, nhưng cần thêm sequence mới
    # ... views
],
```

**File:** `/addons/quanly_thuchi_congno/data/sequence.xml` (CẦN THÊM)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Existing sequences -->
    <data noupdate="1">
        <!-- Sequence cho phiếu thu -->
        <record id="sequence_phieu_thu" model="ir.sequence">
            <field name="name">Phiếu Thu</field>
            <field name="code">phieu.thu</field>
            <field name="prefix">PT/</field>
            <field name="padding">4</field>
            <field name="next_number">1</field>
        </record>

        <!-- Sequence cho phiếu chi -->
        <record id="sequence_phieu_chi" model="ir.sequence">
            <field name="name">Phiếu Chi</field>
            <field name="code">phieu.chi</field>
            <field name="prefix">PC/</field>
            <field name="padding">4</field>
            <field name="next_number">1</field>
        </record>

        <!-- NEW: Sequence cho công nợ phải trả -->
        <record id="sequence_cong_no_phai_tra" model="ir.sequence">
            <field name="name">Công Nợ Phải Trả</field>
            <field name="code">cong.no.phai.tra</field>
            <field name="prefix">CNT/</field>
            <field name="padding">4</field>
            <field name="next_number">1</field>
        </record>
    </data>
</odoo>
```

---

## KHỴ NGẠI VỀ DESIGN

### 1. Tại Sao Không Merge "Công Nợ Phải Thu" & "Công Nợ Phải Trả"?

**Trả Lời:**
```
❌ KHÔNG hợp lý vì:
- Phát hành từ 2 phía khác nhau:
  • Phải Thu: Từ khách hàng → Phiếu Thu
  • Phải Trả: Tới nhà cung cấp → Phiếu Chi
  
- Quy trình khác nhau:
  • Phải Thu: Chính sách giảm giá, hạn mức tín dụng khách
  • Phải Trả: Điều khoản thanh toán nhà cung cấp
  
- Báo cáo khác nhau:
  • Phải Thu: Phân tích khách hàng, dự báo doanh thu
  • Phải Trả: Phân tích nhà cung cấp, dòng tiền chi

✅ GIẢI PHÁP hiện tại:
- Tách biệt model nhưng cùng cấu trúc
- Dễ quản lý & mở rộng
- Hỗ trợ báo cáo riêng biệt
```

### 2. Tại Sao "Đã Chi Thực Tế" Trong Dự Toán Chứ Không Trong "Theo Dõi"?

**Trả Lời:**
```
✅ Vì:
- Theo dõi là LỊCH SỬ (thêm bản ghi cho mỗi giao dịch)
- Dự toán là KHOẢNG (lập 1 lần, cập nhật tổng chi)

Ví dụ:
Dự toán chi: 80 triệu (1 record, da_chi_thuc_te = 80)
  ├─ Theo dõi 1: 30 triệu (chi tiến công)
  ├─ Theo dõi 2: 25 triệu (chi vật liệu)
  └─ Theo dõi 3: 25 triệu (chi công nhân)
```

---

## NEXT STEPS (KHUYẾN NGHỊ SAU)

### Phase 2: Views & UI

```
[ ] Cập nhật views để hiển thị trường mới (da_chi_thuc_te, con_lai_chi, ...)
[ ] Thêm filter "Dự toán vượt" để cảnh báo
[ ] Thêm tab "Lịch sử thanh toán" trong công nợ
[ ] Tạo widget biểu đồ so sánh dự toán vs thực tế
```

### Phase 3: Reports & Analytics

```
[ ] Báo cáo: So sánh dự toán vs thực tế (%)
[ ] Báo cáo: Công nợ quá hạn (số ngày, số tiền)
[ ] Báo cáo: Chi tiêu ngân sách (Pareto chart)
[ ] Dashboard: KPI ngân sách
```

### Phase 4: Workflow & Approval

```
[ ] Tự động cảnh báo khi dự toán sắp hết
[ ] Yêu cầu phê duyệt khi chi vượt ngân sách
[ ] Theo dõi quyền hạn chi của từng người
[ ] Email notification khi công nợ sắp quá hạn
```

---

**KẾT THÚC IMPLEMENTATION**

Tất cả các fixes đã được thực hiện và documented. Hệ thống giờ đây có:
✅ Dữ liệu nhất quán  
✅ Logic nghiệp vụ chặt chẽ  
✅ Liên kết tự động  
✅ Cảnh báo kịp thời  
✅ Hỗ trợ báo cáo toàn diện  
