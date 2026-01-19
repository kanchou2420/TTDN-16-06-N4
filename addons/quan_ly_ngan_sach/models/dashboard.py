# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BudgetDashboard(models.Model):
    _name = 'budget.dashboard'
    _description = 'Dashboard for Budget Management'
    _auto = False

    @api.model
    def name_get(self):
        return [(record.id, "Dashboard Ngân Sách") for record in self]

    @api.model
    def get_budget_overview_data(self):
        """Lấy dữ liệu tổng quan ngân sách"""
        
        # Thống kê ngân sách
        total_budgets = self.env['ngan_sach'].search_count([])
        active_budgets = self.env['ngan_sach'].search_count([('trang_thai', '=', 'dang_thuc_hien')])
        approved_budgets = self.env['ngan_sach'].search_count([('trang_thai', '=', 'duyet')])
        draft_budgets = self.env['ngan_sach'].search_count([('trang_thai', '=', 'nhap')])
        completed_budgets = self.env['ngan_sach'].search_count([('trang_thai', '=', 'ket_thuc')])
        
        # Tổng giá trị ngân sách
        budgets = self.env['ngan_sach'].search([('trang_thai', 'in', ['duyet', 'dang_thuc_hien'])])
        total_budget_amount = sum(budgets.mapped('tong_ngan_sach'))
        total_allocated = sum(budgets.mapped('tong_phan_bo'))
        total_remaining = sum(budgets.mapped('con_lai'))
        
        # Thống kê dự toán chi
        total_estimates = self.env['du_toan_chi'].search_count([])
        pending_estimates = self.env['du_toan_chi'].search_count([('trang_thai', '=', 'cho_duyet')])
        approved_estimates = self.env['du_toan_chi'].search_count([('trang_thai', '=', 'duyet')])
        rejected_estimates = self.env['du_toan_chi'].search_count([('trang_thai', '=', 'tu_choi')])
        
        # Tổng giá trị dự toán
        estimates = self.env['du_toan_chi'].search([('trang_thai', '=', 'duyet')])
        total_estimated_amount = sum(estimates.mapped('so_tien_du_kien'))
        total_approved_amount = sum(estimates.mapped('so_tien_duyet'))
        
        # Thống kê phân bổ ngân sách
        allocations = self.env['phan_bo_ngan_sach'].search([])
        total_allocations = len(allocations)
        allocation_in_use = self.env['phan_bo_ngan_sach'].search_count([('trang_thai', '=', 'dang_su_dung')])
        allocation_exhausted = self.env['phan_bo_ngan_sach'].search_count([('trang_thai', '=', 'het')])
        
        # Thống kê giao dịch thực hiện
        total_transactions = self.env['theo_doi_thuc_hien_ngan_sach'].search_count([])
        pending_transactions = self.env['theo_doi_thuc_hien_ngan_sach'].search_count([('trang_thai', '=', 'cho_duyet')])
        completed_transactions = self.env['theo_doi_thuc_hien_ngan_sach'].search_count([('trang_thai', '=', 'hoan_thanh')])
        
        transactions = self.env['theo_doi_thuc_hien_ngan_sach'].search([('trang_thai', '=', 'hoan_thanh')])
        total_spent = sum(transactions.filtered(lambda t: t.loai_giao_dich == 'chi_tieu').mapped('so_tien_thuc_te'))
        total_recovered = sum(transactions.filtered(lambda t: t.loai_giao_dich == 'thu_hoi').mapped('so_tien_thuc_te'))
        
        # Phân bổ theo phòng ban
        departments_data = []
        departments = self.env['phong_ban'].search([])
        for dept in departments:
            dept_allocations = self.env['phan_bo_ngan_sach'].search([('phong_ban_id', '=', dept.id)])
            total_amount = sum(dept_allocations.mapped('so_tien'))
            used_amount = sum(dept_allocations.mapped('so_tien_da_su_dung'))
            if total_amount > 0:
                departments_data.append({
                    'name': dept.ten_phong_ban or dept.ma_phong_ban,
                    'allocated': total_amount,
                    'used': used_amount,
                    'remaining': total_amount - used_amount
                })
        
        # Phân bổ theo loại chi
        expense_types_data = []
        expense_types = [
            ('mua_sam_ts', 'Mua sắm tài sản'),
            ('khau_hao_ts', 'Khấu hao tài sản'),
            ('bao_duong_sua_chua', 'Bảo dưỡng sửa chữa'),
            ('nhan_su', 'Chi phí nhân sự'),
            ('van_phong_pham', 'Văn phòng phẩm'),
            ('dao_tao', 'Đào tạo'),
            ('marketing', 'Marketing'),
            ('khac', 'Chi phí khác'),
        ]
        for code, name in expense_types:
            estimate_count = self.env['du_toan_chi'].search_count([('loai_chi', '=', code)])
            estimate_amount = sum(self.env['du_toan_chi'].search([('loai_chi', '=', code), ('trang_thai', '=', 'duyet')]).mapped('so_tien_duyet'))
            if estimate_count > 0:
                expense_types_data.append({
                    'name': name,
                    'count': estimate_count,
                    'amount': estimate_amount
                })
        
        # Xu hướng chi tiêu theo tháng (6 tháng gần nhất)
        from datetime import datetime, timedelta
        monthly_spending = []
        for i in range(5, -1, -1):
            month_date = datetime.now() - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            if month_date.month == 12:
                month_end = month_date.replace(year=month_date.year + 1, month=1, day=1)
            else:
                month_end = month_date.replace(month=month_date.month + 1, day=1)
            
            month_transactions = self.env['theo_doi_thuc_hien_ngan_sach'].search([
                ('ngay_giao_dich', '>=', month_start.strftime('%Y-%m-%d')),
                ('ngay_giao_dich', '<', month_end.strftime('%Y-%m-%d')),
                ('loai_giao_dich', '=', 'chi_tieu'),
                ('trang_thai', '=', 'hoan_thanh')
            ])
            month_total = sum(month_transactions.mapped('so_tien_thuc_te'))
            monthly_spending.append({
                'month': month_date.strftime('%m/%Y'),
                'amount': month_total
            })
        
        # Ngân sách theo trạng thái
        budget_status_data = [
            {'name': 'Nháp', 'count': draft_budgets, 'color': '#6c757d'},
            {'name': 'Đã duyệt', 'count': approved_budgets, 'color': '#17a2b8'},
            {'name': 'Đang thực hiện', 'count': active_budgets, 'color': '#28a745'},
            {'name': 'Kết thúc', 'count': completed_budgets, 'color': '#007bff'},
        ]
        
        # Cảnh báo ngân sách sắp hết (tỷ lệ sử dụng > 80%)
        warning_allocations = []
        for allocation in self.env['phan_bo_ngan_sach'].search([('trang_thai', '=', 'dang_su_dung')]):
            if allocation.ty_le_su_dung >= 80:
                warning_allocations.append({
                    'name': allocation.ten_phan_bo,
                    'percentage': round(allocation.ty_le_su_dung, 1),
                    'remaining': allocation.so_tien_con_lai
                })
        
        return {
            # Tổng quan ngân sách
            'total_budgets': total_budgets,
            'active_budgets': active_budgets,
            'approved_budgets': approved_budgets,
            'draft_budgets': draft_budgets,
            'completed_budgets': completed_budgets,
            
            # Giá trị ngân sách
            'total_budget_amount': total_budget_amount,
            'total_allocated': total_allocated,
            'total_remaining': total_remaining,
            
            # Dự toán chi
            'total_estimates': total_estimates,
            'pending_estimates': pending_estimates,
            'approved_estimates': approved_estimates,
            'rejected_estimates': rejected_estimates,
            'total_estimated_amount': total_estimated_amount,
            'total_approved_amount': total_approved_amount,
            
            # Phân bổ
            'total_allocations': total_allocations,
            'allocation_in_use': allocation_in_use,
            'allocation_exhausted': allocation_exhausted,
            
            # Giao dịch
            'total_transactions': total_transactions,
            'pending_transactions': pending_transactions,
            'completed_transactions': completed_transactions,
            'total_spent': total_spent,
            'total_recovered': total_recovered,
            
            # Dữ liệu biểu đồ
            'departments_data': departments_data,
            'expense_types_data': expense_types_data,
            'monthly_spending': monthly_spending,
            'budget_status_data': budget_status_data,
            
            # Cảnh báo
            'warning_allocations': warning_allocations,
        }
