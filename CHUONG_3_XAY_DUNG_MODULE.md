# CHƯƠNG 3: XÂY DỰNG MODULE QUẢN LÝ TÀI SẢN VÀ CÁC MODULE QUẢN LÝ TÀI CHÍNH KẾ TOÁN

## 3.1. Thiết lập cấu trúc Module

### 3.1.1. Tổng quan kiến trúc hệ thống

Hệ thống được xây dựng trên nền tảng **Odoo 15 Community Edition**, bao gồm các module custom sau:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HỆ THỐNG QUẢN LÝ TÀI SẢN & TÀI CHÍNH              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────┐   ┌──────────────────┐   ┌──────────────────────────┐  │
│   │    nhan_su    │   │  quan_ly_tai_san │   │   quan_ly_ngan_sach      │  │
│   │   (Nhân sự)   │   │    (Tài sản)     │   │      (Ngân sách)         │  │
│   └───────┬───────┘   └────────┬─────────┘   └────────────┬─────────────┘  │
│           │                    │                          │                │
│           └────────────────────┼──────────────────────────┘                │
│                                │                                           │
│                    ┌───────────┴───────────┐                               │
│                    │ quanly_thuchi_congno  │                               │
│                    │    (Thu Chi Công Nợ)  │                               │
│                    └───────────┬───────────┘                               │
│                                │                                           │
│                    ┌───────────┴───────────┐                               │
│                    │   ke_toan_tai_san     │                               │
│                    │ (Kế Toán & Dự Báo AI) │                               │
│                    └───────────────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1.2. Khởi tạo Module Custom

#### A. Cấu trúc thư mục Module

Mỗi module Odoo custom tuân theo cấu trúc thư mục chuẩn:

```
quan_ly_tai_san/
├── __init__.py              # File khởi tạo module
├── __manifest__.py          # File khai báo metadata
├── controllers/             # Xử lý HTTP requests
│   └── __init__.py
├── models/                  # Định nghĩa Models (Business Logic)
│   ├── __init__.py
│   ├── tai_san.py
│   ├── lich_su_khau_hao.py
│   ├── phan_bo_tai_san.py
│   └── ...
├── views/                   # Giao diện XML/QWeb
│   ├── tai_san.xml
│   ├── menu.xml
│   └── ...
├── security/                # Phân quyền truy cập
│   └── ir.model.access.csv
├── static/                  # Tài nguyên tĩnh (CSS, JS, Images)
│   └── src/
│       ├── css/
│       └── js/
└── demo/                    # Dữ liệu demo
    └── demo.xml
```

#### B. File `__init__.py` - Khởi tạo Module

**Mục đích**: Import các thành phần của module để Odoo nhận diện.

**File gốc `/quan_ly_tai_san/__init__.py`:**
```python
# -*- coding: utf-8 -*-

from . import controllers
from . import models
```

**File `/quan_ly_tai_san/models/__init__.py`:**
```python
# -*- coding: utf-8 -*-
from . import danh_muc_tai_san, tai_san, phan_bo_tai_san, lich_su_ky_thuat
from . import lich_su_khau_hao
from . import muon_tra_tai_san, muon_tra_tai_san_line, don_muon_tai_san, don_muon_tai_san_line
from . import thanh_ly_tai_san
from . import kiem_ke_tai_san_line, kiem_ke_tai_san, luan_chuyen_tai_san_line, luan_chuyen_tai_san
from . import dashboard
```

#### C. File `__manifest__.py` - Khai báo Metadata

**Mục đích**: Khai báo thông tin module, dependencies, data files.

**Module quan_ly_tai_san:**
```python
# -*- coding: utf-8 -*-
{
    'name': "quan_ly_tai_san",
    'summary': "Quản lý tài sản của Doanh Nghiệp",
    'description': """
        Quản lý tài sản của Doanh Nghiệp
    """,
    'author': "Nguyễn Ngọc Đan Trường - 1504",
    'website': "http://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '0.1',
    'license': 'LGPL-3',

    # Dependencies - Các module phụ thuộc
    'depends': ['base', 'web', 'nhan_su'],

    # Data files - Các file dữ liệu được load
    'data': [
        'security/ir.model.access.csv',
        'views/danh_muc_tai_san.xml',
        'views/kiem_ke_tai_san.xml',
        'views/lich_su_khau_hao.xml',
        'views/luan_chuyen_tai_san.xml',
        'views/don_muon_tai_san.xml',
        'views/muon_tra_tai_san.xml',
        'views/phan_bo_tai_san.xml',
        'views/tai_san.xml',
        'views/thanh_ly_tai_san.xml',
        'views/dashboard_overview.xml',
        'views/dashboard_borrowing.xml',
        'views/menu.xml',
    ],
    
    # Assets - Tài nguyên frontend
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js',
            'quan_ly_tai_san/static/src/css/dashboard.css',
            'quan_ly_tai_san/static/src/js/dashboard_overview.js',
        ],
    },
}
```

