# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime


class KeToanDashboard(models.Model):
    _name = 'ke_toan.dashboard'
    _description = 'Dashboard Kế Toán Tài Sản'
    
    name = fields.Char('Dashboard', default='Kế Toán Tài Sản')
    
    # Thống kê tài sản
    tong_tai_san = fields.Integer('Tổng số tài sản', compute='_compute_asset_stats', search=False)
    tong_gia_tri_tai_san = fields.Float('Tổng giá trị tài sản', compute='_compute_asset_stats', search=False)
    tong_khau_hao = fields.Float('Tổng khấu hao', compute='_compute_asset_stats', search=False)
    gia_tri_con_lai = fields.Float('Giá trị còn lại', compute='_compute_asset_stats', search=False)
    
    # Chi phí khấu hao
    chi_phi_khau_hao_thang_nay = fields.Float('Chi phí khấu hao tháng này', compute='_compute_depreciation_expense', search=False)
    chi_phi_khau_hao_nam_nay = fields.Float('Chi phí khấu hao năm nay', compute='_compute_depreciation_expense', search=False)
    
    @api.depends('name')
    def _compute_asset_stats(self):
        for record in self:
            tai_san_ids = self.env['tai_san'].search([])
            record.tong_tai_san = len(tai_san_ids)
            record.tong_gia_tri_tai_san = sum(ts.gia_tri_ban_dau for ts in tai_san_ids)
            
            # Tính khấu hao từ lich_su_khau_hao hoặc khau_hao_tai_san
            khau_hao_records = self.env['khau_hao_tai_san'].search([
                ('trang_thai', '=', 'posted')
            ])
            record.tong_khau_hao = sum(kh.so_tien_khau_hao for kh in khau_hao_records)
            record.gia_tri_con_lai = record.tong_gia_tri_tai_san - record.tong_khau_hao
    
    @api.depends('name')
    def _compute_depreciation_expense(self):
        for record in self:
            today = fields.Date.today()
            
            # Chi phí tháng này
            khau_hao_thang = self.env['khau_hao_tai_san'].search([
                ('trang_thai', '=', 'posted'),
                ('ngay_khau_hao', '>=', f'{today.year}-{today.month:02d}-01'),
            ])
            record.chi_phi_khau_hao_thang_nay = sum(kh.so_tien_khau_hao for kh in khau_hao_thang)
            
            # Chi phí năm nay
            khau_hao_nam = self.env['khau_hao_tai_san'].search([
                ('trang_thai', '=', 'posted'),
                ('ngay_khau_hao', '>=', f'{today.year}-01-01'),
            ])
            record.chi_phi_khau_hao_nam_nay = sum(kh.so_tien_khau_hao for kh in khau_hao_nam)
