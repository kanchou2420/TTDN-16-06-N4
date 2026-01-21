from odoo import models, fields, api
from odoo.exceptions import ValidationError


class VanBanDi(models.Model):
    """
    Mô hình Văn Bản Đi (Outgoing Documents)
    Quản lý toàn bộ văn bản đi của công ty
    """
    _name = 'van_ban_di'
    _description = 'Văn bản đi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = "ten_van_ban"

    # Thông tin cơ bản
    ten_van_ban = fields.Char('Tên văn bản', required=True, tracking=True)
    
    loai_van_ban = fields.Selection([
        ('thong_bao', 'Thông báo'),
        ('quyet_dinh', 'Quyết định'),
        ('hop_dong', 'Hợp đồng'),
        ('thoathuan', 'Thỏa thuận'),
        ('chi_thi', 'Chỉ thị'),
        ('yeu_cau', 'Yêu cầu'),
        ('khac', 'Khác'),
    ], string='Loại văn bản', tracking=True)
    
    noi_dung = fields.Html('Nội dung', help='Nội dung chi tiết của văn bản')
    
    file_dinh_kem = fields.Binary('File đính kèm', attachment=True)
    file_dinh_kem_filename = fields.Char('Tên file')
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('issued', 'Đã ban hành'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    note = fields.Text(string='Ghi chú')
    
    def action_issued(self):
        """Ban hành văn bản"""
        self.write({'state': 'issued'})
    
    def action_cancel(self):
        """Hủy văn bản"""
        self.write({'state': 'cancelled'})