{
    'name': 'Quản lý Thu Chi & Công Nợ',
    'version': '15.0.2.0.0',
    'summary': 'Quản lý phiếu thu/chi và công nợ phải thu/phải trả - Tích hợp ngân sách',
    'description': """
        Module Quản Lý Thu Chi & Công Nợ
        =================================
        
        Chức năng chính:
        - Quản lý phiếu thu với workflow: Nháp → Xác nhận → Ghi sổ
        - Quản lý phiếu chi với workflow: Nháp → Xác nhận → Duyệt → Ghi sổ
        - Theo dõi công nợ phải thu/phải trả với lịch sử thanh toán
        - Cảnh báo quá hạn công nợ
        - Kiểm tra ngân sách trước khi chi
        
        Tích hợp với:
        - Module Quản Lý Ngân Sách (kiểm tra và theo dõi chi tiêu)
        - Module Quản Lý Tài Sản (thu thanh lý, chi mua sắm)
        - Module Nhân Sự (phòng ban, nhân viên)
    """,
    'category': 'Accounting',
    'author': 'TTDN-15-04-N6',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'quan_ly_ngan_sach', 'quan_ly_tai_san', 'nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/dashboard_views.xml',
        'views/phieu_thu_views.xml',
        'views/phieu_chi_views.xml',
        'views/cong_no_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
