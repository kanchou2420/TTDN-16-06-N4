# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TaiKhoanKhauHao(models.Model):
    _name = 'tai_khoan_khau_hao'
    _description = 'Cấu hình tài khoản khấu hao'
    
    name = fields.Char('Tên cấu hình', required=True)
    loai_tai_san_id = fields.Many2one('danh_muc_tai_san', 'Loại tài sản', required=True)
    
    # Thông tin tài khoản kế toán - Lưu mã tài khoản (không dùng account.account)
    ma_tk_tai_san = fields.Char('Mã TK Tài sản cố định', required=True,
        default='211', help='VD: 211 - Tài sản cố định hữu hình')
    
    ma_tk_khau_hao_luy_ke = fields.Char('Mã TK Khấu hao lũy kế', required=True,
        default='2141', help='VD: 2141 - Hao mòn TSCĐ hữu hình')
    
    ma_tk_chi_phi = fields.Char('Mã TK Chi phí khấu hao', required=True,
        default='6274', help='VD: 6274 - Chi phí khấu hao TSCĐ')
    
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
