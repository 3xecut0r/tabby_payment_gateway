odoo.define('pos_tabby_integration.TabbyPaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const TabbyPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
                this.lockedValidateOrder = this._wrapValidateOrderWithLock(this.validateOrder);
            }

            _wrapValidateOrderWithLock(method) {
                const component = this;
                let called = false;
                return async (...args) => {
                    if (called) {
                        return;
                    }
                    try {
                        called = true;
                        await method.call(component, ...args);
                    } finally {
                        called = false;
                    }
                };
            }

            async validateOrder(isForceValidate) {
                const currentOrder = this.env.pos.get_order();

                const selectedPaymentLine = currentOrder.selected_paymentline;

                if (selectedPaymentLine && selectedPaymentLine.payment_method.name === 'Tabby') {
                    const { confirmed } = await this.showPopup('TabbyPopup', {
                        title: this.env._t('Tabby Payment Confirmation'),
                    });
                    if (!confirmed) return;
                }
                return super.validateOrder(isForceValidate);
            }
        };

    Registries.Component.extend(PaymentScreen, TabbyPaymentScreen);

    return TabbyPaymentScreen;
});
