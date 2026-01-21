# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ThanhLyTaiSanInherit(models.Model):
    _inherit = 'thanh_ly_tai_san'

    phieu_thu_id = fields.Many2one('phieu_thu', string='Phiếu thu liên quan', readonly=True)

    def action_tao_phieu_thu(self):
        """Tạo phiếu thu từ thanh lý tài sản"""
        self.ensure_one()
        if self.phieu_thu_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'phieu_thu',
                'res_id': self.phieu_thu_id.id,
                'view_mode': 'form',
            }
        
        # Tạo phiếu thu mới
        phieu_thu = self.env['phieu_thu'].create({
            'date': self.thoi_gian_thanh_ly.date() if self.thoi_gian_thanh_ly else fields.Date.today(),
            'loai_thu': 'thu_thanh_ly',
            'amount': self.gia_ban or 0,
            'ly_do': f'Thu tiền thanh lý tài sản {self.ma_thanh_ly} - {self.tai_san_id.ten_tai_san}',
            'thanh_ly_id': self.id,
            'note': f'Phiếu thu từ thanh lý tài sản\nMã thanh lý: {self.ma_thanh_ly}\nTài sản: {self.tai_san_id.ten_tai_san}',
        })
        self.phieu_thu_id = phieu_thu.id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'phieu_thu',
            'res_id': phieu_thu.id,
            'view_mode': 'form',
        }
