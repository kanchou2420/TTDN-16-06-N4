# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DuToanChi(models.Model):
    _name = 'du_toan_chi'
    _description = 'Dự toán chi'
    _rec_name = 'ten_du_toan'
    _order = 'ngay_tao desc, id desc'

    ma_du_toan = fields.Char('Mã dự toán', required=True, copy=False)
    ten_du_toan = fields.Char('Tên dự toán', required=True)
    
    ngan_sach_id = fields.Many2one('ngan_sach', string='Ngân sách', required=True, ondelete='restrict')
    
    loai_chi = fields.Selection([
        ('mua_sam_ts', 'Mua sắm tài sản'),
        ('khau_hao_ts', 'Khấu hao tài sản'),
        ('bao_duong_sua_chua', 'Bảo dưỡng sửa chữa'),
        ('nhan_su', 'Chi phí nhân sự'),
        ('van_phong_pham', 'Văn phòng phẩm'),
        ('dao_tao', 'Đào tạo'),
        ('marketing', 'Marketing'),
        ('khac', 'Chi phí khác'),
    ], string='Loại chi', required=True)
    
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban đề xuất')
    danh_muc_ts_id = fields.Many2one('danh_muc_tai_san', string='Danh mục tài sản', 
                                      help='Áp dụng cho loại chi mua sắm tài sản')
    
    so_tien_du_kien = fields.Float('Số tiền dự kiến', required=True, default=0)
    so_tien_duyet = fields.Float('Số tiền được duyệt', default=0)
    
    # FIX: Thêm trường theo dõi "đã chi thực tế" để so sánh với dự toán
    # Trường này tự động cập nhật khi lập phiếu chi
    da_chi_thuc_te = fields.Float(
        'Đã chi thực tế',
        default=0,
        readonly=True,
        help='Tự động cập nhật từ phiếu chi - dùng để so sánh với dự toán'
    )
    con_lai_chi = fields.Float(
        'Còn lại chi',
        compute='_compute_con_lai_chi',
        store=True,
        help='Số tiền còn được phép chi = so_tien_duyet - da_chi_thuc_te'
    )
    tien_tiet_kiem = fields.Float(
        'Tiết kiệm',
        compute='_compute_tien_tiet_kiem',
        store=True,
        help='Tính được tiết kiệm = so_tien_duyet - da_chi_thuc_te (nếu > 0)'
    )
    tien_vuot = fields.Float(
        'Vượt',
        compute='_compute_tien_vuot',
        store=True,
        help='Nếu da_chi > so_tien_duyet'
    )
    
    don_vi_tien_te = fields.Selection([
        ('vnd', 'VNĐ'),
        ('usd', 'USD'),
    ], string='Đơn vị tiền tệ', default='vnd', required=True)
    
    thoi_gian_du_kien = fields.Date('Thời gian dự kiến thực hiện')
    uu_tien = fields.Selection([
        ('cao', 'Cao'),
        ('trung_binh', 'Trung bình'),
        ('thap', 'Thấp'),
    ], string='Mức độ ưu tiên', default='trung_binh')
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối'),
        ('hoan_thanh', 'Hoàn thành'),
    ], string='Trạng thái', default='nhap', required=True)
    
    ly_do_de_xuat = fields.Text('Lý do đề xuất')
    ly_do_tu_choi = fields.Text('Lý do từ chối')
    ghi_chu = fields.Text('Ghi chú')
    
    nguoi_de_xuat = fields.Many2one('res.users', string='Người đề xuất', default=lambda self: self.env.user)
    ngay_tao = fields.Date('Ngày tạo', default=fields.Date.today)
    nguoi_duyet = fields.Many2one('res.users', string='Người duyệt')
    ngay_duyet = fields.Date('Ngày duyệt')
    
    # File đính kèm
    file_dinh_kem = fields.Binary('File đính kèm', attachment=True)
    file_dinh_kem_filename = fields.Char('Tên file')
    
    # FIX: Thêm các hàm tính toán cho "đã chi thực tế"
    @api.depends('so_tien_duyet', 'da_chi_thuc_te')
    def _compute_con_lai_chi(self):
        """Tính số tiền còn lại được phép chi"""
        for record in self:
            record.con_lai_chi = record.so_tien_duyet - record.da_chi_thuc_te
    
    @api.depends('so_tien_duyet', 'da_chi_thuc_te')
    def _compute_tien_tiet_kiem(self):
        """Tính tiết kiệm (nếu chi ít hơn dự toán)"""
        for record in self:
            if record.da_chi_thuc_te < record.so_tien_duyet:
                record.tien_tiet_kiem = record.so_tien_duyet - record.da_chi_thuc_te
            else:
                record.tien_tiet_kiem = 0
    
    @api.depends('so_tien_duyet', 'da_chi_thuc_te')
    def _compute_tien_vuot(self):
        """Tính tiền vượt (nếu chi nhiều hơn dự toán)"""
        for record in self:
            if record.da_chi_thuc_te > record.so_tien_duyet:
                record.tien_vuot = record.da_chi_thuc_te - record.so_tien_duyet
            else:
                record.tien_vuot = 0
    
    @api.constrains('so_tien_du_kien')
    def _check_so_tien(self):
        for record in self:
            if record.so_tien_du_kien <= 0:
                raise ValidationError('Số tiền dự kiến phải lớn hơn 0!')
    
    @api.constrains('so_tien_duyet', 'so_tien_du_kien')
    def _check_so_tien_duyet(self):
        for record in self:
            if record.so_tien_duyet > record.so_tien_du_kien:
                raise ValidationError('Số tiền được duyệt không được vượt quá số tiền dự kiến!')
    
    def action_gui_duyet(self):
        """Gửi duyệt dự toán"""
        self.write({'trang_thai': 'cho_duyet'})
    
    def action_duyet(self):
        """Duyệt dự toán"""
        if self.so_tien_duyet <= 0:
            raise ValidationError('Vui lòng nhập số tiền được duyệt!')
        
        self.write({
            'trang_thai': 'duyet',
            'nguoi_duyet': self.env.user.id,
            'ngay_duyet': fields.Date.today(),
        })
    
    def action_tu_choi(self):
        """Từ chối dự toán"""
        if not self.ly_do_tu_choi:
            raise ValidationError('Vui lòng nhập lý do từ chối!')
        
        self.write({
            'trang_thai': 'tu_choi',
            'nguoi_duyet': self.env.user.id,
            'ngay_duyet': fields.Date.today(),
        })
    
    def action_hoan_thanh(self):
        """Hoàn thành dự toán"""
        self.write({'trang_thai': 'hoan_thanh'})
