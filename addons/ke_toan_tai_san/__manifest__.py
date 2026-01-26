# -*- coding: utf-8 -*-
{
    'name': "Kế Toán Tài Sản & Khấu Hao",

    'summary': """
        Quản lý khấu hao tài sản, tích hợp sổ cái kế toán và dự báo AI
    """,

    'description': """
        Module Kế Toán Tài Sản & Khấu Hao
        ==================================
        
        Chức năng chính:
        - Tính toán và ghi nhận khấu hao tự động hàng tháng
        - Tích hợp với sổ cái kế toán (Journal Entries)
        - Báo cáo chi tiết khấu hao theo tài sản, phòng ban
        - Bảng cân đối tài sản (Asset Register)
        - Phân tích giá trị tài sản
        - Dự báo AI cho chi phí bảo trì
        
        Tích hợp với:
        - Module Quản Lý Tài Sản (lấy dữ liệu tài sản)
        - Module Quản Lý Ngân Sách (theo dõi chi phí)
        - Module Quản Lý Thu Chi (ghi nhận giao dịch)
    """,

    'author': "TTDN-16-06-N4",
    'website': "http://www.yourcompany.com",

    'category': 'Accounting',
    'version': '1.0',
    'license': 'LGPL-3',

    # Dependencies
    'depends': ['base', 'web', 'mail', 'account', 'quan_ly_tai_san'],

    # Data files
    'data': [
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'views/khau_hao_view.xml',
        'views/so_tai_san_view.xml',
        'views/tai_khoan_khau_hao_view.xml',
        'views/dashboard_view.xml',
        'views/menu.xml',
    ],

    'demo': [],

    'assets': {
        'web.assets_backend': [
            'ke_toan_tai_san/static/src/css/dashboard_common.css',
            'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js',
        ],
    },
    
    'installable': True,
    'application': True,
}
