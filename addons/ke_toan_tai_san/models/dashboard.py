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
    
    # Tích hợp từ module thu chi công nợ
    tong_thu_thang = fields.Float('Tổng thu tháng này', compute='_compute_thu_chi_stats', search=False)
    tong_chi_thang = fields.Float('Tổng chi tháng này', compute='_compute_thu_chi_stats', search=False)
    can_doi_thang = fields.Float('Cân đối tháng này', compute='_compute_thu_chi_stats', search=False)
    
    # Tích hợp từ module ngân sách
    tong_ngan_sach = fields.Float('Tổng ngân sách', compute='_compute_ngan_sach_stats', search=False)
    ngan_sach_da_chi = fields.Float('Ngân sách đã chi', compute='_compute_ngan_sach_stats', search=False)
    ngan_sach_con_lai = fields.Float('Ngân sách còn lại', compute='_compute_ngan_sach_stats', search=False)
    
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
    
    @api.depends('name')
    def _compute_thu_chi_stats(self):
        """Tính toán thống kê thu chi từ module quanly_thuchi_congno"""
        for record in self:
            today = fields.Date.today()
            first_of_month = f'{today.year}-{today.month:02d}-01'
            
            # Tổng thu tháng này
            try:
                phieu_thu = self.env['phieu_thu'].search([
                    ('state', '=', 'posted'),
                    ('date', '>=', first_of_month),
                ])
                record.tong_thu_thang = sum(pt.amount for pt in phieu_thu)
            except Exception:
                record.tong_thu_thang = 0
            
            # Tổng chi tháng này
            try:
                phieu_chi = self.env['phieu_chi'].search([
                    ('state', '=', 'posted'),
                    ('date', '>=', first_of_month),
                ])
                record.tong_chi_thang = sum(pc.amount for pc in phieu_chi)
            except Exception:
                record.tong_chi_thang = 0
            
            record.can_doi_thang = record.tong_thu_thang - record.tong_chi_thang
    
    @api.depends('name')
    def _compute_ngan_sach_stats(self):
        """Tính toán thống kê ngân sách từ module quan_ly_ngan_sach"""
        for record in self:
            try:
                ngan_sach_list = self.env['ngan_sach'].search([
                    ('trang_thai', 'in', ['duyet', 'dang_thuc_hien']),
                ])
                record.tong_ngan_sach = sum(ns.tong_ngan_sach for ns in ngan_sach_list)
                record.ngan_sach_da_chi = sum(ns.tong_phan_bo for ns in ngan_sach_list)
                record.ngan_sach_con_lai = sum(ns.con_lai for ns in ngan_sach_list)
            except Exception:
                record.tong_ngan_sach = 0
                record.ngan_sach_da_chi = 0
                record.ngan_sach_con_lai = 0