### 3.1.3. Khai báo thư viện phụ thuộc (Dependencies)

Các module được thiết kế với chuỗi phụ thuộc rõ ràng:

| Module | Dependencies | Mô tả |
|--------|--------------|-------|
| **nhan_su** | `base`, `web` | Module nền tảng quản lý nhân sự |
| **quan_ly_tai_san** | `base`, `web`, `nhan_su` | Quản lý tài sản, phụ thuộc nhân sự |
| **quan_ly_ngan_sach** | `base`, `web`, `mail`, `quan_ly_tai_san`, `nhan_su` | Quản lý ngân sách |
| **quanly_thuchi_congno** | `base`, `mail`, `quan_ly_ngan_sach`, `quan_ly_tai_san`, `nhan_su` | Thu chi công nợ |
| **ke_toan_tai_san** | `base`, `web`, `mail`, `quan_ly_tai_san`, `quan_ly_ngan_sach`, `quanly_thuchi_congno` | Kế toán & Dự báo AI |

**Lưu ý quan trọng**: Module `ke_toan_tai_san` được thiết kế **ĐỘC LẬP** với module `account` của Odoo, tránh cài đặt hệ thống kế toán phức tạp không cần thiết.

---

## 3.2. Lập trình Backend (Python)

### 3.2.1. Định nghĩa Models cho Tài sản

#### A. Model `tai_san` - Quản lý thông tin tài sản

**File: `/quan_ly_tai_san/models/tai_san.py`**

```python
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime

class TaiSan(models.Model):
    _name = 'tai_san'
    _description = 'Bảng chứa thông tin tài sản'
    _rec_name = 'cus_rec_name'
    _order = 'ngay_mua_ts desc'
    _sql_constraints = [
        ("ma_tai_san_unique", "unique(ma_tai_san)", "Mã tài sản đã tồn tại !"),
    ]

    # ===== THÔNG TIN CƠ BẢN =====
    ma_tai_san = fields.Char('Mã tài sản', required=True)
    ten_tai_san = fields.Char('Tên tài sản', required=True)
    ngay_mua_ts = fields.Date('Ngày mua tài sản', required=True)
    
    don_vi_tien_te = fields.Selection([
        ('vnd', 'VNĐ'),
        ('usd', '$'),
    ], string='Đơn vị tiền tệ', default='vnd', required=True)
    
    gia_tri_ban_dau = fields.Float('Giá trị ban đầu', default=1, required=True)
    gia_tri_hien_tai = fields.Float('Giá trị hiện tại', default=1, required=True)
    
    danh_muc_ts_id = fields.Many2one('danh_muc_tai_san', string='Loại tài sản', 
                                      required=True, ondelete='restrict')
    
    giay_to_tai_san = fields.Binary('Giấy tờ liên quan', attachment=True)
    hinh_anh = fields.Image('Hình ảnh', max_width=200, max_height=200)

    # ===== CẤU HÌNH KHẤU HAO =====
    pp_khau_hao = fields.Selection([
        ('straight-line', 'Tuyến tính'),
        ('degressive', 'Giảm dần'),
        ('none', 'Không')
    ], string='Phương pháp khấu hao', default='none', required=True)
    
    thoi_gian_su_dung = fields.Integer('Thời gian đã sử dụng (năm)', default=0)
    thoi_gian_toi_da = fields.Integer('Thời gian sử dụng còn lại tối đa (năm)', default=5)
    ty_le_khau_hao = fields.Float('Tỷ lệ khấu hao (%)', default=20)

    # ===== COMPUTED FIELDS =====
    cus_rec_name = fields.Char(compute='_compute_cus_rec_name', store=True)
    
    trang_thai_thanh_ly = fields.Selection([
        ('chua_phan_bo', 'Chưa phân bổ'),
        ('da_phan_bo', 'Đã phân bổ'),
        ('da_thanh_ly', 'Đã thanh lý'),
    ], string='Trạng thái', compute='_compute_trang_thai_thanh_ly', store=True)

    # ===== RELATIONS =====
    phong_ban_su_dung_ids = fields.One2many('phan_bo_tai_san', 'tai_san_id', 
                                             string='Phòng ban sử dụng')
    lich_su_khau_hao_ids = fields.One2many('lich_su_khau_hao', 'ma_ts', 
                                            string='Lịch sử khấu hao')
    thanh_ly_ids = fields.One2many('thanh_ly_tai_san', 'tai_san_id', 
                                    string='Lịch sử thanh lý')
```

**Giải thích các thành phần:**

