odoo.define('tabby_payment_gateway.TabbyQRCodePopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const rpc = require('web.rpc')

    class TabbyQRCodePopup extends AbstractAwaitablePopup {
        async confirm() {
            const result = await rpc.query({
                route: '/pos/retrieve_data',
                params: {
                    payment_id: this.props.payment_id,
                    company_id: this.props.company_id
                }
            });
            if (result.status === 'Success') {
                alert('The payment was completed successfully.');
                this._super_confirm()
            } else if (result.status === 'Cancelled') {
                 alert('The payment was cancelled. Please choose another payment method.');
                this.cancel() // replace

            } else if (result.status === 'In progress') {
                const retry = confirm('The payment is still in progress. Would you like to try again?');
                if (retry) {
                    await this.confirm();
                } else {
                    this.cancel();
                }
            } else {
                alert('An unknown error occurred. Please contact support.');
                this.cancel();
            }
        }
        _super_confirm() {
            super.confirm();
        }
    }
    TabbyQRCodePopup.template = 'TabbyQRCodePopup';
    TabbyQRCodePopup.defaultProps = {
        confirmText: _lt('Continue'),
        cancelText: _lt('Cancel'),
        title: _lt('Scan QR-code to make a payment'),
        body: '',
        payment_id: '',
        company_id: '',
    };

    Registries.Component.add(TabbyQRCodePopup);

    return TabbyQRCodePopup;
});
