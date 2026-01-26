# -*- coding: utf-8 -*-
"""
Model: Công Nợ Phải Trả (Payable Accounts)

Chức năng: Quản lý công nợ phải trả tới nhà cung cấp, nhân viên, v.v
Luồng: Tạo công nợ → Trả tiền (phiếu chi) → Đóng công nợ

FIX: Thêm model này để hỗ trợ liên kết phiếu chi → công nợ phải trả
Từ đó có thể theo dõi lịch sử thanh toán công nợ.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class CongNoPhaiTra(models.Model):
    _name = 'cong_no_phai_tra'
    _description = 'Công nợ phải trả'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'due_date asc, date desc, id desc'
    _rec_name = 'display_name'

    # ==== THÔNG TIN CƠ BẢN ====
    name = fields.Char(
        string='Mã công nợ',
        required=True,
        copy=False,
        default='New',
        tracking=True,
        help='Tự động tạo từ sequence'
    )
    display_name = fields.Char(
        string='Tên hiển thị',
        compute='_compute_display_name',
        store=True
    )

    # ==== ĐỐI TƯỢNG CÔNG NỢ ====
    partner_id = fields.Many2one(
        'res.partner',
        string='Nhà cung cấp/Đối tác',
        required=True,
        ondelete='restrict',
        tracking=True
    )

    # ==== NGUỒN GỐC CÔNG NỢ ====
    origin = fields.Char(
        string='Nguồn gốc',
        help='Số hóa đơn, số đơn đặt hàng, v.v'
    )
    origin_type = fields.Selection(
        [
            ('invoice', 'Hóa đơn'),
            ('bill', 'Phiếu yêu cầu thanh toán'),
            ('po', 'Đơn đặt hàng'),
            ('contract', 'Hợp đồng'),
            ('other', 'Khác'),
        ],
        string='Loại nguồn gốc',
        default='invoice'
    )

    # ==== NGÀY THÁNG ====
    date = fields.Date(
        string='Ngày tạo nợ',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    due_date = fields.Date(
        string='Ngày đáo hạn',
        required=True,
        tracking=True
    )

    # ==== SỐ TIỀN ====
    amount = fields.Monetary(
        string='Số tiền gốc',
        required=True,
        tracking=True,
        help='Tổng số tiền phải trả'
    )
    paid_amount = fields.Monetary(
        string='Đã trả',
        compute='_compute_paid_amount',
        store=True,
        help='Tổng số tiền đã thanh toán'
    )
    residual = fields.Monetary(
        string='Còn nợ',
        compute='_compute_residual',
        store=True,
        help='Số tiền còn phải trả'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    # ==== TRẠNG THÁI ====
    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('open', 'Đang nợ'),
            ('partial', 'Trả một phần'),
            ('paid', 'Đã trả đủ'),
            ('cancelled', 'Đã hủy'),
        ],
        string='Trạng thái',
        default='draft',
        required=True,
        tracking=True
    )

    # ==== TÌNH TRẠNG QUÁHẠN ====
    is_overdue = fields.Boolean(
        string='Quá hạn',
        compute='_compute_is_overdue',
        store=True
    )
    overdue_days = fields.Integer(
        string='Số ngày quá hạn',
        compute='_compute_overdue_days'
    )

    # ==== PHÒNG BAN & NHÂN VIÊN ====
    phonban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban phụ trách',
        ondelete='set null'
    )
    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên phụ trách',
        ondelete='set null'
    )

    # ==== LIÊN KẾT VỚI PHIẾU CHI ====
    phieu_chi_ids = fields.One2many(
        'phieu_chi',
        'cong_no_phai_tra_id',
        string='Phiếu chi thanh toán',
        help='Danh sách phiếu chi thanh toán công nợ này'
    )
    phieu_chi_count = fields.Integer(
        string='Số phiếu chi',
        compute='_compute_phieu_chi_count'
    )

    # ==== LỊCH SỬ THANH TOÁN ====
    payment_line_ids = fields.One2many(
        'cong_no_phai_tra.payment',
        'cong_no_id',
        string='Lịch sử thanh toán'
    )

    # ==== GHI CHÚ ====
    note = fields.Text(string='Ghi chú')
    ly_do = fields.Char(string='Lý do tạo công nợ')

    # ==== NGƯỜI TẠO ====
    nguoi_tao = fields.Many2one(
        'res.users',
        string='Người tạo',
        default=lambda self: self.env.user,
        readonly=True
    )
    ngay_tao = fields.Datetime(
        string='Ngày tạo',
        default=fields.Datetime.now,
        readonly=True
    )

    # ==== COMPUTE & ONCHANGE ====

    @api.depends('name', 'partner_id')
    def _compute_display_name(self):
        for rec in self:
            if rec.partner_id:
                rec.display_name = f"{rec.name} - {rec.partner_id.name}"
            else:
                rec.display_name = rec.name

    @api.model
    def create(self, vals):
        """Tự động tạo mã công nợ từ sequence"""
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('cong.no.phai.tra') or 'CNT/0000'
            vals['name'] = seq
        return super().create(vals)

    @api.depends('payment_line_ids.amount')
    def _compute_paid_amount(self):
        """Tính tổng tiền đã trả từ các phiếu chi"""
        for rec in self:
            rec.paid_amount = sum(
                rec.phieu_chi_ids.filtered(
                    lambda p: p.state in ('approved', 'posted')
                ).mapped('amount')
            )

    @api.depends('amount', 'paid_amount')
    def _compute_residual(self):
        """Tính số tiền còn nợ"""
        for rec in self:
            rec.residual = rec.amount - rec.paid_amount

    @api.depends('due_date', 'state')
    def _compute_is_overdue(self):
        """Kiểm tra quá hạn (so với ngày hôm nay)"""
        today = fields.Date.today()
        for rec in self:
            # Chỉ tính quá hạn nếu vẫn còn nợ
            rec.is_overdue = (
                rec.state in ('open', 'partial')
                and rec.due_date
                and rec.due_date < today
            )

    @api.depends('due_date')
    def _compute_overdue_days(self):
        """Tính số ngày quá hạn"""
        today = fields.Date.today()
        for rec in self:
            if rec.is_overdue:
                delta = today - rec.due_date
                rec.overdue_days = delta.days
            else:
                rec.overdue_days = 0

    @api.depends('phieu_chi_ids')
    def _compute_phieu_chi_count(self):
        """Đếm số phiếu chi"""
        for rec in self:
            rec.phieu_chi_count = len(rec.phieu_chi_ids)

    # ==== VALIDATION ====

    @api.constrains('due_date', 'date')
    def _check_dates(self):
        """Ngày đáo hạn phải >= ngày tạo nợ"""
        for rec in self:
            if rec.due_date < rec.date:
                raise ValidationError('Ngày đáo hạn phải >= ngày tạo nợ!')

    @api.constrains('amount')
    def _check_amount(self):
        """Số tiền phải > 0"""
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Số tiền phải lớn hơn 0!')

    # ==== ACTIONS ====

    def action_confirm(self):
        """Xác nhận công nợ từ nháp → đang nợ"""
        self.write({'state': 'open'})

    def action_cancel(self):
        """Hủy công nợ"""
        for rec in self:
            if rec.state == 'paid':
                raise ValidationError('Không thể hủy công nợ đã trả đủ!')
            rec.write({'state': 'cancelled'})

    def _update_payment(self, amount, phieu_chi_id):
        """
        FIX: Hàm này được gọi từ phieu_chi.action_post()
        để cập nhật tình trạng công nợ khi ghi sổ phiếu chi.
        
        Parameters:
            amount: Số tiền thanh toán
            phieu_chi_id: ID phiếu chi (để tạo lịch sử)
        """
        for rec in self:
            # Kiểm tra số tiền thanh toán hợp lệ
            if amount <= 0:
                return

            if amount > rec.residual:
                return

            # Cập nhật trạng thái dựa trên số tiền còn nợ
            new_residual = rec.residual - amount

            if new_residual <= 0:
                new_state = 'paid'
            elif new_residual < rec.amount:
                new_state = 'partial'
            else:
                new_state = 'open'

            rec.write({
                'state': new_state,
            })


class CongNoPhaiTraPayment(models.Model):
    """
    Lịch sử thanh toán của một công nợ phải trả.
    Mỗi lần lập phiếu chi để trả nợ, sẽ tạo một bản ghi ở đây.
    """
    _name = 'cong_no_phai_tra.payment'
    _description = 'Lịch sử thanh toán công nợ phải trả'
    _order = 'date desc'

    cong_no_id = fields.Many2one(
        'cong_no_phai_tra',
        string='Công nợ',
        required=True,
        ondelete='cascade'
    )
    amount = fields.Monetary(
        string='Số tiền thanh toán',
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='cong_no_id.currency_id',
        store=True
    )
    date = fields.Date(
        string='Ngày thanh toán',
        required=True
    )
    phieu_chi_id = fields.Many2one(
        'phieu_chi',
        string='Phiếu chi liên quan'
    )
    note = fields.Text(string='Ghi chú')