| Thành phần | Mô tả |
|------------|-------|
| `_name` | Tên kỹ thuật của model, dùng để tham chiếu |
| `_description` | Mô tả hiển thị cho người dùng |
| `_rec_name` | Field dùng làm tên hiển thị của record |
| `_order` | Thứ tự sắp xếp mặc định |
| `_sql_constraints` | Ràng buộc ở cấp database (unique, check) |

#### B. Các loại Fields trong Odoo

```python
# Scalar Fields - Trường đơn giá trị
ma_tai_san = fields.Char('Mã tài sản', required=True)           # Chuỗi
gia_tri_ban_dau = fields.Float('Giá trị ban đầu', default=1)    # Số thực
thoi_gian_su_dung = fields.Integer('Thời gian sử dụng', default=0)  # Số nguyên
ngay_mua_ts = fields.Date('Ngày mua', required=True)            # Ngày
ngay_tao = fields.Datetime('Ngày tạo', default=fields.Datetime.now)  # Datetime
ghi_chu = fields.Text('Ghi chú')                                 # Text dài
active = fields.Boolean('Kích hoạt', default=True)              # Boolean

# Selection Field - Trường lựa chọn
pp_khau_hao = fields.Selection([
    ('straight-line', 'Tuyến tính'),
    ('degressive', 'Giảm dần'),
    ('none', 'Không')
], string='Phương pháp khấu hao', default='none')

# Binary Fields - Trường nhị phân
giay_to_tai_san = fields.Binary('Giấy tờ', attachment=True)
hinh_anh = fields.Image('Hình ảnh', max_width=200, max_height=200)

# Relational Fields - Trường quan hệ
danh_muc_ts_id = fields.Many2one('danh_muc_tai_san', string='Loại tài sản')  # N-1
lich_su_khau_hao_ids = fields.One2many('lich_su_khau_hao', 'ma_ts', string='Lịch sử')  # 1-N
luan_chuyen_ids = fields.Many2many('luan_chuyen_tai_san', string='Luân chuyển')  # N-N

# Computed Fields - Trường tính toán
trang_thai = fields.Selection(..., compute='_compute_trang_thai', store=True)
```

### 3.2.2. Viết các hàm logic tính toán khấu hao

#### A. Hàm tính toán giá trị còn lại

```python
@api.depends('thanh_ly_ids', 'phong_ban_su_dung_ids')
def _compute_trang_thai_thanh_ly(self):
    """
    Tự động tính toán trạng thái tài sản dựa trên:
    - Đã có thanh lý chưa
    - Đã được phân bổ cho phòng ban chưa
    """
    for record in self:
        if record.thanh_ly_ids:
            record.trang_thai_thanh_ly = 'da_thanh_ly'
        elif record.phong_ban_su_dung_ids:
            record.trang_thai_thanh_ly = 'da_phan_bo'
        else:
            record.trang_thai_thanh_ly = 'chua_phan_bo'
```

**Giải thích decorator `@api.depends`:**
- Khai báo các field mà computed field phụ thuộc
- Khi các field này thay đổi, hàm tính toán sẽ được gọi lại
- `store=True`: Lưu giá trị vào database thay vì tính toán mỗi lần truy vấn

#### B. Hàm tính khấu hao tự động

```python
def action_tinh_khau_hao(self):
    """
    Tính khấu hao tự động cho tài sản
    Hỗ trợ 2 phương pháp:
    1. Tuyến tính (straight-line): Khấu hao đều theo năm
    2. Giảm dần (degressive): Khấu hao theo tỷ lệ % của giá trị còn lại
    """
    for record in self:
        # Kiểm tra điều kiện
        if record.gia_tri_hien_tai <= 0:
            raise ValidationError("Giá trị hiện tại phải lớn hơn 0!")
        if record.pp_khau_hao == 'none':
            raise ValidationError("Tài sản này không có phương pháp khấu hao!")

        so_tien_khau_hao = 0

        # Phương pháp tuyến tính: Khấu hao = Giá trị ban đầu / Số năm sử dụng
        if record.pp_khau_hao == 'straight-line':
            if record.thoi_gian_toi_da <= 0:
                raise ValidationError("Thời gian sử dụng tối đa phải > 0!")
            so_tien_khau_hao = record.gia_tri_ban_dau / record.thoi_gian_toi_da

        # Phương pháp giảm dần: Khấu hao = Giá trị hiện tại × Tỷ lệ %
        elif record.pp_khau_hao == 'degressive':
            if record.ty_le_khau_hao <= 0 or record.ty_le_khau_hao >= 100:
                raise ValidationError("Tỷ lệ khấu hao phải trong khoảng (0, 100)!")
            so_tien_khau_hao = record.gia_tri_hien_tai * (record.ty_le_khau_hao / 100)

        # Đảm bảo không khấu hao vượt quá giá trị còn lại
        so_tien_khau_hao = min(so_tien_khau_hao, record.gia_tri_hien_tai)
        
        # Tạo mã phiếu khấu hao duy nhất
        ma_phieu = 'KH-' + record.ma_tai_san + '-' + datetime.now().strftime('%Y%m%d%H%M%S')

        # Tạo bản ghi lịch sử khấu hao
        self.env['lich_su_khau_hao'].create({
            'ma_phieu_khau_hao': ma_phieu,
            'ma_ts': record.id,
            'ngay_khau_hao': fields.Datetime.now(),
            'so_tien_khau_hao': so_tien_khau_hao,
            'gia_tri_con_lai': record.gia_tri_hien_tai,
            'loai_phieu': 'automatic',
            'ghi_chu': f'Khấu hao tự động {fields.Date.today().strftime("%Y/%m")}'
        })

        # Cập nhật thời gian sử dụng
        record.thoi_gian_su_dung += 1

        # Gửi thông báo thành công
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'simple_notification',
            {
                'title': 'Thành công',
                'message': f'Khấu hao tài sản "{record.ten_tai_san}" thành công!',
                'type': 'success'
            }
        )
```

