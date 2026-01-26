# -*- coding: utf-8 -*-

import logging
from odoo import http, fields, models
from odoo.http import request
import json

_logger = logging.getLogger(__name__)


class KeToanTaiSanAPI(http.Controller):
    
    @http.route('/api/du_bao_thu_chi', type='json', auth='user', methods=['POST'])
    def du_bao_thu_chi(self):
        """API dự báo thu chi sử dụng AI"""
        try:
            data = request.get_json_data()
            
            # Lấy tháng và năm
            nam = data.get('nam', fields.Date.today().year)
            thang = data.get('thang', fields.Date.today().month)
            
            # Gọi hàm dự báo
            result = self._predict_cash_flow(nam, thang)
            
            return {
                'status': 'success',
                'data': result
            }
        except Exception as e:
            _logger.error(f"Lỗi dự báo: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _predict_cash_flow(self, nam, thang):
        """Dự báo dòng tiền dựa trên dữ liệu lịch sử"""
        env = request.env
        
        # Lấy dữ liệu phiếu thu tháng trước
        phieu_thu_objs = env['phieu_thu'].search([
            ('nam', '=', nam if thang > 1 else nam - 1),
            ('thang', '=', thang - 1 if thang > 1 else 12),
            ('trang_thai', '=', 'posted'),
        ])
        
        # Lấy dữ liệu phiếu chi tháng trước
        phieu_chi_objs = env['phieu_chi'].search([
            ('nam', '=', nam if thang > 1 else nam - 1),
            ('thang', '=', thang - 1 if thang > 1 else 12),
            ('trang_thai', '=', 'posted'),
        ])
        
        # Tính bình quân
        so_tien_thu_tb = sum(pt.tong_tien for pt in phieu_thu_objs) / len(phieu_thu_objs) if phieu_thu_objs else 0
        so_tien_chi_tb = sum(pc.tong_tien for pc in phieu_chi_objs) / len(phieu_chi_objs) if phieu_chi_objs else 0
        
        # Thêm yếu tố khấu hao
        khau_hao_chi_phi = self._tinhchi_phi_khau_hao(nam, thang)
        so_tien_chi_tb += khau_hao_chi_phi
        
        # Dự báo
        du_bao_thu = so_tien_thu_tb * 1.05  # Tăng 5%
        du_bao_chi = so_tien_chi_tb * 1.05
        
        # Tính dòng tiền ròng
        dong_tien_rong = du_bao_thu - du_bao_chi
        
        return {
            'thang': thang,
            'nam': nam,
            'du_bao_thu': du_bao_thu,
            'du_bao_chi': du_bao_chi,
            'du_bao_khau_hao': khau_hao_chi_phi,
            'dong_tien_rong': dong_tien_rong,
            'mo_ta': f"Dự báo dòng tiền tháng {thang}/{nam}"
        }
    
    def _tinhchi_phi_khau_hao(self, nam, thang):
        """Tính chi phí khấu hao dự kiến"""
        env = request.env
        
        khau_hao_records = env['khau_hao_tai_san'].search([
            ('ngay_khau_hao', '>=', f'{nam}-{thang:02d}-01'),
            ('ngay_khau_hao', '<', f'{nam}-{thang+1:02d}-01' if thang < 12 else f'{nam+1}-01-01'),
            ('trang_thai', '=', 'posted'),
        ])
        
        return sum(kh.so_tien_khau_hao for kh in khau_hao_records)
