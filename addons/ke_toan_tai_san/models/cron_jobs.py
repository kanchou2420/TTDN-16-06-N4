# -*- coding: utf-8 -*-

import logging
from odoo import models, fields
from datetime import datetime

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = 'ir.cron'
    
    @staticmethod
    def _khau_hao_tu_dong():
        """Tính khấu hao tự động hàng tháng"""
        from odoo import api
        
        env = api.Environment(api.environment.cr, api.environment.uid, api.environment.context)
        
        try:
            tai_san_obj = env['tai_san']
            khau_hao_obj = env['khau_hao_tai_san']
            
            # Lấy tất cả tài sản có phương pháp khấu hao
            tai_san_ids = tai_san_obj.search([
                ('pp_khau_hao', '!=', 'none'),
                ('gia_tri_hien_tai', '>', 0),
                ('trang_thai_thanh_ly', '!=', 'da_thanh_ly'),
            ])
            
            for tai_san in tai_san_ids:
                so_tien_khau_hao = env['so_tai_san']._tinh_khau_hao(tai_san)
                
                if so_tien_khau_hao > 0:
                    khau_hao_vals = {
                        'tai_san_id': tai_san.id,
                        'ngay_khau_hao': fields.Date.today(),
                        'gia_tri_con_lai': tai_san.gia_tri_hien_tai,
                        'so_tien_khau_hao': so_tien_khau_hao,
                        'pp_khau_hao': tai_san.pp_khau_hao,
                    }
                    
                    khau_hao_record = khau_hao_obj.create(khau_hao_vals)
                    khau_hao_record.action_post_journal()
                    
                    # Cập nhật giá trị tài sản
                    tai_san.gia_tri_hien_tai = max(0, tai_san.gia_tri_hien_tai - so_tien_khau_hao)
                    
                    _logger.info(f"Khấu hao tài sản {tai_san.ma_tai_san}: {so_tien_khau_hao}")
            
            _logger.info("Khấu hao tự động hoàn tất")
        
        except Exception as e:
            _logger.error(f"Lỗi khi khấu hao tự động: {str(e)}")