**Công thức khấu hao:**

| Phương pháp | Công thức | Đặc điểm |
|-------------|-----------|----------|
| **Tuyến tính** | `Khấu hao = Giá trị ban đầu / Số năm sử dụng` | Khấu hao đều mỗi năm |
| **Giảm dần** | `Khấu hao = Giá trị hiện tại × Tỷ lệ %` | Khấu hao nhiều đầu, giảm dần |

#### C. Model Lịch sử khấu hao với auto-update

```python
class LichSuKhauHao(models.Model):
    _name = 'lich_su_khau_hao'
    _description = 'Lịch sử khấu hao'
    _order = 'ngay_khau_hao desc'
    
    ma_phieu_khau_hao = fields.Char('Mã phiếu', required=True)
    ma_ts = fields.Many2one('tai_san', string='Tài sản', required=True, ondelete='cascade')
    ngay_khau_hao = fields.Datetime('Ngày khấu hao', default=fields.Datetime.now, required=True)
    so_tien_khau_hao = fields.Float('Số tiền khấu hao', required=True, default=0)
    gia_tri_con_lai = fields.Float('Giá trị còn lại', store=True)
    
    loai_phieu = fields.Selection([
        ('automatic', 'Tự động'),
        ('manual', 'Thủ công')
    ], string='Phương thức', required=True)
    
    @api.model
    def create(self, vals):
        """
        Override create để tự động cập nhật giá trị hiện tại của tài sản
        khi tạo bản ghi khấu hao mới
        """
        tai_san = self.env['tai_san'].browse(vals.get('ma_ts'))
        if tai_san:
            so_tien = vals.get('so_tien_khau_hao', 0)
            
            if tai_san.gia_tri_hien_tai == 0:
                raise ValidationError("Tài sản đã hết giá trị, không thể khấu hao!")
            
            # Đảm bảo không khấu hao vượt quá giá trị còn lại
            if so_tien > tai_san.gia_tri_hien_tai:
                so_tien = tai_san.gia_tri_hien_tai
            
            # Cập nhật giá trị hiện tại của tài sản
            tai_san.gia_tri_hien_tai = max(0, tai_san.gia_tri_hien_tai - so_tien)
            
            # Lưu giá trị còn lại sau khấu hao
            vals['gia_tri_con_lai'] = tai_san.gia_tri_hien_tai
            
        return super().create(vals)
```

### 3.2.3. Module Kế toán Tài sản - Bút toán nội bộ

#### A. Model Khấu hao Tài sản (ke_toan_tai_san)

```python
class KhauHaoTaiSan(models.Model):
    _name = 'khau_hao_tai_san'
    _description = 'Khấu hao tài sản - Ghi nhận nội bộ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    ma_khau_hao = fields.Char('Mã khấu hao', readonly=True)
    tai_san_id = fields.Many2one('tai_san', 'Tài sản', required=True, ondelete='cascade')
    ngay_khau_hao = fields.Date('Ngày khấu hao', required=True, default=fields.Date.today)
    
    # Giá trị
    gia_tri_ban_dau = fields.Float('Giá trị ban đầu', related='tai_san_id.gia_tri_ban_dau', store=True)
    gia_tri_con_lai = fields.Float('Giá trị còn lại trước khấu hao', required=True)
    so_tien_khau_hao = fields.Float('Số tiền khấu hao', required=True)
    gia_tri_sau_khau_hao = fields.Float('Giá trị sau khấu hao', compute='_compute_gia_tri_sau', store=True)
    
    # Bút toán nội bộ (KHÔNG dùng account.move)
    but_toan_id = fields.Many2one('but_toan_khau_hao', 'Bút toán khấu hao', readonly=True)
    
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('posted', 'Ghi sổ'),
        ('cancelled', 'Hủy'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    @api.depends('gia_tri_con_lai', 'so_tien_khau_hao')
    def _compute_gia_tri_sau(self):
        for record in self:
            record.gia_tri_sau_khau_hao = max(0, record.gia_tri_con_lai - record.so_tien_khau_hao)
```

