odoo.define('ke_toan_tai_san.dashboard_view', function(require) {
    'use strict';

    const FormView = require('web.FormView');
    const FormController = require('web.FormController');

    const KeToanDashboardView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: DashboardController,
        }),
    });

    const DashboardController = FormController.extend({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.btn-du-bao', this._on_du_bao.bind(this));
            }
        },

        _on_du_bao: function () {
            const self = this;
            this._rpc({
                route: '/api/du_bao_thu_chi',
                type: 'json',
                data: {
                    thang: new Date().getMonth() + 1,
                    nam: new Date().getFullYear()
                }
            }).then(result => {
                if (result.status === 'success') {
                    this._show_du_bao_dialog(result.data);
                } else {
                    this.displayNotification({
                        title: 'Lỗi',
                        message: result.message,
                        type: 'danger',
                    });
                }
            });
        },

        _show_du_bao_dialog: function (data) {
            const html = `
                <div class="dialog-du-bao">
                    <h4>Dự Báo Dòng Tiền Tháng ${data.thang}/${data.nam}</h4>
                    <table class="table table-bordered">
                        <tr>
                            <td><strong>Dự báo thu:</strong></td>
                            <td>${(data.du_bao_thu / 1000000).toFixed(2)}M VNĐ</td>
                        </tr>
                        <tr>
                            <td><strong>Dự báo chi:</strong></td>
                            <td>${(data.du_bao_chi / 1000000).toFixed(2)}M VNĐ</td>
                        </tr>
                        <tr>
                            <td><strong>Chi phí khấu hao:</strong></td>
                            <td>${(data.du_bao_khau_hao / 1000000).toFixed(2)}M VNĐ</td>
                        </tr>
                        <tr style="background-color: #e7f3ff; font-weight: bold;">
                            <td>Dòng tiền ròng:</td>
                            <td style="color: ${data.dong_tien_rong >= 0 ? 'green' : 'red'};">
                                ${(data.dong_tien_rong / 1000000).toFixed(2)}M VNĐ
                            </td>
                        </tr>
                    </table>
                </div>
            `;

            const dialog = new (require('web.Dialog'))(this, {
                title: 'Dự Báo Dòng Tiền',
                size: 'medium',
                buttons: [
                    { text: 'Đóng', click: function() { dialog.close(); } }
                ]
            }, $(html));
            
            dialog.open();
        }
    });

    return KeToanDashboardView;
});
