from odoo.tests.common import TransactionCase


class TestThanhLy(TransactionCase):
    def setUp(self):
        super(TestThanhLy, self).setUp()
        self.ThanhLy = self.env['thanh_ly_tai_san']
        # create a sample asset
        tai_san = self.env['tai_san'].create({
            'ma_tai_san': 'TS-TEST-1',
            'ten_tai_san': 'Tệst Asset',
            'ngay_mua_ts': '2020-01-01',
            'gia_tri_ban_dau': 1000.0,
            'gia_tri_hien_tai': 1000.0,
            'danh_muc_ts_id': self.env['danh_muc_tai_san'].create({'ma_tai_san_type':'T1','ten_danh_muc':'TestLoại'}).id,
        })
        self.tai_san = tai_san
        # create a nhân viên
        nv = self.env['nhan_vien'].create({'name': 'NV Test'})
        self.nv = nv

    def test_thanh_ly_tao_phieu_thu(self):
        rec = self.ThanhLy.create({
            'ma_thanh_ly': 'TL-TEST-1',
            'hanh_dong': 'ban',
            'tai_san_id': self.tai_san.id,
            'nguoi_thanh_ly_id': self.nv.id,
            'thoi_gian_thanh_ly': '2020-12-01 00:00:00',
            'gia_ban': 500.0,
        })
        self.assertTrue(rec.phieu_thu_id, "Phải tạo phiếu thu khi thanh lý bán có giá bán > 0")
        self.assertEqual(rec.phieu_thu_id.amount, 500.0)
