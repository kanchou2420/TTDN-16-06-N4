# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TaiKhoanKhauHao(models.Model):
    _name = 'tai_khoan_khau_hao'
    _description = 'Cấu hình tài khoản khấu hao'
    
    name = fields.Char('Tên cấu hình', required=True)
    loai_tai_san_id = fields.Many2one('danh_muc_tai_san', 'Loại tài sản', required=True)
    
    # Thông tin tài khoản kế toán
    journal_id = fields.Many2one('account.journal', 'Sổ nhật ký', required=True,
        domain=[('type', '=', 'general')])
    
    account_asset_id = fields.Many2one('account.account', 'TK Tài sản cố định',
        required=True, domain=[('deprecated', '=', False)])
    
    account_accumulated_depreciation_id = fields.Many2one('account.account', 
        'TK Khấu hao tích lũy', required=True, domain=[('deprecated', '=', False)])
    
    account_depreciation_expense_id = fields.Many2one('account.account',
        'TK Chi phí khấu hao', required=True, domain=[('deprecated', '=', False)])
    
    # Cấu hình khấu hao
    thoi_gian_su_dung = fields.Integer('Thời gian sử dụng (năm)', default=5)
    ty_le_khau_hao = fields.Float('Tỷ lệ khấu hao (%)', default=20)
    pp_khau_hao_mac_dinh = fields.Selection([
        ('straight-line', 'Tuyến tính'),
        ('degressive', 'Giảm dần'),
        ('units', 'Đơn vị sản xuất'),
    ], string='Phương pháp khấu hao mặc định', default='straight-line')
    
    active = fields.Boolean('Kích hoạt', default=True)
    ghi_chu = fields.Text('Ghi chú')
