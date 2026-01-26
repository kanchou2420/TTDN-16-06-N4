odoo.define('quan_ly_ngan_sach.budget_dashboard', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');

    var BudgetDashboardController = FormController.extend({
        start: function () {
            this._super.apply(this, arguments);
            this.$el.addClass('o_budget_dashboard_view');
        },
        willStart: function () {
            return Promise.all([
                this._super.apply(this, arguments),
                this._loadDashboardData()
            ]);
        },
        _loadDashboardData: function () {
            const self = this;
            return this._rpc({
                model: 'budget.dashboard',
                method: 'get_budget_overview_data',
                args: [],
            }).then(function (data) {
                self.dashboardData = data;
            });
        },
        renderButtons: function () {
            this.$buttons = $();
            return this.$buttons;
        },
        _update: function () {
            const self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._loadDashboardData().then(function () {
                    self._updateDashboard();
                });
            });
        },
        on_attach_callback: function () {
            this._super.apply(this, arguments);
            this._updateDashboard();
        },
        _updateDashboard: function () {
            if (!this.dashboardData) return;
            const data = this.dashboardData;
            
            // Update main stat cards
            this.$('.total_budget_amount').text(this._formatCurrency(data.total_budget_amount));
            this.$('.total_allocated').text(this._formatCurrency(data.total_allocated));
            this.$('.total_remaining').text(this._formatCurrency(data.total_remaining));
            this.$('.total_spent').text(this._formatCurrency(data.total_spent));
            
            // Update badges
            this.$('.total_budgets_count').text(data.total_budgets);
            this.$('.allocation_in_use').text(data.allocation_in_use);
            this.$('.completed_transactions').text(data.completed_transactions);
            
            // Calculate remaining percentage
            if (data.total_budget_amount > 0) {
                const remainingPct = ((data.total_remaining / data.total_budget_amount) * 100).toFixed(1);
                this.$('.remaining_percentage').text(remainingPct + '%');
            }
            
            // Update status cards
            this.$('.draft_budgets').text(data.draft_budgets);
            this.$('.approved_budgets').text(data.approved_budgets);
            this.$('.active_budgets').text(data.active_budgets);
            this.$('.pending_estimates').text(data.pending_estimates);
            
            // Update info cards
            this.$('.total_estimates').text(data.total_estimates);
            this.$('.approved_estimates').text(data.approved_estimates);
            this.$('.rejected_estimates').text(data.rejected_estimates);
            this.$('.total_approved_amount').text(this._formatCurrency(data.total_approved_amount));
            
            this.$('.total_allocations').text(data.total_allocations);
            this.$('.allocation_in_use_count').text(data.allocation_in_use);
            this.$('.allocation_exhausted').text(data.allocation_exhausted);
            
            this.$('.total_transactions').text(data.total_transactions);
            this.$('.pending_transactions').text(data.pending_transactions);
            this.$('.completed_transactions_count').text(data.completed_transactions);
            this.$('.total_recovered').text(this._formatCurrency(data.total_recovered));
            
            // Update warning section
            this._updateWarnings(data.warning_allocations);
            
            // Render charts
            this._renderMonthlySpendingChart(data.monthly_spending);
            this._renderBudgetStatusChart(data.budget_status_data);
            this._renderDepartmentChart(data.departments_data);
            this._renderExpenseTypeChart(data.expense_types_data);
        },
        _formatCurrency: function (amount) {
            if (!amount) return '0 VNĐ';
            return amount.toLocaleString('vi-VN') + ' VNĐ';
        },
        _updateWarnings: function (warnings) {
            const $warningList = this.$('.warning-list');
            $warningList.empty();
            
            if (!warnings || warnings.length === 0) {
                $warningList.html('<p class="text-muted mb-0"><i class="fa fa-check-circle text-success mr-2"></i>Không có cảnh báo nào - Tất cả ngân sách hoạt động bình thường!</p>');
                return;
            }
            
            warnings.forEach(function (warning) {
                const progressColor = warning.percentage >= 90 ? 'danger' : 'warning';
                const $item = $(`
                    <div class="warning-item d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <i class="fa fa-exclamation-triangle text-${progressColor} mr-2"></i>
                            <strong>${warning.name}</strong>
                        </div>
                        <div class="d-flex align-items-center">
                            <div class="progress mr-3" style="width: 150px; height: 20px;">
                                <div class="progress-bar bg-${progressColor}" role="progressbar" 
                                     style="width: ${warning.percentage}%;" 
                                     aria-valuenow="${warning.percentage}" aria-valuemin="0" aria-valuemax="100">
                                    ${warning.percentage}%
                                </div>
                            </div>
                            <span class="badge badge-${progressColor}">Còn: ${warning.remaining.toLocaleString('vi-VN')} VNĐ</span>
                        </div>
                    </div>
                `);
                $warningList.append($item);
            });
        },
        _renderMonthlySpendingChart: function (monthlyData) {
            if (this.monthlyChart) {
                this.monthlyChart.destroy();
            }
            
            const ctx = this.$('#monthlySpendingChart')[0];
            if (!ctx) return;
            
            const labels = monthlyData.map(d => d.month);
            const data = monthlyData.map(d => d.amount);
            
            this.monthlyChart = new Chart(ctx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Chi tiêu (VNĐ)',
                        data: data,
                        borderColor: '#4e73df',
                        backgroundColor: 'rgba(78, 115, 223, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#4e73df',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.parsed.y.toLocaleString('vi-VN') + ' VNĐ';
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString('vi-VN');
                                }
                            }
                        }
                    }
                }
            });
        },
        _renderBudgetStatusChart: function (statusData) {
            if (this.statusChart) {
                this.statusChart.destroy();
            }
            
            const ctx = this.$('#budgetStatusChart')[0];
            if (!ctx) return;
            
            const labels = statusData.map(d => d.name);
            const data = statusData.map(d => d.count);
            const colors = statusData.map(d => d.color);
            
            this.statusChart = new Chart(ctx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    cutout: '60%'
                }
            });
        },
        _renderDepartmentChart: function (departmentsData) {
            if (this.departmentChart) {
                this.departmentChart.destroy();
            }
            
            const ctx = this.$('#departmentChart')[0];
            if (!ctx) return;
            
            if (!departmentsData || departmentsData.length === 0) {
                return;
            }
            
            const labels = departmentsData.map(d => d.name);
            const allocatedData = departmentsData.map(d => d.allocated);
            const usedData = departmentsData.map(d => d.used);
            
            this.departmentChart = new Chart(ctx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Đã phân bổ',
                            data: allocatedData,
                            backgroundColor: 'rgba(54, 185, 204, 0.8)',
                            borderColor: '#36b9cc',
                            borderWidth: 1
                        },
                        {
                            label: 'Đã sử dụng',
                            data: usedData,
                            backgroundColor: 'rgba(231, 74, 59, 0.8)',
                            borderColor: '#e74a3b',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + context.parsed.y.toLocaleString('vi-VN') + ' VNĐ';
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString('vi-VN');
                                }
                            }
                        }
                    }
                }
            });
        },
        _renderExpenseTypeChart: function (expenseData) {
            if (this.expenseChart) {
                this.expenseChart.destroy();
            }
            
            const ctx = this.$('#expenseTypeChart')[0];
            if (!ctx) return;
            
            if (!expenseData || expenseData.length === 0) {
                return;
            }
            
            const labels = expenseData.map(d => d.name);
            const data = expenseData.map(d => d.amount);
            
            const backgroundColors = [
                '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e',
                '#e74a3b', '#5a5c69', '#858796', '#6f42c1'
            ];
            
            this.expenseChart = new Chart(ctx.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: backgroundColors.slice(0, data.length),
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label + ': ' + context.parsed.toLocaleString('vi-VN') + ' VNĐ';
                                }
                            }
                        }
                    }
                }
            });
        }
    });

    var BudgetDashboardView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: BudgetDashboardController
        })
    });

    viewRegistry.add('budget_dashboard_view', BudgetDashboardView);
    
    return {
        BudgetDashboardController: BudgetDashboardController,
        BudgetDashboardView: BudgetDashboardView,
    };
});
