from odoo import models, fields, api  


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân sự'
    _rec_name = 'ho_ten'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten = fields.Char("Họ tên", required=True, default='')
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    
    # Chức vụ hiện tại - BẮT BUỘC
    chuc_vu_id = fields.Many2one('chuc_vu', string='Chức vụ hiện tại', required=True,
                                  help='Chức vụ hiện tại của nhân sự')
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban hiện tại',
                                    help='Phòng ban hiện tại của nhân sự')
    
    lich_su_cong_tac_ids = fields.One2many("lich_su_cong_tac", string="Danh sách lịch sử công tác", inverse_name="nhan_vien_id")
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)
    
    # Helper để kiểm tra vai trò lãnh đạo
    is_lanh_dao = fields.Boolean(string='Là lãnh đạo', compute='_compute_is_lanh_dao', store=True,
                                  help='Kiểm tra xem nhân sự có phải là Chủ tịch hoặc Giám đốc')

    # ids_van_ban_di = fields.One2many(comodel_name='van_ban_di', inverse_name='id_nguoi_phat_hanh', string="Số văn bản đi")

    @api.depends('ngay_sinh')
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                record.tuoi = (fields.Date.today() - record.ngay_sinh).days // 365
    
    @api.depends('chuc_vu_id', 'chuc_vu_id.ten_chuc_vu')
    def _compute_is_lanh_dao(self):
        """Kiểm tra xem nhân sự có phải là Chủ tịch hoặc Giám đốc không"""
        lanh_dao_keywords = ['chủ tịch', 'giám đốc', 'chu tich', 'giam doc', 'director', 'president', 'ceo']
        for record in self:
            if record.chuc_vu_id and record.chuc_vu_id.ten_chuc_vu:
                ten_cv = record.chuc_vu_id.ten_chuc_vu.lower()
                record.is_lanh_dao = any(keyword in ten_cv for keyword in lanh_dao_keywords)
            else:
                record.is_lanh_dao = False


