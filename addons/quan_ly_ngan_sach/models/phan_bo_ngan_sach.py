# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PhanBoNganSach(models.Model):
    _name = 'phan_bo_ngan_sach'
    _description = 'Phân bổ ngân sách'
    _rec_name = 'ten_phan_bo'
    _order = 'ngay_phan_bo desc, id desc'

    ma_phan_bo = fields.Char('Mã phân bổ', required=True, copy=False)
    ten_phan_bo = fields.Char('Tên phân bổ', required=True)
    
    ngan_sach_id = fields.Many2one('ngan_sach', string='Ngân sách', required=True, ondelete='cascade')
    
    loai_phan_bo = fields.Selection([
        ('phong_ban', 'Theo phòng ban'),
        ('danh_muc_ts', 'Theo danh mục tài sản'),
        ('du_an', 'Theo dự án'),
        ('hoat_dong', 'Theo hoạt động'),
    ], string='Loại phân bổ', required=True)
    
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban')
    danh_muc_ts_id = fields.Many2one('danh_muc_tai_san', string='Danh mục tài sản')
    
    so_tien = fields.Float('Số tiền phân bổ', required=True, default=0)
    so_tien_da_su_dung = fields.Float('Số tiền đã sử dụng', compute='_compute_so_tien_da_su_dung', store=True)
    so_tien_con_lai = fields.Float('Số tiền còn lại', compute='_compute_so_tien_con_lai', store=True)
    ty_le_su_dung = fields.Float('Tỷ lệ sử dụng (%)', compute='_compute_ty_le_su_dung', store=True)
    
    don_vi_tien_te = fields.Selection([
        ('vnd', 'VNĐ'),
        ('usd', 'USD'),
    ], string='Đơn vị tiền tệ', default='vnd', required=True)
    
    ngay_bat_dau = fields.Date('Ngày bắt đầu', required=True)
    ngay_ket_thuc = fields.Date('Ngày kết thúc', required=True)
    
    trang_thai = fields.Selection([
        ('chua_su_dung', 'Chưa sử dụng'),
        ('dang_su_dung', 'Đang sử dụng'),
        ('het', 'Đã hết'),
        ('het_han', 'Hết hạn'),
    ], string='Trạng thái', default='chua_su_dung', required=True)
    
    muc_dich = fields.Text('Mục đích sử dụng')
    ghi_chu = fields.Text('Ghi chú')
    
    # Liên kết với nhân sự
    nguoi_phu_trach_id = fields.Many2one('nhan_vien', string='Nhân sự phụ trách',
                                          help='Nhân sự phụ trách phân bổ ngân sách này')
    nguoi_phu_trach = fields.Many2one('res.users', string='User phụ trách')
    nguoi_tao_id = fields.Many2one('nhan_vien', string='Nhân sự tạo',
                                    help='Nhân sự tạo bản ghi phân bổ')
    nguoi_tao = fields.Many2one('res.users', string='User tạo', default=lambda self: self.env.user)
    ngay_phan_bo = fields.Date('Ngày phân bổ', default=fields.Date.today)
    
    # Relations
    theo_doi_ids = fields.One2many('theo_doi_thuc_hien_ngan_sach', 'phan_bo_id', string='Theo dõi chi tiêu')
    
    @api.depends('theo_doi_ids.so_tien_thuc_te')
    def _compute_so_tien_da_su_dung(self):
        for record in self:
            record.so_tien_da_su_dung = sum(record.theo_doi_ids.mapped('so_tien_thuc_te'))
    
    @api.depends('so_tien', 'so_tien_da_su_dung')
    def _compute_so_tien_con_lai(self):
        for record in self:
            record.so_tien_con_lai = record.so_tien - record.so_tien_da_su_dung
    
    @api.depends('so_tien', 'so_tien_da_su_dung')
    def _compute_ty_le_su_dung(self):
        for record in self:
            if record.so_tien > 0:
                record.ty_le_su_dung = (record.so_tien_da_su_dung / record.so_tien) * 100
            else:
                record.ty_le_su_dung = 0
    
    @api.constrains('so_tien')
    def _check_so_tien(self):
        for record in self:
            if record.so_tien <= 0:
                raise ValidationError('Số tiền phân bổ phải lớn hơn 0!')
    
    # FIX: THÊM kiểm tra tổng phân bổ không vượt quá ngân sách
    @api.constrains('so_tien', 'ngan_sach_id')
    def _check_tong_phan_bo_not_exceed_budget(self):
        """
        Đảm bảo tổng số tiền phân bổ không vượt quá tổng ngân sách.
        Quản lý rủi ro: tránh phân bổ quá mức.
        """
        for record in self:
            if record.ngan_sach_id:
                # Tính tổng phân bổ (bao gồm bản ghi hiện tại)
                tong_phan_bo = sum(
                    record.ngan_sach_id.phan_bo_ids.mapped('so_tien')
                )
                
                if tong_phan_bo > record.ngan_sach_id.tong_ngan_sach:
                    raise ValidationError(
                        f'❌ VƯỢT NGÂN SÁCH!\n'
                        f'Tổng phân bổ ({tong_phan_bo:,.0f}) vượt quá '
                        f'ngân sách ({record.ngan_sach_id.tong_ngan_sach:,.0f})\n'
                        f'Vui lòng giảm số tiền phân bổ.'
                    )
    
    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_dates(self):
        for record in self:
            if record.ngay_ket_thuc < record.ngay_bat_dau:
                raise ValidationError('Ngày kết thúc phải sau ngày bắt đầu!')
    
    @api.constrains('so_tien', 'ngan_sach_id')
    def _check_ngan_sach_con_lai(self):
        for record in self:
            if record.ngan_sach_id.con_lai < 0:
                raise ValidationError('Số tiền phân bổ vượt quá ngân sách còn lại!')
    
    @api.onchange('so_tien_da_su_dung', 'so_tien')
    def _onchange_trang_thai(self):
        """Tự động cập nhật trạng thái khi số tiền thay đổi"""
        for record in self:
            if record.so_tien_da_su_dung >= record.so_tien:
                record.trang_thai = 'het'
            elif record.so_tien_da_su_dung > 0:
                record.trang_thai = 'dang_su_dung'
            else:
                record.trang_thai = 'chua_su_dung'
