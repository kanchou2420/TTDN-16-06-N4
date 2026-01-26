# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TheoDoiThucHienNganSach(models.Model):
    _name = 'theo_doi_thuc_hien_ngan_sach'
    _description = 'Theo dõi thực hiện ngân sách'
    _rec_name = 'ma_giao_dich'
    _order = 'ngay_giao_dich desc, id desc'

    ma_giao_dich = fields.Char('Mã giao dịch', required=True, copy=False)
    
    ngan_sach_id = fields.Many2one('ngan_sach', string='Ngân sách', required=True, ondelete='restrict')
    phan_bo_id = fields.Many2one('phan_bo_ngan_sach', string='Phân bổ ngân sách', required=True, ondelete='restrict')
    
    loai_giao_dich = fields.Selection([
        ('chi_tieu', 'Chi tiêu'),
        ('thu_hoi', 'Thu hồi'),
        ('dieu_chinh', 'Điều chỉnh'),
    ], string='Loại giao dịch', required=True, default='chi_tieu')
    
    loai_chi_tiet = fields.Selection([
        ('mua_tai_san', 'Mua tài sản mới'),
        ('khau_hao_ts', 'Chi phí khấu hao'),
        ('thanh_ly_ts', 'Thu từ thanh lý tài sản'),
        ('bao_duong', 'Bảo dưỡng tài sản'),
        ('sua_chua', 'Sửa chữa tài sản'),
        ('luong', 'Lương nhân viên'),
        ('phuc_loi', 'Phúc lợi'),
        ('dao_tao', 'Đào tạo'),
        ('khac', 'Khác'),
    ], string='Loại chi tiết')
    
    ngay_giao_dich = fields.Date('Ngày giao dịch', required=True, default=fields.Date.today)
    
    # Liên kết với tài sản (nếu có)
    tai_san_id = fields.Many2one('tai_san', string='Tài sản liên quan')
    thanh_ly_ts_id = fields.Many2one('thanh_ly_tai_san', string='Thanh lý tài sản')
    danh_muc_ts_id = fields.Many2one('danh_muc_tai_san', string='Danh mục tài sản')
    
    # Liên kết với phòng ban
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban')
    
    so_tien_du_kien = fields.Float('Số tiền dự kiến', default=0)
    so_tien_thuc_te = fields.Float('Số tiền thực tế', required=True, default=0)
    chenh_lech = fields.Float('Chênh lệch', compute='_compute_chenh_lech', store=True)
    
    don_vi_tien_te = fields.Selection([
        ('vnd', 'VNĐ'),
        ('usd', 'USD'),
    ], string='Đơn vị tiền tệ', default='vnd', required=True)
    
    noi_dung = fields.Text('Nội dung giao dịch', required=True)
    ghi_chu = fields.Text('Ghi chú')
    
    # Chứng từ
    so_chung_tu = fields.Char('Số chứng từ')
    file_chung_tu = fields.Binary('File chứng từ', attachment=True)
    file_chung_tu_filename = fields.Char('Tên file chứng từ')
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối'),
        ('hoan_thanh', 'Hoàn thành'),
    ], string='Trạng thái', default='nhap', required=True)
    
    nguoi_thuc_hien = fields.Many2one('res.users', string='Người thực hiện', default=lambda self: self.env.user)
    nguoi_duyet = fields.Many2one('res.users', string='Người duyệt')
    ngay_tao = fields.Date('Ngày tạo', default=fields.Date.today)
    ngay_duyet = fields.Date('Ngày duyệt')
    
    @api.depends('so_tien_du_kien', 'so_tien_thuc_te')
    def _compute_chenh_lech(self):
        for record in self:
            record.chenh_lech = record.so_tien_thuc_te - record.so_tien_du_kien
    
    @api.constrains('so_tien_thuc_te')
    def _check_so_tien_thuc_te(self):
        for record in self:
            if record.loai_giao_dich == 'chi_tieu' and record.so_tien_thuc_te <= 0:
                raise ValidationError('Số tiền thực tế phải lớn hơn 0!')
    
    @api.constrains('so_tien_thuc_te', 'phan_bo_id')
    def _check_so_tien_con_lai(self):
        for record in self:
            if record.loai_giao_dich == 'chi_tieu':
                if record.phan_bo_id.so_tien_con_lai < record.so_tien_thuc_te:
                    raise ValidationError(
                        f'Số tiền chi vượt quá ngân sách còn lại của phân bổ!\n'
                        f'Còn lại: {record.phan_bo_id.so_tien_con_lai:,.0f} {record.don_vi_tien_te.upper()}'
                    )
    
    def action_gui_duyet(self):
        """Gửi duyệt giao dịch"""
        self.write({'trang_thai': 'cho_duyet'})
    
    def action_duyet(self):
        """Duyệt giao dịch"""
        self.write({
            'trang_thai': 'da_duyet',
            'nguoi_duyet': self.env.user.id,
            'ngay_duyet': fields.Date.today(),
        })
    
    def action_tu_choi(self):
        """Từ chối giao dịch"""
        self.write({
            'trang_thai': 'tu_choi',
            'nguoi_duyet': self.env.user.id,
            'ngay_duyet': fields.Date.today(),
        })
    
    def action_hoan_thanh(self):
        """Hoàn thành giao dịch"""
        if self.trang_thai != 'da_duyet':
            raise ValidationError('Chỉ có thể hoàn thành giao dịch đã được duyệt!')
        self.write({'trang_thai': 'hoan_thanh'})
    
    @api.model
    def create(self, vals):
        """Tạo mã giao dịch tự động nếu chưa có"""
        if not vals.get('ma_giao_dich'):
            vals['ma_giao_dich'] = self.env['ir.sequence'].next_by_code('theo_doi_thuc_hien_ngan_sach') or 'New'
        return super(TheoDoiThucHienNganSach, self).create(vals)
