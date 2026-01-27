# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ButToanKhauHao(models.Model):
    _name = 'but_toan_khau_hao'
    _description = 'Bút toán khấu hao - Sổ nội bộ'
    _rec_name = 'ma_but_toan'
    _order = 'ngay_ghi_so desc, id desc'
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
    
    # Computed fields
    ten_tai_san = fields.Char('Tên tài sản', related='tai_san_id.ten_tai_san', store=True)
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban', 
                                    compute='_compute_phong_ban', store=True)
    
    @api.depends('tai_san_id')
    def _compute_phong_ban(self):
        for record in self:
            # Lấy phòng ban từ phân bổ tài sản
            phan_bo = self.env['phan_bo_tai_san'].search([
                ('tai_san_id', '=', record.tai_san_id.id)
            ], limit=1)
            record.phong_ban_id = phan_bo.phong_ban_id.id if phan_bo else False
    
    def action_post(self):
        """Ghi sổ bút toán"""
        self.write({'trang_thai': 'posted'})
    
    def action_cancel(self):
        """Hủy bút toán"""
        self.write({'trang_thai': 'cancelled'})
    
    def action_draft(self):
        """Chuyển về nháp"""
        self.write({'trang_thai': 'draft'})
