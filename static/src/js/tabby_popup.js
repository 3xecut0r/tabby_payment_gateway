odoo.define('tabby_payment_gateway.TabbyPopup', function (require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const rpc = require('web.rpc')

    class TabbyPopup extends AbstractAwaitablePopup {

        confirm() {
            const self = this;
            const name = this.el.querySelector('input[name="name"]').value;
            // const phone = this.el.querySelector('input[name="phone"]').value;
            // const email = this.el.querySelector('input[name="email"]').value;
            // const dob = this.el.querySelector('input[name="dob"]').value;
            if (!name ) this.cancel();
            const orderlines = this.env.pos.get_order().orderlines.models;
            const items = orderlines.map(line => {
                return {
                    'title': line.get_product().display_name,
                    'description': line.get_product().description_sale || '',
                    'quantity': line.get_quantity(),
                    'unit_price': line.get_price_with_tax().toFixed(2),
                    'discount_amount': line.get_discount() ? (line.get_price_with_tax() * line.get_discount() / 100).toFixed(2) : '0.00',
                    'reference_id': line.get_product().id.toString(),
                    'image_url': '',
                    'product_url': '',
                    'gender': 'Unisex',
                    'category': line.get_product().categ_id[1],
                    'color': 'N/A',
                    'product_material': 'N/A',
                    'size_type': 'N/A',
                    'size': 'N/A',
                    'brand': 'N/A',
                };
            });
            if (!this.env.pos.get_order().attributes.client ) {
                this.cancel();
                this.showPopup('ErrorPopup', {
                    title: this.env._t('You didn\'t pick the customer'),
                    body: this.env._t('Please choose a customer'),
                });
            } else if (!this.env.pos.get_order().attributes.client.address || !this.env.pos.get_order().attributes.client.city || !this.env.pos.get_order().attributes.client.zip) {
                this.cancel();
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Missing Address'),
                    body: this.env._t('The selected customer does not have a complete address. Please provide the address, city, and postal code before proceeding.'),
                });
            } else {
                console.log(this.env.pos.get_order());
                const result = rpc.query({
                    route: '/pos/save_customer_data',
                    params: {
                        'cid': this.env.pos.get_order().cid,
                        'amount': this.env.pos.get_order().get_total_with_tax(),
                        'description': this.env.pos.get_order().name,
                        'x_name': name,
                        'x_phone': this.env.pos.get_order().attributes.client.phone || this.env.pos.get_order().attributes.client.mobile,
                        'x_email': this.env.pos.get_order().attributes.client.email,
                        'x_dob': '1996-04-16', // random date
                        'company_id': this.env.pos.company.id,
                        'address': this.env.pos.get_order().attributes.client.address,
                        'city': this.env.pos.get_order().attributes.client.city,
                        'zip': this.env.pos.get_order().attributes.client.zip,
                        'buyer_registered_since': this.env.pos.get_order().attributes.client.write_date,
                        'tax_amount': this.env.pos.get_order().get_total_tax(),
                        'reference_id': this.env.pos.get_order().uid,
                        'discount': this.env.pos.get_order().get_total_discount(),
                        'items': items,
                        'customer_id': this.env.pos.get_order().attributes.client.id,
                    }
                }).then(function(result) {
                    if (result.error) {
                        alert(result.error);
                    } else {
                        return rpc.query({
                            route: '/pos/redirect_to_payment',
                            params: {
                                'result': result
                            }
                        });
                    }
                }).then(function(redirectData) {
                    if (redirectData && redirectData.redirect_url) {
                        window.location.href = redirectData.redirect_url;
                    } else if (!redirectData) {
                        self.cancel()
                        alert('An unexpected error occurred. Please use an alternative payment method for your order.');
                    } else {
                        self._super_confirm();
                    }
                }).catch(function(err) {
                    self.cancel()
                    console.error("RPC Error:", err);
                    alert("An error occurred while processing the payment. Please try again.");
                    self.cancel()
                });
            }
        }

        _super_confirm() {
            super.confirm();  // Вызов super в отдельном методе
        }
    }

    TabbyPopup.template = 'TabbyPopup';
    Registries.Component.add(TabbyPopup);

    return TabbyPopup;
});