#### B. Model Bút toán Khấu hao (Ghi sổ kép)

```python
class ButToanKhauHao(models.Model):
    _name = 'but_toan_khau_hao'
    _description = 'Bút toán khấu hao - Sổ nội bộ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    ma_but_toan = fields.Char('Mã bút toán', required=True)
    ngay_ghi_so = fields.Date('Ngày ghi sổ', required=True, default=fields.Date.today)
    
    khau_hao_id = fields.Many2one('khau_hao_tai_san', 'Khấu hao', ondelete='cascade')
    tai_san_id = fields.Many2one('tai_san', 'Tài sản', required=True)
    
    # Thông tin bút toán kép
    tai_khoan_no = fields.Char('TK Nợ (Chi phí)', required=True,
                                help='Tài khoản chi phí khấu hao - VD: 6274')
    tai_khoan_co = fields.Char('TK Có (Khấu hao lũy kế)', required=True,
                                help='Tài khoản khấu hao lũy kế - VD: 2141')
    so_tien = fields.Float('Số tiền', required=True)
    
    dien_giai = fields.Text('Diễn giải')
    
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('posted', 'Đã ghi sổ'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', tracking=True)
```

**Nguyên tắc ghi sổ kép:**
```
Nợ TK 6274 (Chi phí khấu hao)     xxx
    Có TK 2141 (Khấu hao lũy kế)       xxx
```

#### C. Hàm ghi sổ khấu hao

```python
def action_post_journal(self):
    """Ghi sổ khấu hao nội bộ"""
    for record in self:
        if record.but_toan_id:
            raise ValidationError("Bút toán đã được ghi sổ!")
        
        tai_san = record.tai_san_id
        
        # Lấy cấu hình tài khoản khấu hao theo loại tài sản
        tai_khoan_config = self.env['tai_khoan_khau_hao'].search([
            ('loai_tai_san_id', '=', tai_san.danh_muc_ts_id.id)
        ], limit=1)
        
        if not tai_khoan_config:
            raise ValidationError(
                f"Chưa cấu hình tài khoản khấu hao cho loại tài sản "
                f"'{tai_san.danh_muc_ts_id.ten_danh_muc_ts}'"
            )
        
        # Tạo bút toán khấu hao nội bộ
        but_toan = self.env['but_toan_khau_hao'].create({
            'ma_but_toan': f"BT-{record.ma_khau_hao}",
            'ngay_ghi_so': record.ngay_khau_hao,
            'khau_hao_id': record.id,
            'tai_san_id': tai_san.id,
            'tai_khoan_no': tai_khoan_config.ma_tk_chi_phi,      # 6274
            'tai_khoan_co': tai_khoan_config.ma_tk_khau_hao_luy_ke,  # 2141
            'so_tien': record.so_tien_khau_hao,
            'dien_giai': f"Khấu hao {tai_san.ten_tai_san} ({record.ma_khau_hao})",
            'trang_thai': 'posted',
        })
        
        record.but_toan_id = but_toan.id
        record.trang_thai = 'posted'
        
        # Cập nhật giá trị tài sản
        tai_san.gia_tri_hien_tai = record.gia_tri_sau_khau_hao
```

### 3.2.4. Constraints và Validations

```python
@api.constrains('gia_tri_ban_dau', 'gia_tri_hien_tai')
def _check_gia_tri(self):
    """
    Kiểm tra ràng buộc giá trị tài sản:
    - Giá trị không được âm
    - Giá trị hiện tại không được lớn hơn giá trị ban đầu
    """
    for record in self:
        if record.gia_tri_ban_dau < 0 or record.gia_tri_hien_tai < 0:
            raise ValidationError("Giá trị (ban đầu, hiện tại) không thể âm!")
        elif record.gia_tri_hien_tai > record.gia_tri_ban_dau:
            raise ValidationError("Giá trị hiện tại không thể lớn hơn giá trị ban đầu!")
```

---

## 3.3. Thiết kế giao diện (XML/QWeb)

### 3.3.1. Xây dựng Tree View (Danh sách)

**File: `/quan_ly_tai_san/views/tai_san.xml`**

```xml
<!-- Tree view - Hiển thị danh sách tài sản -->
<record id="tai_san_view_tree" model="ir.ui.view">
    <field name="name">tai_san.view.tree</field>
    <field name="model">tai_san</field>
    <field name="arch" type="xml">
        <tree string="Danh sách tài sản">
            <field name="ma_tai_san"/>
            <field name="ten_tai_san"/>
            <field name="danh_muc_ts_id"/>
            <field name="gia_tri_hien_tai"/>
            <field name="trang_thai_thanh_ly"/>
            <field name="ghi_chu"/>
        </tree>
    </field>
</record>
```

