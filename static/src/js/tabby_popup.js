odoo.define('tabby_payment_gateway.TabbyPopup', function (require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const rpc = require('web.rpc')

    class TabbyPopup extends AbstractAwaitablePopup {

        confirm() {
            const self = this;
            const phone = this.el.querySelector('input[name="phone"]').value;
            if (!phone ) this.cancel();
            const orderlines = this.env.pos.get_order().orderlines.models;
            const items = orderlines.map(line => {
                return {
                    'title': line.get_product().display_name,
                    'quantity': line.get_quantity(),
                    'unit_price': line.get_price_with_tax().toFixed(2),
                    'category': line.get_product().categ_id[1],
                };
            });
            if (!this.env.pos.get_order().attributes.client) {
                this.cancel();
                this.showPopup('ErrorPopup', {
                    title: this.env._t('You didn\'t pick the customer'),
                    body: this.env._t('Please choose a customer'),
                });
            } else {
                rpc.query({
                    route: '/pos/save_customer_data',
                    params: {
                        'cid': this.env.pos.get_order().cid,
                        'amount': this.env.pos.get_order().get_total_with_tax(),
                        'x_phone': phone,
                        'company_id': this.env.pos.company.id,
                        'reference_id': this.env.pos.get_order().uid,
                        'items': items,
                    }
                }).then(function(result) {
                    if (result.error) {
                        alert(result.error);
                    } else {
                        self.showPopup('TabbyQRCodePopup', {
                            title: self.env._t('Scan QR-code to make a payment'),
                            body: result.qr_code,
                            payment_id: result.payment_id,
                            company_id: result.company_id,
                            confirmText: self.env._t('Continue'),
                            cancelText: self.env._t('Cancel')
                        }).then(function (popupResult) {
                            if (popupResult.confirmed) {
                                self._super_confirm()
                            } else {
                                self.cancel()
                            }
                        })
                    }
                });
            }
        }
        _super_confirm() {
            super.confirm();
        }
    }

    TabbyPopup.template = 'TabbyPopup';
    Registries.Component.add(TabbyPopup);

    return TabbyPopup;
});
