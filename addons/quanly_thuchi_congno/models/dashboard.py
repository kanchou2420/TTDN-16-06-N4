# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, timedelta


class ThuChiDashboard(models.TransientModel):
    _name = 'thuchi.dashboard'
    _description = 'Dashboard Thu Chi Công Nợ'

    name = fields.Char('Tên', default='Dashboard Thu Chi')
    
    # ===== PHIẾU THU =====
    tong_phieu_thu = fields.Integer('Tổng phiếu thu', compute='_compute_phieu_thu')
    phieu_thu_nhap = fields.Integer('PT Nháp', compute='_compute_phieu_thu')
    phieu_thu_xacnhan = fields.Integer('PT Xác nhận', compute='_compute_phieu_thu')
    phieu_thu_posted = fields.Integer('PT Đã ghi sổ', compute='_compute_phieu_thu')
    tong_tien_thu = fields.Float('Tổng tiền thu', compute='_compute_phieu_thu')
    tong_tien_thu_thang = fields.Float('Thu tháng này', compute='_compute_phieu_thu')
    
    # ===== PHIẾU CHI =====
    tong_phieu_chi = fields.Integer('Tổng phiếu chi', compute='_compute_phieu_chi')
    phieu_chi_nhap = fields.Integer('PC Nháp', compute='_compute_phieu_chi')
    phieu_chi_cho_duyet = fields.Integer('PC Chờ duyệt', compute='_compute_phieu_chi')
    phieu_chi_da_duyet = fields.Integer('PC Đã duyệt', compute='_compute_phieu_chi')
    phieu_chi_posted = fields.Integer('PC Đã ghi sổ', compute='_compute_phieu_chi')
    tong_tien_chi = fields.Float('Tổng tiền chi', compute='_compute_phieu_chi')
    tong_tien_chi_thang = fields.Float('Chi tháng này', compute='_compute_phieu_chi')
    
    # ===== CÔNG NỢ =====
    tong_cong_no_thu = fields.Integer('Công nợ phải thu', compute='_compute_cong_no')
    tong_tien_phai_thu = fields.Float('Tiền phải thu', compute='_compute_cong_no')
    cong_no_thu_qua_han = fields.Integer('Phải thu quá hạn', compute='_compute_cong_no')
    
    tong_cong_no_tra = fields.Integer('Công nợ phải trả', compute='_compute_cong_no')
    tong_tien_phai_tra = fields.Float('Tiền phải trả', compute='_compute_cong_no')
    cong_no_tra_qua_han = fields.Integer('Phải trả quá hạn', compute='_compute_cong_no')
    
    # ===== CÂN ĐỐI =====
    can_doi = fields.Float('Cân đối Thu - Chi', compute='_compute_can_doi')
    can_doi_thang = fields.Float('Cân đối tháng này', compute='_compute_can_doi')

    @api.depends('name')
    def _compute_phieu_thu(self):
        PhieuThu = self.env['phieu_thu']
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        for rec in self:
            all_pt = PhieuThu.search([])
            rec.tong_phieu_thu = len(all_pt)
            rec.phieu_thu_nhap = PhieuThu.search_count([('state', '=', 'draft')])
            rec.phieu_thu_xacnhan = PhieuThu.search_count([('state', '=', 'confirmed')])
            rec.phieu_thu_posted = PhieuThu.search_count([('state', '=', 'posted')])
            
            posted_pt = PhieuThu.search([('state', '=', 'posted')])
            rec.tong_tien_thu = sum(posted_pt.mapped('amount'))
            
            # Thu tháng này
            pt_thang = PhieuThu.search([
                ('state', '=', 'posted'),
                ('date', '>=', first_day_of_month),
                ('date', '<=', today)
            ])
            rec.tong_tien_thu_thang = sum(pt_thang.mapped('amount'))

    @api.depends('name')
    def _compute_phieu_chi(self):
        PhieuChi = self.env['phieu_chi']
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        for rec in self:
            all_pc = PhieuChi.search([])
            rec.tong_phieu_chi = len(all_pc)
            rec.phieu_chi_nhap = PhieuChi.search_count([('state', '=', 'draft')])
            rec.phieu_chi_cho_duyet = PhieuChi.search_count([('state', '=', 'confirmed')])
            rec.phieu_chi_da_duyet = PhieuChi.search_count([('state', '=', 'approved')])
            rec.phieu_chi_posted = PhieuChi.search_count([('state', '=', 'posted')])
            
            posted_pc = PhieuChi.search([('state', '=', 'posted')])
            rec.tong_tien_chi = sum(posted_pc.mapped('amount'))
            
            # Chi tháng này
            pc_thang = PhieuChi.search([
                ('state', '=', 'posted'),
                ('date', '>=', first_day_of_month),
                ('date', '<=', today)
            ])
            rec.tong_tien_chi_thang = sum(pc_thang.mapped('amount'))

    @api.depends('name')
    def _compute_cong_no(self):
        CongNoThu = self.env['cong_no_phai_thu']
        CongNoTra = self.env['cong_no_phai_tra']
        
        for rec in self:
            # Công nợ phải thu
            cn_thu = CongNoThu.search([('state', '!=', 'done')])
            rec.tong_cong_no_thu = len(cn_thu)
            rec.tong_tien_phai_thu = sum(cn_thu.mapped('residual'))
            rec.cong_no_thu_qua_han = CongNoThu.search_count([
                ('is_overdue', '=', True),
                ('state', '!=', 'done')
            ])
            
            # Công nợ phải trả
            cn_tra = CongNoTra.search([('state', '!=', 'done')])
            rec.tong_cong_no_tra = len(cn_tra)
            rec.tong_tien_phai_tra = sum(cn_tra.mapped('residual'))
            rec.cong_no_tra_qua_han = CongNoTra.search_count([
                ('is_overdue', '=', True),
                ('state', '!=', 'done')
            ])

    @api.depends('tong_tien_thu', 'tong_tien_chi', 'tong_tien_thu_thang', 'tong_tien_chi_thang')
    def _compute_can_doi(self):
        for rec in self:
            rec.can_doi = rec.tong_tien_thu - rec.tong_tien_chi
            rec.can_doi_thang = rec.tong_tien_thu_thang - rec.tong_tien_chi_thang

    # ===== ACTIONS =====
    def action_view_phieu_thu(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phiếu Thu',
            'res_model': 'phieu_thu',
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_phieu_thu_draft(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phiếu Thu Nháp',
            'res_model': 'phieu_thu',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'draft')],
            'target': 'current',
        }

    def action_view_phieu_chi(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phiếu Chi',
            'res_model': 'phieu_chi',
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_phieu_chi_pending(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phiếu Chi Chờ Duyệt',
            'res_model': 'phieu_chi',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'confirmed')],
            'target': 'current',
        }

    def action_view_cong_no_thu(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công Nợ Phải Thu',
            'res_model': 'cong_no_phai_thu',
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_cong_no_thu_overdue(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công Nợ Quá Hạn',
            'res_model': 'cong_no_phai_thu',
            'view_mode': 'tree,form',
            'domain': [('is_overdue', '=', True), ('state', '!=', 'done')],
            'target': 'current',
        }

    def action_view_cong_no_tra(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công Nợ Phải Trả',
            'res_model': 'cong_no_phai_tra',
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_cong_no_tra_overdue(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công Nợ Quá Hạn',
            'res_model': 'cong_no_phai_tra',
            'view_mode': 'tree,form',
            'domain': [('is_overdue', '=', True), ('state', '!=', 'done')],
            'target': 'current',
        }

    @api.model
    def action_open_dashboard(self):
        """Mở dashboard - tạo bản ghi tạm thời"""
        dashboard = self.create({'name': 'Dashboard'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tổng Quan Thu Chi & Công Nợ',
            'res_model': 'thuchi.dashboard',
            'view_mode': 'form',
            'res_id': dashboard.id,
            'target': 'current',
            'flags': {'mode': 'readonly'},
        }