**Các thuộc tính Tree View:**

| Thuộc tính | Mô tả |
|------------|-------|
| `string` | Tiêu đề của view |
| `editable="bottom/top"` | Cho phép edit trực tiếp trong danh sách |
| `decoration-xxx` | Tô màu hàng theo điều kiện |
| `default_order` | Thứ tự sắp xếp mặc định |

### 3.3.2. Xây dựng Form View (Chi tiết)

```xml
<!-- Form view - Chi tiết tài sản -->
<record id="tai_san_view_form" model="ir.ui.view">
    <field name="name">tai_san.view.form</field>
    <field name="model">tai_san</field>
    <field name="arch" type="xml">
        <form string="Tài sản">
            <sheet>
                <!-- Nhóm thông tin chung -->
                <group>
                    <group string="Thông tin chung">
                        <field name="ma_tai_san"/>
                        <field name="ten_tai_san"/>
                        <field name="ngay_mua_ts"/>
                        <field name="danh_muc_ts_id"/>
                        <field name="trang_thai_thanh_ly"/>
                    </group>
                    <group string="Hình ảnh TS">
                        <field name="hinh_anh" widget="image" nolabel="1"/>
                    </group>
                </group>
                
                <!-- Nhóm khấu hao -->
                <group>
                    <group string="Phương pháp Khấu hao">
                        <field name="pp_khau_hao"/>
                        <field name="thoi_gian_su_dung"/>
                        
                        <!-- Hiển thị có điều kiện với attrs -->
                        <field name="thoi_gian_toi_da" 
                            attrs="{'invisible': ['|', 
                                ('pp_khau_hao','=','none'), 
                                ('pp_khau_hao','=','degressive')]}"/>
                        <field name="ty_le_khau_hao" 
                            attrs="{'invisible': ['|', 
                                ('pp_khau_hao','=','none'), 
                                ('pp_khau_hao','=','straight-line')]}"/>
                        
                        <!-- Button gọi hàm Python -->
                        <button name="action_tinh_khau_hao"
                            attrs="{'invisible': ['|', 
                                ('pp_khau_hao','=','none'), 
                                ('id','=',False)]}"
                            string="Tính khấu hao tự động cho 01 năm"
                            type="object"
                            class="btn-primary w-100 mt-3"/>
                    </group>
                    <group string="Giấy tờ liên quan">
                        <field name="giay_to_tai_san" filename="giay_to_tai_san_filename"/>
                    </group>
                </group>
                
                <!-- Giá trị tài sản -->
                <group string="Cấu hình tài sản">
                    <group>
                        <field name="gia_tri_ban_dau"/>
                        <field name="don_vi_tien_te"/>
                    </group>
                    <group>
                        <field name="gia_tri_hien_tai"/>
                        <field name="don_vi_tinh"/>
                        <field name="ghi_chu"/>
                    </group>
                </group>
                
                <!-- Notebook chứa các tab -->
                <notebook>
                    <page name="pbsd" string="Phòng ban sử dụng">
                        <field name="phong_ban_su_dung_ids" readonly="True">
                            <tree>
                                <field name="phong_ban_id"/>
                                <field name="trang_thai"/>
                                <field name="vi_tri_tai_san_id"/>
                            </tree>
                        </field>
                    </page>
                    <page name="lskh" string="Lịch sử khấu hao">
                        <field name="lich_su_khau_hao_ids" readonly="True">
                            <tree>
                                <field name="ma_phieu_khau_hao" width="200"/>
                                <field name="ngay_khau_hao" width="150"/>
                                <field name="so_tien_khau_hao" width="200"/>
                                <field name="gia_tri_con_lai" width="200"/>
                                <field name="loai_phieu" width="200"/>
                                <field name="ghi_chu" width="300"/>
                            </tree>
                        </field>
                    </page>
                    <page name="lskk" string="Lịch sử kiểm kê">
                        <field name="kiem_ke_history_ids" readonly="True">
                            <tree>
                                <field name="kiem_ke_tai_san_id"/>
                                <field name="so_luong_thuc_te"/>
                                <field name="trang_thai_tai_san"/>
                            </tree>
                        </field>
                    </page>
                    <page name="lslc" string="Lịch sử luân chuyển">
                        <field name="luan_chuyen_ids" readonly="True">
                            <tree>
                                <field name="ma_phieu_luan_chuyen"/>
                                <field name="bo_phan_nguon"/>
                                <field name="bo_phan_dich"/>
                                <field name="thoi_gian_luan_chuyen"/>
                            </tree>
                        </field>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>
```

**Các thành phần quan trọng:**

