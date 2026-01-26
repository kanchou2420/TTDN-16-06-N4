# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class SoTaiSan(models.Model):
    _name = 'so_tai_san'
    _description = 'Sổ tài sản - Bảng cân đối tài sản'
    
    name = fields.Char('Tên báo cáo', compute='_compute_name', store=True, search=False)
    ngay_lap = fields.Date('Ngày lập', default=fields.Date.today)
    thang = fields.Integer('Tháng', required=True, default=lambda: datetime.now().month)
    nam = fields.Integer('Năm', required=True, default=lambda: datetime.now().year)
    
    # Chi tiết tài sản
    tai_san_ids = fields.One2many('so_tai_san_line', 'so_tai_san_id', 'Chi tiết tài sản', search=False)
    
    tong_gia_tri_ban_dau = fields.Float('Tổng giá trị ban đầu', compute='_compute_totals', store=True, search=False)
    tong_khau_hao_luy_ke = fields.Float('Tổng khấu hao lũy kế', compute='_compute_totals', store=True, search=False)
    tong_gia_tri_con_lai = fields.Float('Tổng giá trị còn lại', compute='_compute_totals', store=True, search=False)
    
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
    ], string='Trạng thái', default='draft')
    
    @api.depends('thang', 'nam')
    def _compute_name(self):
        for record in self:
            record.name = f"Sổ tài sản tháng {record.thang}/{record.nam}"
    
    @api.depends('tai_san_ids.gia_tri_ban_dau', 'tai_san_ids.khau_hao_luy_ke', 'tai_san_ids.gia_tri_con_lai')
    def _compute_totals(self):
        for record in self:
            record.tong_gia_tri_ban_dau = sum(line.gia_tri_ban_dau for line in record.tai_san_ids)
            record.tong_khau_hao_luy_ke = sum(line.khau_hao_luy_ke for line in record.tai_san_ids)
            record.tong_gia_tri_con_lai = sum(line.gia_tri_con_lai for line in record.tai_san_ids)
    
    def action_calculate_depreciation(self):
        """Tính toán khấu hao cho tất cả tài sản"""
        tai_san_objs = self.env['tai_san'].search([
            ('pp_khau_hao', '!=', 'none'),
        ])
        
        for tai_san in tai_san_objs:
            so_tien_khau_hao = self._tinh_khau_hao(tai_san)
            if so_tien_khau_hao > 0:
                self.env['khau_hao_tai_san'].create({
                    'tai_san_id': tai_san.id,
                    'gia_tri_con_lai': tai_san.gia_tri_hien_tai,
                    'so_tien_khau_hao': so_tien_khau_hao,
                    'pp_khau_hao': tai_san.pp_khau_hao,
                })
    
    def _tinh_khau_hao(self, tai_san):
        """Tính số tiền khấu hao"""
        if tai_san.pp_khau_hao == 'straight-line':
            # Phương pháp tuyến tính
            nam_con_lai = tai_san.thoi_gian_toi_da - tai_san.thoi_gian_su_dung
            if nam_con_lai > 0:
                return tai_san.gia_tri_hien_tai / nam_con_lai / 12
        
        elif tai_san.pp_khau_hao == 'degressive':
            # Phương pháp giảm dần
            ty_le = tai_san.ty_le_khau_hao / 100
            return tai_san.gia_tri_hien_tai * ty_le / 12
        
        return 0


class SoTaiSanLine(models.Model):
    _name = 'so_tai_san_line'
    _description = 'Chi tiết sổ tài sản'
    
    so_tai_san_id = fields.Many2one('so_tai_san', 'Sổ tài sản', required=True, ondelete='cascade')
    tai_san_id = fields.Many2one('tai_san', 'Tài sản', required=True)
    
    ma_tai_san = fields.Char('Mã tài sản', related='tai_san_id.ma_tai_san', search=False)
    ten_tai_san = fields.Char('Tên tài sản', related='tai_san_id.ten_tai_san', search=False)
    
    gia_tri_ban_dau = fields.Float('Giá trị ban đầu', compute='_compute_values', store=True, search=False)
    khau_hao_luy_ke = fields.Float('Khấu hao lũy kế', compute='_compute_values', store=True, search=False)
    gia_tri_con_lai = fields.Float('Giá trị còn lại', compute='_compute_values', store=True, search=False)
    
    @api.depends('tai_san_id')
    def _compute_values(self):
        for line in self:
            if line.tai_san_id:
                line.gia_tri_ban_dau = line.tai_san_id.gia_tri_ban_dau
                
                # Tính khấu hao lũy kế từ lich_su_khau_hao
                khau_hao_records = self.env['khau_hao_tai_san'].search([
                    ('tai_san_id', '=', line.tai_san_id.id),
                    ('trang_thai', '=', 'posted'),
                ])
                line.khau_hao_luy_ke = sum(kh.so_tien_khau_hao for kh in khau_hao_records)
                
                line.gia_tri_con_lai = line.gia_tri_ban_dau - line.khau_hao_luy_ke
