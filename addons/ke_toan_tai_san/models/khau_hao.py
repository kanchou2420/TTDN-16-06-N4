# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class KhauHaoTaiSan(models.Model):
    _name = 'khau_hao_tai_san'
    _description = 'Khấu hao tài sản - Ghi nhận nội bộ'
    _rec_name = 'ma_khau_hao'
    _order = 'ngay_khau_hao desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    ma_khau_hao = fields.Char('Mã khấu hao', readonly=True)
    tai_san_id = fields.Many2one('tai_san', 'Tài sản', required=True, ondelete='cascade')
    ngay_khau_hao = fields.Date('Ngày khấu hao', required=True, default=fields.Date.today)
    
    gia_tri_ban_dau = fields.Float('Giá trị ban đầu', related='tai_san_id.gia_tri_ban_dau', store=True, search=False)
    gia_tri_con_lai = fields.Float('Giá trị còn lại trước khấu hao', required=True)
    so_tien_khau_hao = fields.Float('Số tiền khấu hao', required=True)
    gia_tri_sau_khau_hao = fields.Float('Giá trị sau khấu hao', compute='_compute_gia_tri_sau', store=True, search=False)
    
    pp_khau_hao = fields.Selection([
        ('straight-line', 'Tuyến tính'),
        ('degressive', 'Giảm dần'),
        ('units', 'Đơn vị sản xuất'),
    ], string='Phương pháp khấu hao', required=True, default='straight-line')
    
    # Bút toán nội bộ (không dùng account.move)
    but_toan_id = fields.Many2one('but_toan_khau_hao', 'Bút toán khấu hao', readonly=True)
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('posted', 'Ghi sổ'),
        ('cancelled', 'Hủy'),
    ], string='Trạng thái', default='draft', readonly=True, tracking=True)
    
    ghi_chu = fields.Text('Ghi chú')
    
    @api.depends('gia_tri_con_lai', 'so_tien_khau_hao')
    def _compute_gia_tri_sau(self):
        for record in self:
            record.gia_tri_sau_khau_hao = max(0, record.gia_tri_con_lai - record.so_tien_khau_hao)
    
    @api.model
    def create(self, vals):
        # Tạo mã khấu hao tự động
        if not vals.get('ma_khau_hao'):
            sequence = self.env['ir.sequence'].next_by_code('khau_hao_tai_san') or '0'
            vals['ma_khau_hao'] = f"KH-{sequence}-{datetime.now().strftime('%m%Y')}"
        return super().create(vals)
    
    def action_post_journal(self):
        """Ghi sổ khấu hao nội bộ"""
        for record in self:
            if record.but_toan_id:
                raise ValidationError("Bút toán đã được ghi sổ!")
            
            tai_san = record.tai_san_id
            # Lấy tài khoản khấu hao từ cấu hình
            tai_khoan_config = self.env['tai_khoan_khau_hao'].search([
                ('loai_tai_san_id', '=', tai_san.danh_muc_ts_id.id)
            ], limit=1)
            
            if not tai_khoan_config:
                raise ValidationError(
                    f"Chưa cấu hình tài khoản khấu hao cho loại tài sản '{tai_san.danh_muc_ts_id.ten_danh_muc_ts}'"
                )
            
            # Tạo bút toán khấu hao nội bộ
            but_toan = self.env['but_toan_khau_hao'].create({
                'ma_but_toan': f"BT-{record.ma_khau_hao}",
                'ngay_ghi_so': record.ngay_khau_hao,
                'khau_hao_id': record.id,
                'tai_san_id': tai_san.id,
                'tai_khoan_no': tai_khoan_config.ma_tk_chi_phi,
                'tai_khoan_co': tai_khoan_config.ma_tk_khau_hao_luy_ke,
                'so_tien': record.so_tien_khau_hao,
                'dien_giai': f"Khấu hao {tai_san.ten_tai_san} ({record.ma_khau_hao})",
                'trang_thai': 'posted',
            })
            
            record.but_toan_id = but_toan.id
            record.trang_thai = 'posted'
            
            # Cập nhật giá trị hiện tại của tài sản
            if hasattr(tai_san, 'gia_tri_hien_tai'):
                tai_san.gia_tri_hien_tai = record.gia_tri_sau_khau_hao
    
    def action_cancel(self):
        """Hủy khấu hao"""
        for record in self:
            if record.but_toan_id:
                record.but_toan_id.trang_thai = 'cancelled'
            record.trang_thai = 'cancelled'