| Thành phần | Mô tả |
|------------|-------|
| `<sheet>` | Container chính của form |
| `<group>` | Nhóm các field, tạo layout 2 cột |
| `<notebook>` | Container cho các tab |
| `<page>` | Mỗi tab trong notebook |
| `attrs` | Điều khiển hiển thị/ẩn/readonly có điều kiện |
| `widget` | Widget đặc biệt (image, monetary, progressbar...) |

### 3.3.3. Search View (Tìm kiếm)

```xml
<!-- Search view -->
<record id="tai_san_view_search" model="ir.ui.view">
    <field name="name">tai_san.view.search</field>
    <field name="model">tai_san</field>
    <field name="arch" type="xml">
        <search string="Tìm kiếm tài sản">
            <!-- Các field tìm kiếm -->
            <field name="ma_tai_san"/>
            <field name="ten_tai_san"/>
            <field name="ngay_mua_ts"/>
            <field name="pp_khau_hao"/>
            <field name="don_vi_tinh"/>
            
            <!-- Bộ lọc nhanh -->
            <filter string="Đã phân bổ" name="da_phan_bo" 
                    domain="[('trang_thai_thanh_ly','=','da_phan_bo')]"/>
            <filter string="Đã thanh lý" name="da_thanh_ly" 
                    domain="[('trang_thai_thanh_ly','=','da_thanh_ly')]"/>
            
            <!-- Nhóm theo -->
            <group expand="0" string="Nhóm theo">
                <filter string="Loại tài sản" name="group_loai" 
                        context="{'group_by': 'danh_muc_ts_id'}"/>
                <filter string="Trạng thái" name="group_trang_thai" 
                        context="{'group_by': 'trang_thai_thanh_ly'}"/>
            </group>
        </search>
    </field>
</record>
```

### 3.3.4. Cấu hình Action và Menu

#### A. Định nghĩa Action

```xml
<!-- Action - Định nghĩa hành động mở view -->
<record id="tai_san_action" model="ir.actions.act_window">
    <field name="name">Tài sản cụ thể</field>
    <field name="res_model">tai_san</field>
    <field name="view_mode">tree,form</field>
    <!-- Optional: Domain, Context, Help text -->
    <field name="domain">[]</field>
    <field name="context">{}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Tạo tài sản đầu tiên!
        </p>
    </field>
</record>
```

#### B. Cấu hình Menu điều hướng

**File: `/quan_ly_tai_san/views/menu.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Menu gốc (Root menu) -->
        <menuitem id="menu_root" name="Quản lý tài sản" sequence="0"/>

        <!-- Dashboard submenu -->
        <menuitem id="menu_asset_dashboard" name="Dashboard" 
                  parent="menu_root" sequence="1"/>
        
        <menuitem id="menu_dashboard_overview" name="Tổng quan" 
                  action="dashboard_tong_quan_action" 
                  parent="menu_asset_dashboard" sequence="1"/>

        <!-- Tài sản submenu -->
        <menuitem name="Tài sản" id="menu_tai_san" 
                  parent="menu_root" sequence="2"/>
        
        <menuitem id="danh_muc_tai_san_menu" name="Loại tài sản" 
                  action="danh_muc_tai_san_action" 
                  parent="menu_tai_san" sequence="1"/>
        
        <menuitem id="tai_san_menu" name="Quản lý tài sản cụ thể" 
                  action="tai_san_action" 
                  parent="menu_tai_san" sequence="2"/>
        
        <menuitem id="phan_bo_tai_san_menu" name="Phân bổ tài sản" 
                  action="phan_bo_tai_san_action" 
                  parent="menu_tai_san" sequence="3"/>

        <!-- Khấu hao/Kiểm kê submenu -->
        <menuitem name="Khấu hao/Kiểm kê" id="kiem_ke_khau_hao" 
                  parent="menu_root" sequence="3"/>
        
        <menuitem id="khau_hao_tai_san_menu" name="Khấu hao tài sản" 
                  action="lich_su_khau_hao_action" 
                  parent="kiem_ke_khau_hao" sequence="1"/>
        
        <menuitem id="kiem_ke_tai_san_menu" name="Kiểm kê tài sản" 
                  action="kiem_ke_tai_san_action" 
                  parent="kiem_ke_khau_hao" sequence="2"/>

        <!-- Luân chuyển/Thanh lý submenu -->
        <menuitem name="Luân chuyển/Thanh lý" id="menu_luan_chuyen_tai_san" 
                  parent="menu_root" sequence="4"/>
        
        <menuitem id="luan_chuyen_tai_san_menu" name="Quản lý luân chuyển" 
                  parent="menu_luan_chuyen_tai_san" 
                  action="luan_chuyen_tai_san_action" sequence="1"/>
        
        <menuitem id="thanh_ly_tai_san_menu" name="Thanh lý tài sản" 
                  parent="menu_luan_chuyen_tai_san" 
                  action="thanh_ly_tai_san_action" sequence="2"/>

        <!-- Mượn trả submenu -->
        <menuitem name="Mượn trả tài sản" id="menu_muon_tra_tai_san" 
                  parent="menu_root" sequence="5"/>
        
        <menuitem id="don_muon_tai_san_menu" name="Đơn mượn tài sản" 
                  parent="menu_muon_tra_tai_san" 
                  action="don_muon_tai_san_action" sequence="1"/>
        
        <menuitem id="muon_tra_tai_san_menu" name="Quản lý mượn trả" 
                  parent="menu_muon_tra_tai_san" 
                  action="muon_tra_tai_san_action" sequence="2"/>
    </data>
</odoo>
```

