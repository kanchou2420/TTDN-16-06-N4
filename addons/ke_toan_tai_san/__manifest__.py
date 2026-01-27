# -*- coding: utf-8 -*-
{
    'name': "Kế Toán Tài Sản & Dự Báo AI",

    'summary': """
        Quản lý khấu hao tài sản, tích hợp ngân sách và dự báo AI
    """,

    'description': """
        Module Kế Toán Tài Sản & Dự Báo AI
        ======================================
        
        MODULE ĐỘC LẬP - KHÔNG CẦN CÀI ĐẶT MODULE ACCOUNT (Lên hóa đơn)
        
        Chức năng chính:
        - Tính toán và ghi nhận khấu hao tự động hàng tháng
        - Quản lý bút toán khấu hao nội bộ
        - Báo cáo chi tiết khấu hao theo tài sản, phòng ban
        - Bảng cân đối tài sản (Asset Register)
        - Dự BÁO AI thu chi, chi phí khấu hao
        - Phân tích xu hướng tài chính
        
        Tích hợp với:
        - Module Quản Lý Tài Sản (lấy dữ liệu tài sản)
        - Module Quản Lý Ngân Sách (theo dõi ngân sách)
        - Module Thu Chi Công Nợ (dữ liệu thu chi thực tế)
    """,

    'author': "TTDN-16-06-N4",
    'website': "http://www.yourcompany.com",

    'category': 'Accounting',
    'version': '2.0',
    'license': 'LGPL-3',

    # Dependencies - TÍCH HỢP VỚI CÁC MODULE KHÁC
    'depends': ['base', 'web', 'mail', 'quan_ly_tai_san', 'quan_ly_ngan_sach', 'quanly_thuchi_congno'],

    # Data files
    'data': [
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'views/khau_hao_view.xml',
        'views/but_toan_khau_hao_view.xml',
        'views/so_tai_san_view.xml',
        'views/tai_khoan_khau_hao_view.xml',
        'views/ai_forecast_view.xml',
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
