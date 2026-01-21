# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class NganSach(models.Model):
    _name = 'ngan_sach'
    _description = 'Ngân sách'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ten_ngan_sach'
    _order = 'nam desc, id desc'
    _sql_constraints = [
        ('ma_ngan_sach_unique', 'unique(ma_ngan_sach)', 'Mã ngân sách đã tồn tại!'),
    ]

    ma_ngan_sach = fields.Char('Mã ngân sách', required=True, copy=False)
    ten_ngan_sach = fields.Char('Tên ngân sách', required=True)
    nam = fields.Integer('Năm', required=True, default=lambda self: datetime.now().year)
    
    loai_ngan_sach = fields.Selection([
        ('nam', 'Ngân sách năm'),
        ('quy', 'Ngân sách quý'),
        ('thang', 'Ngân sách tháng'),
        ('du_an', 'Ngân sách dự án'),
    ], string='Loại ngân sách', required=True, default='nam')
    
    quy = fields.Selection([
        ('1', 'Quý 1'),
        ('2', 'Quý 2'),
        ('3', 'Quý 3'),
        ('4', 'Quý 4'),
    ], string='Quý')
    
    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12'),
    ], string='Tháng')
    
    ngay_bat_dau = fields.Date('Ngày bắt đầu', required=True)
    ngay_ket_thuc = fields.Date('Ngày kết thúc', required=True)
    
    don_vi_tien_te = fields.Selection([
        ('vnd', 'VNĐ'),
        ('usd', 'USD'),
    ], string='Đơn vị tiền tệ', default='vnd', required=True)
    
    tong_ngan_sach = fields.Float('Tổng ngân sách', required=True, default=0, tracking=True)
    tong_phan_bo = fields.Float('Tổng đã phân bổ', compute='_compute_tong_phan_bo', store=True)
    con_lai = fields.Float('Còn lại', compute='_compute_con_lai', store=True)
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('duyet', 'Đã duyệt'),
        ('dang_thuc_hien', 'Đang thực hiện'),
        ('ket_thuc', 'Kết thúc'),
        ('huy', 'Hủy'),
    ], string='Trạng thái', default='nhap', required=True, tracking=True)
    
    nguoi_lap = fields.Many2one('res.users', string='Người lập', default=lambda self: self.env.user)
    ngay_lap = fields.Date('Ngày lập', default=fields.Date.today)
    nguoi_duyet = fields.Many2one('res.users', string='Người duyệt')
    ngay_duyet = fields.Date('Ngày duyệt')
    
    ghi_chu = fields.Text('Ghi chú')
    
    # Relations
    du_toan_chi_ids = fields.One2many('du_toan_chi', 'ngan_sach_id', string='Dự toán chi')
    phan_bo_ids = fields.One2many('phan_bo_ngan_sach', 'ngan_sach_id', string='Phân bổ ngân sách')
    theo_doi_ids = fields.One2many('theo_doi_thuc_hien_ngan_sach', 'ngan_sach_id', string='Theo dõi thực hiện')
    
    @api.depends('phan_bo_ids.so_tien')
    def _compute_tong_phan_bo(self):
        for record in self:
            record.tong_phan_bo = sum(record.phan_bo_ids.mapped('so_tien'))
    
    @api.depends('tong_ngan_sach', 'tong_phan_bo')
    def _compute_con_lai(self):
        for record in self:
            record.con_lai = record.tong_ngan_sach - record.tong_phan_bo
    
    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_dates(self):
        for record in self:
            if record.ngay_ket_thuc < record.ngay_bat_dau:
                raise ValidationError('Ngày kết thúc phải sau ngày bắt đầu!')
    
    @api.constrains('tong_ngan_sach')
    def _check_tong_ngan_sach(self):
        for record in self:
            if record.tong_ngan_sach <= 0:
                raise ValidationError('Tổng ngân sách phải lớn hơn 0!')
    
    # FIX: THÊM kiểm tra bắt buộc quý/tháng theo loại ngân sách
    @api.constrains('loai_ngan_sach', 'quy', 'thang')
    def _check_loai_ngan_sach_fields(self):
        """
        Đảm bảo dữ liệu nhất quán:
        - Nếu loại = 'quy' → bắt buộc chọn quý
        - Nếu loại = 'thang' → bắt buộc chọn tháng
        """
        for record in self:
            if record.loai_ngan_sach == 'quy' and not record.quy:
                raise ValidationError(
                    'Vui lòng chọn quý khi loại ngân sách = "Ngân sách quý"'
                )
            elif record.loai_ngan_sach == 'thang' and not record.thang:
                raise ValidationError(
                    'Vui lòng chọn tháng khi loại ngân sách = "Ngân sách tháng"'
                )
    
    def action_duyet(self):
        """Duyệt ngân sách"""
        self.write({
            'trang_thai': 'duyet',
            'nguoi_duyet': self.env.user.id,
            'ngay_duyet': fields.Date.today(),
        })
    
    def action_bat_dau_thuc_hien(self):
        """Bắt đầu thực hiện ngân sách"""
        self.write({'trang_thai': 'dang_thuc_hien'})
    
    def action_ket_thuc(self):
        """Kết thúc ngân sách"""
        self.write({'trang_thai': 'ket_thuc'})
    
    def action_huy(self):
        """Hủy ngân sách"""
        self.write({'trang_thai': 'huy'})
    
    def action_chuyen_ve_nhap(self):
        """Chuyển về trạng thái nháp"""
        self.write({'trang_thai': 'nhap'})
