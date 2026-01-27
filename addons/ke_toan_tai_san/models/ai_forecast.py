# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging

_logger = logging.getLogger(__name__)


class AIForecast(models.Model):
    _name = 'ai_forecast'
    _description = 'Dự báo AI Thu Chi & Tài Chính'
    _rec_name = 'ten_du_bao'
    _order = 'ngay_tao desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ten_du_bao = fields.Char('Tên dự báo', required=True)
    ngay_tao = fields.Date('Ngày tạo', default=fields.Date.today, readonly=True)
    
    loai_du_bao = fields.Selection([
        ('thu_chi', 'Dự báo Thu Chi'),
        ('khau_hao', 'Dự báo Khấu Hao'),
        ('ngan_sach', 'Dự báo Ngân Sách'),
        ('tong_hop', 'Dự báo Tổng Hợp'),
    ], string='Loại dự báo', required=True, default='thu_chi')
    
    ky_du_bao = fields.Selection([
        ('1_thang', '1 Tháng'),
        ('3_thang', '3 Tháng'),
        ('6_thang', '6 Tháng'),
        ('12_thang', '12 Tháng'),
    ], string='Kỳ dự báo', required=True, default='3_thang')
    
    # Kết quả dự báo
    du_bao_thu = fields.Float('Dự báo Thu', readonly=True)
    du_bao_chi = fields.Float('Dự báo Chi', readonly=True)
    du_bao_khau_hao = fields.Float('Dự báo Khấu Hao', readonly=True)
    du_bao_can_doi = fields.Float('Dự báo Cân Đối', compute='_compute_can_doi', store=True)
    
    # Chi tiết dự báo theo tháng (JSON)
    chi_tiet_du_bao = fields.Text('Chi tiết dự báo', readonly=True)
    
    # Độ tin cậy
    do_tin_cay = fields.Float('Độ tin cậy (%)', readonly=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('calculated', 'Đã tính toán'),
        ('confirmed', 'Đã xác nhận'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    ghi_chu = fields.Text('Ghi chú & Khuyến nghị', readonly=True)
    
    @api.depends('du_bao_thu', 'du_bao_chi')
    def _compute_can_doi(self):
        for record in self:
            record.du_bao_can_doi = record.du_bao_thu - record.du_bao_chi
    
    def action_calculate_forecast(self):
        """Tính toán dự báo AI"""
        for record in self:
            # Xác định số tháng dự báo
            months_map = {
                '1_thang': 1,
                '3_thang': 3,
                '6_thang': 6,
                '12_thang': 12,
            }
            num_months = months_map.get(record.ky_du_bao, 3)
            
            if record.loai_du_bao == 'thu_chi':
                record._calculate_thu_chi_forecast(num_months)
            elif record.loai_du_bao == 'khau_hao':
                record._calculate_khau_hao_forecast(num_months)
            elif record.loai_du_bao == 'ngan_sach':
                record._calculate_ngan_sach_forecast(num_months)
            else:  # tong_hop
                record._calculate_tong_hop_forecast(num_months)
            
            record.trang_thai = 'calculated'
    
    def _calculate_thu_chi_forecast(self, num_months):
        """Dự báo thu chi dựa trên dữ liệu lịch sử"""
        today = fields.Date.today()
        
        # Lấy dữ liệu 12 tháng gần nhất
        past_12_months = today - relativedelta(months=12)
        
        # Thu
        phieu_thu = self.env['phieu_thu'].search([
            ('state', '=', 'posted'),
            ('date', '>=', past_12_months),
        ])
        thu_theo_thang = self._group_by_month(phieu_thu, 'date', 'amount')
        
        # Chi
        phieu_chi = self.env['phieu_chi'].search([
            ('state', '=', 'posted'),
            ('date', '>=', past_12_months),
        ])
        chi_theo_thang = self._group_by_month(phieu_chi, 'date', 'amount')
        
        # Tính trung bình và xu hướng
        avg_thu, trend_thu = self._calculate_avg_and_trend(thu_theo_thang)
        avg_chi, trend_chi = self._calculate_avg_and_trend(chi_theo_thang)
        
        # Dự báo
        forecast_details = []
        total_thu = 0
        total_chi = 0
        
        for i in range(1, num_months + 1):
            month_date = today + relativedelta(months=i)
            predicted_thu = max(0, avg_thu + (trend_thu * i))
            predicted_chi = max(0, avg_chi + (trend_chi * i))
            
            total_thu += predicted_thu
            total_chi += predicted_chi
            
            forecast_details.append({
                'thang': month_date.strftime('%m/%Y'),
                'du_bao_thu': round(predicted_thu, 0),
                'du_bao_chi': round(predicted_chi, 0),
                'can_doi': round(predicted_thu - predicted_chi, 0),
            })
        
        self.du_bao_thu = total_thu
        self.du_bao_chi = total_chi
        self.chi_tiet_du_bao = json.dumps(forecast_details, ensure_ascii=False)
        self.do_tin_cay = self._calculate_confidence(len(thu_theo_thang), len(chi_theo_thang))
        self.ghi_chu = self._generate_thu_chi_recommendations(total_thu, total_chi, trend_thu, trend_chi)
    
    def _calculate_khau_hao_forecast(self, num_months):
        """Dự báo khấu hao tài sản"""
        today = fields.Date.today()
        
        # Lấy tất cả tài sản đang hoạt động
        tai_san_list = self.env['tai_san'].search([
            ('trang_thai_thanh_ly', '!=', 'da_thanh_ly'),
        ])
        
        # Lấy cấu hình khấu hao
        tai_khoan_configs = self.env['tai_khoan_khau_hao'].search([])
        config_map = {cfg.loai_tai_san_id.id: cfg for cfg in tai_khoan_configs}
        
        forecast_details = []
        total_khau_hao = 0
        
        for i in range(1, num_months + 1):
            month_date = today + relativedelta(months=i)
            month_khau_hao = 0
            
            for tai_san in tai_san_list:
                config = config_map.get(tai_san.danh_muc_ts_id.id)
                if config:
                    # Tính khấu hao theo phương pháp tuyến tính
                    yearly_rate = config.ty_le_khau_hao / 100
                    monthly_khau_hao = tai_san.gia_tri_hien_tai * yearly_rate / 12
                    month_khau_hao += monthly_khau_hao
            
            total_khau_hao += month_khau_hao
            forecast_details.append({
                'thang': month_date.strftime('%m/%Y'),
                'du_bao_khau_hao': round(month_khau_hao, 0),
            })
        
        self.du_bao_khau_hao = total_khau_hao
        self.du_bao_chi = total_khau_hao  # Khấu hao là chi phí
        self.chi_tiet_du_bao = json.dumps(forecast_details, ensure_ascii=False)
        self.do_tin_cay = 95  # Khấu hao có độ chính xác cao
        self.ghi_chu = self._generate_khau_hao_recommendations(total_khau_hao, num_months, len(tai_san_list))
    
    def _calculate_ngan_sach_forecast(self, num_months):
        """Dự báo ngân sách dựa trên kế hoạch hiện tại"""
        today = fields.Date.today()
        
        # Lấy ngân sách đang thực hiện
        ngan_sach_list = self.env['ngan_sach'].search([
            ('trang_thai', 'in', ['duyet', 'dang_thuc_hien']),
        ])
        
        total_budget = sum(ns.tong_ngan_sach for ns in ngan_sach_list)
        total_allocated = sum(ns.tong_phan_bo for ns in ngan_sach_list)
        total_remaining = sum(ns.con_lai for ns in ngan_sach_list)
        
        # Tính tốc độ sử dụng ngân sách
        theo_doi = self.env['theo_doi_thuc_hien_ngan_sach'].search([
            ('trang_thai', '=', 'hoan_thanh'),
        ])
        past_12_months = today - relativedelta(months=12)
        recent_spending = sum(
            td.so_tien_thuc_te for td in theo_doi 
            if td.ngay_giao_dich and td.ngay_giao_dich >= past_12_months
        )
        avg_monthly_spending = recent_spending / 12 if recent_spending else 0
        
        forecast_details = []
        remaining = total_remaining
        
        for i in range(1, num_months + 1):
            month_date = today + relativedelta(months=i)
            predicted_spending = min(avg_monthly_spending, remaining)
            remaining = max(0, remaining - predicted_spending)
            
            forecast_details.append({
                'thang': month_date.strftime('%m/%Y'),
                'du_bao_chi': round(predicted_spending, 0),
                'ngan_sach_con_lai': round(remaining, 0),
            })
        
        self.du_bao_chi = sum(fd['du_bao_chi'] for fd in forecast_details)
        self.chi_tiet_du_bao = json.dumps(forecast_details, ensure_ascii=False)
        self.do_tin_cay = 80
        self.ghi_chu = self._generate_ngan_sach_recommendations(
            total_budget, total_remaining, avg_monthly_spending, num_months
        )
    
    def _calculate_tong_hop_forecast(self, num_months):
        """Dự báo tổng hợp từ tất cả nguồn"""
        # Tính từng loại
        self._calculate_thu_chi_forecast(num_months)
        thu_chi_details = json.loads(self.chi_tiet_du_bao) if self.chi_tiet_du_bao else []
        thu_from_tc = self.du_bao_thu
        chi_from_tc = self.du_bao_chi
        
        # Tính khấu hao
        temp_khau_hao = 0
        tai_san_list = self.env['tai_san'].search([
            ('trang_thai_thanh_ly', '!=', 'da_thanh_ly'),
        ])
        tai_khoan_configs = self.env['tai_khoan_khau_hao'].search([])
        config_map = {cfg.loai_tai_san_id.id: cfg for cfg in tai_khoan_configs}
        
        for tai_san in tai_san_list:
            config = config_map.get(tai_san.danh_muc_ts_id.id)
            if config:
                yearly_rate = config.ty_le_khau_hao / 100
                monthly_khau_hao = tai_san.gia_tri_hien_tai * yearly_rate / 12
                temp_khau_hao += monthly_khau_hao * num_months
        
        # Tổng hợp
        self.du_bao_thu = thu_from_tc
        self.du_bao_chi = chi_from_tc + temp_khau_hao
        self.du_bao_khau_hao = temp_khau_hao
        
        # Cập nhật chi tiết
        for i, detail in enumerate(thu_chi_details):
            detail['du_bao_khau_hao'] = round(temp_khau_hao / num_months, 0)
            detail['tong_chi'] = detail.get('du_bao_chi', 0) + detail.get('du_bao_khau_hao', 0)
        
        self.chi_tiet_du_bao = json.dumps(thu_chi_details, ensure_ascii=False)
        self.do_tin_cay = 75
        self.ghi_chu = self._generate_tong_hop_recommendations()
    
    def _group_by_month(self, records, date_field, amount_field):
        """Nhóm dữ liệu theo tháng"""
        result = {}
        for rec in records:
            date_val = getattr(rec, date_field)
            if date_val:
                key = date_val.strftime('%Y-%m')
                amount = getattr(rec, amount_field, 0) or 0
                result[key] = result.get(key, 0) + amount
        return result
    
    def _calculate_avg_and_trend(self, monthly_data):
        """Tính trung bình và xu hướng"""
        if not monthly_data:
            return 0, 0
        
        values = list(monthly_data.values())
        avg = sum(values) / len(values) if values else 0
        
        # Tính xu hướng đơn giản
        if len(values) >= 2:
            trend = (values[-1] - values[0]) / len(values)
        else:
            trend = 0
        
        return avg, trend
    
    def _calculate_confidence(self, thu_data_points, chi_data_points):
        """Tính độ tin cậy dựa trên lượng dữ liệu"""
        total_points = thu_data_points + chi_data_points
        if total_points >= 24:
            return 90
        elif total_points >= 12:
            return 80
        elif total_points >= 6:
            return 70
        else:
            return 60
    
    def _generate_thu_chi_recommendations(self, total_thu, total_chi, trend_thu, trend_chi):
        """Tạo khuyến nghị cho dự báo thu chi"""
        recommendations = []
        
        if total_chi > total_thu:
            recommendations.append("⚠️ CẢNH BÁO: Dự báo chi vượt thu. Cần kiểm soát chi tiêu.")
        
        if trend_chi > 0 and trend_chi > trend_thu:
            recommendations.append("📈 Chi phí có xu hướng tăng nhanh hơn thu. Xem xét cắt giảm chi phí.")
        
        if trend_thu < 0:
            recommendations.append("📉 Thu nhập có xu hướng giảm. Cần tìm nguồn thu mới.")
        
        if total_thu > total_chi * 1.2:
            recommendations.append("✅ Tình hình tài chính tốt. Có thể đầu tư hoặc mở rộng.")
        
        return '\n'.join(recommendations) if recommendations else "Tình hình tài chính ổn định."
    
    def _generate_khau_hao_recommendations(self, total_khau_hao, num_months, num_assets):
        """Tạo khuyến nghị cho dự báo khấu hao"""
        avg_monthly = total_khau_hao / num_months if num_months else 0
        
        return f"""📊 PHÂN TÍCH KHẤU HAO:
- Tổng tài sản đang hoạt động: {num_assets}
- Chi phí khấu hao trung bình/tháng: {avg_monthly:,.0f} VNĐ
- Tổng khấu hao dự kiến {num_months} tháng: {total_khau_hao:,.0f} VNĐ

💡 KHUYẾN NGHỊ:
- Đảm bảo có ngân sách dự phòng cho chi phí khấu hao
- Xem xét thanh lý tài sản đã hết khấu hao để giảm chi phí bảo trì"""
    
    def _generate_ngan_sach_recommendations(self, total_budget, remaining, avg_spending, num_months):
        """Tạo khuyến nghị cho dự báo ngân sách"""
        months_remaining = remaining / avg_spending if avg_spending > 0 else float('inf')
        
        recommendations = [f"📊 PHÂN TÍCH NGÂN SÁCH:",
                          f"- Tổng ngân sách: {total_budget:,.0f} VNĐ",
                          f"- Còn lại: {remaining:,.0f} VNĐ",
                          f"- Tốc độ chi trung bình: {avg_spending:,.0f} VNĐ/tháng"]
        
        if months_remaining < num_months:
            recommendations.append(f"\n⚠️ CẢNH BÁO: Ngân sách có thể hết trong {months_remaining:.1f} tháng!")
            recommendations.append("💡 Cần xin bổ sung ngân sách hoặc giảm chi tiêu.")
        else:
            recommendations.append(f"\n✅ Ngân sách đủ cho {months_remaining:.1f} tháng tiếp theo.")
        
        return '\n'.join(recommendations)
    
    def _generate_tong_hop_recommendations(self):
        """Tạo khuyến nghị tổng hợp"""
        return f"""📊 DỰ BÁO TỔNG HỢP TÀI CHÍNH:

💰 THU NHẬP DỰ KIẾN: {self.du_bao_thu:,.0f} VNĐ
💸 CHI PHÍ DỰ KIẾN: {self.du_bao_chi:,.0f} VNĐ
  - Chi phí hoạt động: {(self.du_bao_chi - self.du_bao_khau_hao):,.0f} VNĐ
  - Chi phí khấu hao: {self.du_bao_khau_hao:,.0f} VNĐ
📈 CÂN ĐỐI: {self.du_bao_can_doi:,.0f} VNĐ

💡 KHUYẾN NGHỊ:
{"- Tình hình tài chính tốt, có thể đầu tư mở rộng." if self.du_bao_can_doi > 0 else "- Cần kiểm soát chi tiêu và tìm nguồn thu mới."}
- Độ tin cậy dự báo: {self.do_tin_cay}%
- Dữ liệu được tổng hợp từ: Thu Chi, Khấu Hao, Ngân Sách"""
    
    def action_confirm(self):
        """Xác nhận dự báo"""
        self.write({'trang_thai': 'confirmed'})
    
    def action_reset(self):
        """Reset về nháp"""
        self.write({
            'trang_thai': 'draft',
            'du_bao_thu': 0,
            'du_bao_chi': 0,
            'du_bao_khau_hao': 0,
            'chi_tiet_du_bao': False,
            'do_tin_cay': 0,
            'ghi_chu': False,
        })
