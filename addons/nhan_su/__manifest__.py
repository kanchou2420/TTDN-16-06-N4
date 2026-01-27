# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Nhân Sự",

    'summary': """
        Quản lý thông tin nhân sự, chức vụ và phòng ban""",

    'description': """
        Module Quản Lý Nhân Sự
        =======================
        
        Chức năng chính:
        - Quản lý thông tin nhân sự (chức vụ bắt buộc)
        - Quản lý phòng ban và chức vụ
        - Theo dõi lịch sử công tác
        - Xác định vai trò lãnh đạo (Chủ tịch, Giám đốc) để phân quyền duyệt
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/nhan_vien.xml',
         'views/phong_ban.xml',
         'views/chuc_vu.xml',
         'views/lich_su_cong_tac.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
