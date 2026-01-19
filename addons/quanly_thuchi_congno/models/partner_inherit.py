# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    # Currency field for monetary fields
    cong_no_currency_id = fields.Many2one(
        'res.currency', string='Tiền tệ',
        default=lambda self: self.env.company.currency_id)

    # Công nợ phải thu
    cong_no_phai_thu_ids = fields.One2many('cong_no_phai_thu', 'partner_id', string='Công nợ phải thu')
    cong_no_phai_thu_count = fields.Integer(string='Số CN phải thu', compute='_compute_cong_no_count')
    tong_cong_no_phai_thu = fields.Monetary(
        string='Tổng nợ phải thu', compute='_compute_tong_cong_no',
        currency_field='cong_no_currency_id')
    
    # Công nợ phải trả
    cong_no_phai_tra_ids = fields.One2many('cong_no_phai_tra', 'partner_id', string='Công nợ phải trả')
    cong_no_phai_tra_count = fields.Integer(string='Số CN phải trả', compute='_compute_cong_no_count')
    tong_cong_no_phai_tra = fields.Monetary(
        string='Tổng nợ phải trả', compute='_compute_tong_cong_no',
        currency_field='cong_no_currency_id')

    def _compute_cong_no_count(self):
        for partner in self:
            partner.cong_no_phai_thu_count = len(partner.cong_no_phai_thu_ids.filtered(
                lambda c: c.state in ('open', 'partial')))
            partner.cong_no_phai_tra_count = len(partner.cong_no_phai_tra_ids.filtered(
                lambda c: c.state in ('open', 'partial')))

    def _compute_tong_cong_no(self):
        for partner in self:
            partner.tong_cong_no_phai_thu = sum(
                partner.cong_no_phai_thu_ids.filtered(lambda c: c.state in ('open', 'partial')).mapped('residual'))
            partner.tong_cong_no_phai_tra = sum(
                partner.cong_no_phai_tra_ids.filtered(lambda c: c.state in ('open', 'partial')).mapped('residual'))

    def action_view_cong_no_phai_thu(self):
        """Xem công nợ phải thu của đối tác"""
        self.ensure_one()
        return {
            'name': f'Công nợ phải thu - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'cong_no_phai_thu',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_view_cong_no_phai_tra(self):
        """Xem công nợ phải trả của đối tác"""
        self.ensure_one()
        return {
            'name': f'Công nợ phải trả - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'cong_no_phai_tra',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
