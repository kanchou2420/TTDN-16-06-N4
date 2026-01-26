# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Ngân Sách & Dự Toán",

    'summary': """
        Quản lý ngân sách, dự toán chi và theo dõi thực hiện ngân sách""",

    'description': """
        Module Quản Lý Ngân Sách & Dự Toán
        ====================================
        
        Chức năng chính:
        - Lập kế hoạch ngân sách theo năm/quý/tháng
        - Quản lý dự toán chi tiết theo phòng ban và danh mục
        - Phân bổ ngân sách cho các hoạt động và dự án
        - Theo dõi thực hiện và so sánh với kế hoạch
        - Báo cáo tình hình sử dụng ngân sách
        
        Tích hợp với:
        - Module Quản Lý Tài Sản (ngân sách mua sắm, khấu hao)
        - Module Nhân Sự (phân bổ theo phòng ban)
    """,

    'author': "Nguyễn Ngọc Đan Trường - 1504",
    'website': "http://www.yourcompany.com",

    'category': 'Accounting',
    'version': '1.0',
    'license': 'LGPL-3',

    # Module dependencies
    'depends': ['base', 'web', 'mail', 'quan_ly_tai_san', 'nhan_su'],

    # Data files
    'data': [
        'security/ir.model.access.csv',
        'views/ngan_sach_view.xml',
        'views/du_toan_chi_view.xml',
        'views/phan_bo_ngan_sach_view.xml',
        'views/theo_doi_thuc_hien_view.xml',
        'views/dashboard_view.xml',
        'views/menu.xml',
    ],
    
    'demo': [],
    
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js',
            'quan_ly_ngan_sach/static/src/css/dashboard.css',
            'quan_ly_ngan_sach/static/src/css/dashboard_common.css',
            'quan_ly_ngan_sach/static/src/js/budget_dashboard.js',
        ],
    },
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