**Cấu trúc Menu:**

```
📁 Quản lý tài sản (menu_root)
├── 📊 Dashboard
│   ├── Tổng quan
│   └── Danh sách mượn trả
├── 📦 Tài sản
│   ├── Loại tài sản
│   ├── Quản lý tài sản cụ thể
│   └── Phân bổ tài sản
├── 📉 Khấu hao/Kiểm kê
│   ├── Khấu hao tài sản
│   └── Kiểm kê tài sản
├── 🔄 Luân chuyển/Thanh lý
│   ├── Quản lý luân chuyển
│   └── Thanh lý tài sản
└── 📋 Mượn trả tài sản
    ├── Đơn mượn tài sản
    └── Quản lý mượn trả
```

### 3.3.5. Phân quyền truy cập (Security)

**File: `/quan_ly_tai_san/security/ir.model.access.csv`**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_danh_muc_tai_san_all,danh_muc_tai_san.all,model_danh_muc_tai_san,base.group_user,1,1,1,1
access_tai_san_all,tai_san.all,model_tai_san,base.group_user,1,1,1,1
access_kiem_ke_tai_san_line_all,kiem_ke_tai_san_line.all,model_kiem_ke_tai_san_line,,1,1,1,1
access_kiem_ke_tai_san_all,kiem_ke_tai_san.all,model_kiem_ke_tai_san,,1,1,1,1
access_lich_su_khau_hao_all,lich_su_khau_hao.all,model_lich_su_khau_hao,,1,1,1,1
access_luan_chuyen_tai_san_all,luan_chuyen_tai_san.all,model_luan_chuyen_tai_san,,1,1,1,1
access_muon_tra_tai_san_all,muon_tra_tai_san.all,model_muon_tra_tai_san,,1,1,1,1
access_phan_bo_tai_san_all,phan_bo_tai_san.all,model_phan_bo_tai_san,,1,1,1,1
access_thanh_ly_tai_san_all,thanh_ly_tai_san.all,model_thanh_ly_tai_san,,1,1,1,1
```

**Giải thích các cột:**

| Cột | Mô tả |
|-----|-------|
| `id` | ID duy nhất của quyền |
| `name` | Tên mô tả |
| `model_id:id` | Model được cấp quyền (format: model_<tên_model>) |
| `group_id:id` | Nhóm người dùng (rỗng = tất cả) |
| `perm_read` | Quyền đọc (1=có, 0=không) |
| `perm_write` | Quyền sửa |
| `perm_create` | Quyền tạo |
| `perm_unlink` | Quyền xóa |

---

## 3.4. Tổng kết

### Bảng tổng hợp các Model đã xây dựng

| Module | Model | Mô tả |
|--------|-------|-------|
| **quan_ly_tai_san** | `tai_san` | Thông tin tài sản chính |
| | `danh_muc_tai_san` | Loại/danh mục tài sản |
| | `phan_bo_tai_san` | Phân bổ tài sản cho phòng ban |
| | `lich_su_khau_hao` | Lịch sử khấu hao |
| | `kiem_ke_tai_san` | Kiểm kê tài sản |
| | `luan_chuyen_tai_san` | Luân chuyển tài sản |
| | `muon_tra_tai_san` | Mượn trả tài sản |
| | `thanh_ly_tai_san` | Thanh lý tài sản |
| **ke_toan_tai_san** | `khau_hao_tai_san` | Khấu hao kế toán |
| | `but_toan_khau_hao` | Bút toán khấu hao |
| | `tai_khoan_khau_hao` | Cấu hình tài khoản |
| | `ai_forecast` | Dự báo AI |

### Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python 3.8+, Odoo ORM |
| Frontend | XML/QWeb, JavaScript, CSS |
| Database | PostgreSQL |
| Web Framework | Werkzeug (qua Odoo) |
| Charting | Chart.js |

---

*Chương 3 - Xây dựng Module Quản lý Tài sản và các Module Tài chính Kế toán*
*Cập nhật: Tháng 01/2026*
