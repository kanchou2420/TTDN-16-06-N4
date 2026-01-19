# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class CongNoPhaiThu(models.Model):
    _name = 'cong_no_phai_thu'
    _description = 'Công nợ phải thu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'due_date asc, date desc, id desc'
    _rec_name = 'display_name'

    name = fields.Char(string='Mã công nợ', required=True, copy=False, default='New', tracking=True)
    display_name = fields.Char(string='Tên hiển thị', compute='_compute_display_name', store=True)
    
    partner_id = fields.Many2one('res.partner', string='Khách hàng', required=True, 
                                  ondelete='restrict', tracking=True)
    
    # Nguồn gốc công nợ
    origin = fields.Char(string='Nguồn gốc', help='Số hóa đơn, đơn hàng...')
    origin_type = fields.Selection([
        ('invoice', 'Hóa đơn'),
        ('order', 'Đơn hàng'),
        ('contract', 'Hợp đồng'),
        ('other', 'Khác'),
    ], string='Loại nguồn gốc', default='invoice')
    
    # Ngày
    date = fields.Date(string='Ngày tạo nợ', default=fields.Date.context_today, required=True, tracking=True)
    due_date = fields.Date(string='Ngày đáo hạn', required=True, tracking=True)
    
    # Số tiền
    amount = fields.Monetary(string='Số tiền gốc', required=True, tracking=True)
    paid_amount = fields.Monetary(string='Đã thu', compute='_compute_paid_amount', store=True)
    residual = fields.Monetary(string='Còn nợ', compute='_compute_residual', store=True)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', required=True,
                                  default=lambda self: self.env.company.currency_id)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('open', 'Đang nợ'),
        ('partial', 'Thu một phần'),
        ('paid', 'Đã thu đủ'),
        ('cancel', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    # Tình trạng quá hạn
    is_overdue = fields.Boolean(string='Quá hạn', compute='_compute_is_overdue', store=True)
    overdue_days = fields.Integer(string='Số ngày quá hạn', compute='_compute_overdue_days')
    
    # Phòng ban phụ trách
    phonban_id = fields.Many2one('phong_ban', string='Phòng ban phụ trách', ondelete='set null')
    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên phụ trách', ondelete='set null')
    
    # Liên kết với phiếu thu
    phieu_thu_ids = fields.One2many('phieu_thu', 'cong_no_id', string='Phiếu thu liên quan')
    phieu_thu_count = fields.Integer(string='Số phiếu thu', compute='_compute_phieu_thu_count')
    
    # Lịch sử thanh toán
    payment_line_ids = fields.One2many('cong_no_phai_thu.payment', 'cong_no_id', string='Lịch sử thanh toán')
    
    note = fields.Text(string='Ghi chú')

    @api.depends('name', 'partner_id')
    def _compute_display_name(self):
        for rec in self:
            if rec.partner_id:
                rec.display_name = f"{rec.name} - {rec.partner_id.name}"
            else:
                rec.display_name = rec.name

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('cong.no.phai.thu') or 'CNT/0000'
            vals['name'] = seq
        return super().create(vals)

    @api.depends('payment_line_ids.amount')
    def _compute_paid_amount(self):
        for rec in self:
            rec.paid_amount = sum(rec.payment_line_ids.filtered(lambda p: p.state == 'done').mapped('amount'))

    @api.depends('amount', 'paid_amount')
    def _compute_residual(self):
        for rec in self:
            rec.residual = rec.amount - rec.paid_amount

    @api.depends('due_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_overdue = rec.state in ('open', 'partial') and rec.due_date and rec.due_date < today

    @api.depends('due_date')
    def _compute_overdue_days(self):
        today = fields.Date.today()
        for rec in self:
            if rec.due_date and rec.due_date < today:
                rec.overdue_days = (today - rec.due_date).days
            else:
                rec.overdue_days = 0

    def _compute_phieu_thu_count(self):
        for rec in self:
            rec.phieu_thu_count = len(rec.phieu_thu_ids)

    def action_confirm(self):
        """Xác nhận công nợ"""
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Số tiền phải lớn hơn 0!')
            rec.write({'state': 'open'})
        return True

    def action_pay(self, amount, phieu_thu_id=False):
        """Ghi nhận thanh toán từ phiếu thu"""
        for rec in self:
            if rec.state not in ('open', 'partial'):
                raise UserError('Chỉ có thể thu công nợ đang mở!')
            
            if amount > rec.residual:
                raise ValidationError(f'Số tiền thu ({amount:,.0f}) vượt quá công nợ còn lại ({rec.residual:,.0f})!')
            
            # Tạo dòng thanh toán
            self.env['cong_no_phai_thu.payment'].create({
                'cong_no_id': rec.id,
                'date': fields.Date.today(),
                'amount': amount,
                'phieu_thu_id': phieu_thu_id,
                'state': 'done',
            })
            
            # Cập nhật trạng thái
            new_residual = rec.residual - amount
            if new_residual <= 0:
                rec.state = 'paid'
            else:
                rec.state = 'partial'
        return True

    def action_reverse_pay(self, amount):
        """Hoàn tác thanh toán (khi hủy phiếu thu)"""
        for rec in self:
            # Tìm và xóa dòng thanh toán tương ứng
            payment = rec.payment_line_ids.filtered(
                lambda p: p.amount == amount and p.state == 'done'
            )[:1]
            if payment:
                payment.unlink()
            
            # Cập nhật trạng thái
            if rec.paid_amount > 0:
                rec.state = 'partial'
            else:
                rec.state = 'open'
        return True

    def action_cancel(self):
        """Hủy công nợ"""
        for rec in self:
            if rec.paid_amount > 0:
                raise UserError('Không thể hủy công nợ đã có thanh toán!')
            rec.write({'state': 'cancel'})
        return True

    def action_view_phieu_thu(self):
        """Xem các phiếu thu liên quan"""
        self.ensure_one()
        return {
            'name': 'Phiếu Thu',
            'type': 'ir.actions.act_window',
            'res_model': 'phieu_thu',
            'view_mode': 'tree,form',
            'domain': [('cong_no_id', '=', self.id)],
            'context': {'default_cong_no_id': self.id, 'default_partner_id': self.partner_id.id},
        }


class CongNoPhaiThuPayment(models.Model):
    _name = 'cong_no_phai_thu.payment'
    _description = 'Lịch sử thanh toán công nợ phải thu'
    _order = 'date desc, id desc'

    cong_no_id = fields.Many2one('cong_no_phai_thu', string='Công nợ', required=True, ondelete='cascade')
    date = fields.Date(string='Ngày thanh toán', required=True, default=fields.Date.context_today)
    amount = fields.Monetary(string='Số tiền', required=True)
    currency_id = fields.Many2one('res.currency', related='cong_no_id.currency_id')
    phieu_thu_id = fields.Many2one('phieu_thu', string='Phiếu thu', ondelete='set null')
    note = fields.Char(string='Ghi chú')
    state = fields.Selection([('draft', 'Nháp'), ('done', 'Hoàn thành')], default='draft')


class CongNoPhaiTra(models.Model):
    _name = 'cong_no_phai_tra'
    _description = 'Công nợ phải trả'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'due_date asc, date desc, id desc'
    _rec_name = 'display_name'

    name = fields.Char(string='Mã công nợ', required=True, copy=False, default='New', tracking=True)
    display_name = fields.Char(string='Tên hiển thị', compute='_compute_display_name', store=True)
    
    partner_id = fields.Many2one('res.partner', string='Nhà cung cấp', required=True, 
                                  ondelete='restrict', tracking=True)
    
    # Nguồn gốc công nợ
    origin = fields.Char(string='Nguồn gốc', help='Số hóa đơn, đơn hàng...')
    origin_type = fields.Selection([
        ('invoice', 'Hóa đơn'),
        ('order', 'Đơn hàng'),
        ('contract', 'Hợp đồng'),
        ('other', 'Khác'),
    ], string='Loại nguồn gốc', default='invoice')
    
    # Ngày
    date = fields.Date(string='Ngày tạo nợ', default=fields.Date.context_today, required=True, tracking=True)
    due_date = fields.Date(string='Ngày đáo hạn', required=True, tracking=True)
    
    # Số tiền
    amount = fields.Monetary(string='Số tiền gốc', required=True, tracking=True)
    paid_amount = fields.Monetary(string='Đã trả', compute='_compute_paid_amount', store=True)
    residual = fields.Monetary(string='Còn nợ', compute='_compute_residual', store=True)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', required=True,
                                  default=lambda self: self.env.company.currency_id)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('open', 'Đang nợ'),
        ('partial', 'Trả một phần'),
        ('paid', 'Đã trả đủ'),
        ('cancel', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    # Tình trạng quá hạn
    is_overdue = fields.Boolean(string='Quá hạn', compute='_compute_is_overdue', store=True)
    overdue_days = fields.Integer(string='Số ngày quá hạn', compute='_compute_overdue_days')
    
    # Phòng ban phụ trách
    phonban_id = fields.Many2one('phong_ban', string='Phòng ban phụ trách', ondelete='set null')
    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên phụ trách', ondelete='set null')
    
    # Liên kết với phiếu chi
    phieu_chi_ids = fields.One2many('phieu_chi', 'cong_no_id', string='Phiếu chi liên quan')
    phieu_chi_count = fields.Integer(string='Số phiếu chi', compute='_compute_phieu_chi_count')
    
    # Lịch sử thanh toán
    payment_line_ids = fields.One2many('cong_no_phai_tra.payment', 'cong_no_id', string='Lịch sử thanh toán')
    
    note = fields.Text(string='Ghi chú')

    @api.depends('name', 'partner_id')
    def _compute_display_name(self):
        for rec in self:
            if rec.partner_id:
                rec.display_name = f"{rec.name} - {rec.partner_id.name}"
            else:
                rec.display_name = rec.name

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('cong.no.phai.tra') or 'CNTR/0000'
            vals['name'] = seq
        return super().create(vals)

    @api.depends('payment_line_ids.amount')
    def _compute_paid_amount(self):
        for rec in self:
            rec.paid_amount = sum(rec.payment_line_ids.filtered(lambda p: p.state == 'done').mapped('amount'))

    @api.depends('amount', 'paid_amount')
    def _compute_residual(self):
        for rec in self:
            rec.residual = rec.amount - rec.paid_amount

    @api.depends('due_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_overdue = rec.state in ('open', 'partial') and rec.due_date and rec.due_date < today

    @api.depends('due_date')
    def _compute_overdue_days(self):
        today = fields.Date.today()
        for rec in self:
            if rec.due_date and rec.due_date < today:
                rec.overdue_days = (today - rec.due_date).days
            else:
                rec.overdue_days = 0

    def _compute_phieu_chi_count(self):
        for rec in self:
            rec.phieu_chi_count = len(rec.phieu_chi_ids)

    def action_confirm(self):
        """Xác nhận công nợ"""
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Số tiền phải lớn hơn 0!')
            rec.write({'state': 'open'})
        return True

    def action_pay(self, amount, phieu_chi_id=False):
        """Ghi nhận thanh toán từ phiếu chi"""
        for rec in self:
            if rec.state not in ('open', 'partial'):
                raise UserError('Chỉ có thể trả công nợ đang mở!')
            
            if amount > rec.residual:
                raise ValidationError(f'Số tiền trả ({amount:,.0f}) vượt quá công nợ còn lại ({rec.residual:,.0f})!')
            
            # Tạo dòng thanh toán
            self.env['cong_no_phai_tra.payment'].create({
                'cong_no_id': rec.id,
                'date': fields.Date.today(),
                'amount': amount,
                'phieu_chi_id': phieu_chi_id,
                'state': 'done',
            })
            
            # Cập nhật trạng thái
            new_residual = rec.residual - amount
            if new_residual <= 0:
                rec.state = 'paid'
            else:
                rec.state = 'partial'
        return True

    def action_reverse_pay(self, amount):
        """Hoàn tác thanh toán (khi hủy phiếu chi)"""
        for rec in self:
            # Tìm và xóa dòng thanh toán tương ứng
            payment = rec.payment_line_ids.filtered(
                lambda p: p.amount == amount and p.state == 'done'
            )[:1]
            if payment:
                payment.unlink()
            
            # Cập nhật trạng thái
            if rec.paid_amount > 0:
                rec.state = 'partial'
            else:
                rec.state = 'open'
        return True

    def action_cancel(self):
        """Hủy công nợ"""
        for rec in self:
            if rec.paid_amount > 0:
                raise UserError('Không thể hủy công nợ đã có thanh toán!')
            rec.write({'state': 'cancel'})
        return True

    def action_view_phieu_chi(self):
        """Xem các phiếu chi liên quan"""
        self.ensure_one()
        return {
            'name': 'Phiếu Chi',
            'type': 'ir.actions.act_window',
            'res_model': 'phieu_chi',
            'view_mode': 'tree,form',
            'domain': [('cong_no_id', '=', self.id)],
            'context': {'default_cong_no_id': self.id, 'default_partner_id': self.partner_id.id},
        }


class CongNoPhaiTraPayment(models.Model):
    _name = 'cong_no_phai_tra.payment'
    _description = 'Lịch sử thanh toán công nợ phải trả'
    _order = 'date desc, id desc'

    cong_no_id = fields.Many2one('cong_no_phai_tra', string='Công nợ', required=True, ondelete='cascade')
    date = fields.Date(string='Ngày thanh toán', required=True, default=fields.Date.context_today)
    amount = fields.Monetary(string='Số tiền', required=True)
    currency_id = fields.Many2one('res.currency', related='cong_no_id.currency_id')
    phieu_chi_id = fields.Many2one('phieu_chi', string='Phiếu chi', ondelete='set null')
    note = fields.Char(string='Ghi chú')
    state = fields.Selection([('draft', 'Nháp'), ('done', 'Hoàn thành')], default='draft')
