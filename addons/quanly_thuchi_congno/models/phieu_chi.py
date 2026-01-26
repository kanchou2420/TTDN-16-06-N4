# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class PhieuChi(models.Model):
    _name = 'phieu_chi'
    _description = 'Phiếu Chi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Số phiếu', required=True, copy=False, default='New', tracking=True)
    date = fields.Date(string='Ngày chi', default=fields.Date.context_today, required=True, tracking=True)
    
    # Đối tác
    partner_id = fields.Many2one('res.partner', string='Đối tác', ondelete='restrict', tracking=True)
    partner_type = fields.Selection([
        ('customer', 'Khách hàng'),
        ('supplier', 'Nhà cung cấp'),
        ('employee', 'Nhân viên'),
        ('other', 'Khác'),
    ], string='Loại đối tác', default='supplier')
    
    # Phòng ban & Nhân viên
    phonban_id = fields.Many2one('phong_ban', string='Phòng ban', ondelete='set null')
    nhan_vien_id = fields.Many2one('nhan_vien', string='Người lập', ondelete='set null',
                                    default=lambda self: self._get_default_employee())
    nguoi_nhan = fields.Char(string='Người nhận tiền')
    
    # Loại chi
    loai_chi = fields.Selection([
        ('chi_cong_no', 'Chi trả công nợ'),
        ('chi_tam_ung', 'Chi tạm ứng'),
        ('chi_mua_sam', 'Chi mua sắm tài sản'),
        ('chi_luong', 'Chi lương'),
        ('chi_van_phong', 'Chi văn phòng phẩm'),
        ('chi_khac', 'Chi khác'),
    ], string='Loại chi', required=True, default='chi_cong_no', tracking=True)
    
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
    du_toan_chi_id = fields.Many2one('du_toan_chi', string='Dự toán chi', ondelete='set null',
                                      domain="[('ngan_sach_id', '=', ngan_sach_id), ('trang_thai', '=', 'duyet')]")
    
    # Liên kết với công nợ
    # FIX: Simplified domain - không sử dụng partner_id vì có thể null
    cong_no_id = fields.Many2one('cong_no_phai_tra', string='Công nợ phải trả', ondelete='set null')
    
    # Liên kết với tài sản (nếu chi mua sắm)
    tai_san_id = fields.Many2one('tai_san', string='Tài sản', ondelete='set null')
    
    # Ghi chú
    note = fields.Text(string='Ghi chú')
    ly_do = fields.Char(string='Lý do chi', required=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('approved', 'Đã duyệt'),
        ('posted', 'Đã ghi sổ'),
        ('cancel', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True, tracking=True)
    
    # Người duyệt
    nguoi_xac_nhan_id = fields.Many2one('res.users', string='Người xác nhận', ondelete='set null')
    ngay_xac_nhan = fields.Datetime(string='Ngày xác nhận')
    nguoi_duyet_id = fields.Many2one('res.users', string='Người duyệt', ondelete='set null')
    ngay_duyet = fields.Datetime(string='Ngày duyệt')
    
    # Theo dõi thực hiện ngân sách tự động tạo
    theo_doi_ngan_sach_id = fields.Many2one('theo_doi_thuc_hien_ngan_sach', string='Theo dõi ngân sách', 
                                             ondelete='set null', readonly=True)
    
    # Kiểm tra ngân sách
    vuot_ngan_sach = fields.Boolean(string='Vượt ngân sách', compute='_compute_vuot_ngan_sach', store=True)
    ngan_sach_con_lai = fields.Monetary(string='Ngân sách còn lại', compute='_compute_ngan_sach_con_lai')

    @api.model
    def _get_default_employee(self):
        """Lấy nhân viên mặc định (cần chọn thủ công)"""
        # Model nhan_vien không có trường user_id
        return False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('phieu.chi') or 'PC/0000'
            vals['name'] = seq
        return super().create(vals)

    @api.depends('phan_bo_id', 'amount')
    def _compute_vuot_ngan_sach(self):
        for rec in self:
            if rec.phan_bo_id and rec.amount:
                rec.vuot_ngan_sach = rec.amount > rec.phan_bo_id.so_tien_con_lai
            else:
                rec.vuot_ngan_sach = False

    @api.depends('phan_bo_id')
    def _compute_ngan_sach_con_lai(self):
        for rec in self:
            if rec.phan_bo_id:
                rec.ngan_sach_con_lai = rec.phan_bo_id.so_tien_con_lai
            else:
                rec.ngan_sach_con_lai = 0

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Tự động điền loại đối tác"""
        if self.partner_id:
            if self.partner_id.supplier_rank > 0:
                self.partner_type = 'supplier'
            elif self.partner_id.customer_rank > 0:
                self.partner_type = 'customer'
            else:
                self.partner_type = 'other'
            # Reset công nợ khi đổi đối tác
            self.cong_no_id = False

    @api.onchange('cong_no_id')
    def _onchange_cong_no_id(self):
        """Tự động điền số tiền từ công nợ còn lại"""
        if self.cong_no_id:
            self.amount = self.cong_no_id.residual
            self.ly_do = f"Chi trả công nợ - {self.cong_no_id.partner_id.name}"

    @api.onchange('ngan_sach_id')
    def _onchange_ngan_sach_id(self):
        """Reset phân bổ khi đổi ngân sách"""
        self.phan_bo_id = False
        self.du_toan_chi_id = False

    @api.onchange('loai_chi')
    def _onchange_loai_chi(self):
        """Map loại chi với loại chi tiết của ngân sách"""
        mapping = {
            'chi_mua_sam': 'mua_tai_san',
            'chi_luong': 'luong',
            'chi_van_phong': 'khac',
        }
        # Có thể sử dụng để lọc dự toán chi phù hợp

    def action_confirm(self):
        """Xác nhận phiếu chi"""
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Số tiền phải lớn hơn 0!')
            rec.write({
                'state': 'confirmed',
                'nguoi_xac_nhan_id': self.env.uid,
                'ngay_xac_nhan': fields.Datetime.now(),
            })
        return True

    def action_approve(self):
        """Duyệt phiếu chi"""
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError('Chỉ có thể duyệt phiếu đã xác nhận!')
            
            # Kiểm tra ngân sách nếu có liên kết
            if rec.phan_bo_id and rec.vuot_ngan_sach:
                raise ValidationError(
                    f'Số tiền chi ({rec.amount:,.0f}) vượt quá ngân sách còn lại ({rec.ngan_sach_con_lai:,.0f})!\n'
                    'Vui lòng điều chỉnh số tiền hoặc chọn phân bổ ngân sách khác.'
                )
            
            rec.write({
                'state': 'approved',
                'nguoi_duyet_id': self.env.uid,
                'ngay_duyet': fields.Datetime.now(),
            })
        return True

    def action_post(self):
        """Ghi sổ phiếu chi"""
        for rec in self:
            if rec.state != 'approved':
                raise UserError('Chỉ có thể ghi sổ phiếu đã được duyệt!')
            
            vals = {'state': 'posted'}
            
            # FIX: CẬP NHẬT DỰ TOÁN CHI
            # Ghi nhận số tiền đã chi thực tế vào dự toán
            if rec.du_toan_chi_id:
                try:
                    new_da_chi = rec.du_toan_chi_id.da_chi_thuc_te + rec.amount
                    rec.du_toan_chi_id.write({'da_chi_thuc_te': new_da_chi})
                except Exception as e:
                    pass
            
            # Tạo bản ghi theo dõi ngân sách nếu có liên kết
            if rec.ngan_sach_id and rec.phan_bo_id:
                try:
                    loai_chi_tiet_map = {
                        'chi_mua_sam': 'mua_tai_san',
                        'chi_luong': 'luong',
                        'chi_van_phong': 'khac',
                        'chi_cong_no': 'khac',
                        'chi_tam_ung': 'khac',
                        'chi_khac': 'khac',
                    }
                    theo_doi = self.env['theo_doi_thuc_hien_ngan_sach'].create({
                        'ma_giao_dich': rec.name,
                        'ngan_sach_id': rec.ngan_sach_id.id,
                        'phan_bo_id': rec.phan_bo_id.id,
                        'loai_giao_dich': 'chi_tieu',
                        'loai_chi_tiet': loai_chi_tiet_map.get(rec.loai_chi, 'khac'),
                        'ngay_giao_dich': rec.date,
                        'so_tien_thuc_te': rec.amount,
                        'noi_dung': rec.ly_do or f'Chi tiền cho {rec.partner_id.name or rec.nguoi_nhan or ""}',
                        'phong_ban_id': rec.phonban_id.id if rec.phonban_id else False,
                        'tai_san_id': rec.tai_san_id.id if rec.tai_san_id else False,
                        'trang_thai': 'hoan_thanh',
                        'nguoi_thuc_hien': self.env.uid,
                    })
                    vals['theo_doi_ngan_sach_id'] = theo_doi.id
                except Exception as e:
                    pass
            
            rec.write(vals)
        return True

    def action_cancel(self):
        """Hủy phiếu chi"""
        for rec in self:
            if rec.state == 'posted':
                # Hoàn tác công nợ nếu cần
                if rec.loai_chi == 'chi_cong_no' and rec.cong_no_id:
                    rec.cong_no_id.action_reverse_pay(rec.amount)
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
