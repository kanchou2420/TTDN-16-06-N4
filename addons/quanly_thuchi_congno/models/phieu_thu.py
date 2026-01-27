# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class PhieuThu(models.Model):
    _name = 'phieu_thu'
    _description = 'Phiếu Thu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Số phiếu', required=True, copy=False, default='New', tracking=True)
    date = fields.Date(string='Ngày thu', default=fields.Date.context_today, required=True, tracking=True)
    
    # Đối tác
    partner_id = fields.Many2one('res.partner', string='Đối tác', ondelete='restrict', tracking=True)
    partner_type = fields.Selection([
        ('customer', 'Khách hàng'),
        ('supplier', 'Nhà cung cấp'),
        ('employee', 'Nhân viên'),
        ('other', 'Khác'),
    ], string='Loại đối tác', default='customer')
    
    # Phòng ban & Nhân viên
    phonban_id = fields.Many2one('phong_ban', string='Phòng ban', ondelete='set null')
    nhan_vien_id = fields.Many2one('nhan_vien', string='Người lập', ondelete='set null',
                                    default=lambda self: self._get_default_employee())
    
    # Loại thu
    loai_thu = fields.Selection([
        ('thu_cong_no', 'Thu công nợ'),
        ('thu_tam_ung', 'Thu hoàn tạm ứng'),
        ('thu_thanh_ly', 'Thu thanh lý tài sản'),
        ('thu_khac', 'Thu khác'),
    ], string='Loại thu', required=True, default='thu_cong_no', tracking=True)
    
    # Số tiền
    amount = fields.Monetary(string='Số tiền', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', required=True,
                                  default=lambda self: self.env.company.currency_id)
    
    # Phương thức thanh toán
    phuong_thuc = fields.Selection([
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
        ('the', 'Thẻ'),
    ], string='Phương thức', default='tien_mat', required=True)
    
    # Liên kết với ngân sách
    ngan_sach_id = fields.Many2one('ngan_sach', string='Ngân sách', ondelete='set null',
                                    domain="[('trang_thai', 'in', ['duyet', 'dang_thuc_hien'])]")
    phan_bo_id = fields.Many2one('phan_bo_ngan_sach', string='Phân bổ ngân sách', ondelete='set null',
                                  domain="[('ngan_sach_id', '=', ngan_sach_id)]")
    
    # Liên kết với công nợ
    cong_no_id = fields.Many2one('cong_no_phai_thu', string='Công nợ phải thu', ondelete='set null',
                                  domain="[('partner_id', '=', partner_id), ('state', '=', 'open')]")
    
    # Liên kết với thanh lý tài sản
    thanh_ly_id = fields.Many2one('thanh_ly_tai_san', string='Thanh lý tài sản', ondelete='set null')
    
    # Ghi chú
    note = fields.Text(string='Ghi chú')
    ly_do = fields.Char(string='Lý do thu', required=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('posted', 'Đã ghi sổ'),
        ('cancel', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    # Người duyệt
    nguoi_duyet_id = fields.Many2one('res.users', string='User duyệt', ondelete='set null')
    nguoi_duyet_nhansu_id = fields.Many2one('nhan_vien', string='Người duyệt',
                                             domain="[('is_lanh_dao', '=', True)]",
                                             ondelete='set null',
                                             help='Chỉ lãnh đạo mới được duyệt phiếu thu')
    ngay_duyet = fields.Datetime(string='Ngày duyệt')
    
    # Theo dõi thực hiện ngân sách tự động tạo
    theo_doi_ngan_sach_id = fields.Many2one('theo_doi_thuc_hien_ngan_sach', string='Theo dõi ngân sách', 
                                             ondelete='set null', readonly=True)

    @api.model
    def _get_default_employee(self):
        """Lấy nhân viên mặc định (cần chọn thủ công)"""
        # Model nhan_vien không có trường user_id
        return False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('phieu.thu') or 'PT/0000'
            vals['name'] = seq
        return super().create(vals)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Tự động điền loại đối tác"""
        if self.partner_id:
            if self.partner_id.customer_rank > 0:
                self.partner_type = 'customer'
            elif self.partner_id.supplier_rank > 0:
                self.partner_type = 'supplier'
            else:
                self.partner_type = 'other'
            # Reset công nợ khi đổi đối tác
            self.cong_no_id = False

    @api.onchange('cong_no_id')
    def _onchange_cong_no_id(self):
        """Tự động điền số tiền từ công nợ còn lại"""
        if self.cong_no_id:
            self.amount = self.cong_no_id.residual
            self.ly_do = f"Thu công nợ - {self.cong_no_id.partner_id.name}"

    @api.onchange('ngan_sach_id')
    def _onchange_ngan_sach_id(self):
        """Reset phân bổ khi đổi ngân sách"""
        self.phan_bo_id = False

    def action_confirm(self):
        """Xác nhận phiếu thu"""
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Số tiền phải lớn hơn 0!')
            rec.write({'state': 'confirmed'})
        return True

    def action_post(self):
        """Ghi sổ phiếu thu"""
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError('Chỉ có thể ghi sổ phiếu đã xác nhận!')
            
            vals = {
                'state': 'posted',
                'nguoi_duyet_id': self.env.uid,
                'ngay_duyet': fields.Datetime.now(),
            }
            
            # Cập nhật công nợ nếu là thu công nợ
            if rec.loai_thu == 'thu_cong_no' and rec.cong_no_id:
                rec.cong_no_id.action_pay(rec.amount, rec.id)
            
            # Tạo bản ghi theo dõi ngân sách nếu có liên kết
            if rec.ngan_sach_id and rec.phan_bo_id:
                theo_doi = self.env['theo_doi_thuc_hien_ngan_sach'].create({
                    'ma_giao_dich': rec.name,
                    'ngan_sach_id': rec.ngan_sach_id.id,
                    'phan_bo_id': rec.phan_bo_id.id,
                    'loai_giao_dich': 'thu_hoi',
                    'loai_chi_tiet': 'thanh_ly_ts' if rec.loai_thu == 'thu_thanh_ly' else 'khac',
                    'ngay_giao_dich': rec.date,
                    'so_tien_thuc_te': -rec.amount,  # Số âm vì là thu
                    'noi_dung': rec.ly_do or f'Thu tiền từ {rec.partner_id.name or ""}',
                    'phong_ban_id': rec.phonban_id.id if rec.phonban_id else False,
                    'trang_thai': 'hoan_thanh',
                    'nguoi_thuc_hien': self.env.uid,
                })
                vals['theo_doi_ngan_sach_id'] = theo_doi.id
            
            rec.write(vals)
        return True

    def action_cancel(self):
        """Hủy phiếu thu"""
        for rec in self:
            if rec.state == 'posted':
                # Hủy theo dõi ngân sách
                if rec.theo_doi_ngan_sach_id:
                    rec.theo_doi_ngan_sach_id.unlink()
            rec.write({
                'state': 'cancel',
                'theo_doi_ngan_sach_id': False,
            })
        return True

    def action_draft(self):
        """Đặt lại về nháp"""
        for rec in self:
            if rec.state == 'cancel':
                rec.write({'state': 'draft'})
        return True

    def unlink(self):
        """Chỉ cho phép xóa phiếu nháp hoặc đã hủy"""
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError('Không thể xóa phiếu đã xác nhận hoặc đã ghi sổ!')
        return super().unlink()
