import logging
from datetime import datetime

import requests
from odoo import http, fields
from odoo.addons.point_of_sale.controllers.main import PosController
from odoo.http import request
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

class TebbyPosController(PosController):
    # noinspection PyMethodMayBeStatic
    @http.route('/pos/save_customer_data', type='json', auth='user')
    def save_customer_data(self, **kw):
        company_id = request.env['res.company'].search([('id', '=', kw['company_id'])])
        api_url = "https://api.tabby.ai/api/v2/checkout"
        headers = {
            'Authorization': f'Bearer {company_id.x_api_secret}',
            'Content-Type': 'application/json',
        }
        data = {
            'payment': {
                'amount': '{:.2f}'.format(kw['amount']),
                'currency': company_id.currency_id.display_name,
                'description': kw['description'],
                'buyer': {
                    'phone': kw['x_phone'],
                    'email': kw['x_email'],
                    'name': kw['x_name'],
                    'dob': '2000-01-01',
                },
                'shipping_address': {
                    'city': kw['city'],
                    'address': kw['address'],
                    'zip': kw['zip'],
                },
                'order': {
                    'tax_amount': '{:.2f}'.format(kw['tax_amount']),
                    'shipping_amount': '0.00',  # doesn't have shipping address
                    'discount_amount': '{:.2f}'.format(kw['discount']),
                    'updated_at': fields.Datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'reference_id': kw['reference_id'],
                    'items': kw['items'],
                },
                'buyer_history': {
                    'registered_since': datetime.strptime(kw['buyer_registered_since'], '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'loyalty_level': 0,
                    'wishlist_count': 0,
                    'is_social_networks_connected': False,
                    'is_phone_number_verified': True,
                    'is_email_verified': True
                },
                'order_history': [],
                'meta': {
                    'order_id': kw['cid'],
                    'customer': kw['customer_id']
                },
                'attachment': {
                    'body': '{\'flight_reservation_details\': {\'pnr\': \'TR9088999\',\'itinerary\': [...],\'insurance\': [...],\'passengers\': [...],\'affiliate_name\': \'some affiliate\'}}',
                    'content_type': 'application/vnd.tabby.v1+json'
                }
            },
            'lang': 'en',
            'merchant_code': company_id.x_merchant_code,
            'merchant_urls': {
                'success': f'{request.httprequest.host_url}/payment/success',
                'cancel': f'{request.httprequest.host_url}/payment/cancel',
                'failure': f'{request.httprequest.host_url}/payment/failure',
            },
            'token': None
        }
        response = requests.post(api_url, headers=headers, json=data).json()
        if response.get('status') == 'created':
            payment_data = {
                'id': response.get('id'),
                'payment_id': response.get('payment', {}).get('id'),
                'customer_name': kw['x_name'],
                'customer_phone': kw['x_phone'],
                'customer_email': kw['x_email'],
                'amount': kw['amount'],
                'payment_date': fields.Datetime.now(),
                'company_id': company_id.id,
            }
            request.env['tabby.payment'].sudo().create(payment_data)
            return response
        elif response.get('status') == 'rejected':
            rejection_reasons = {
                'not_available': 'Sorry, Tabby is unable to approve this purchase. Please use an alternative payment method for your order.',
                'order_amount_too_high': 'This purchase is above your current spending limit with Tabby, try a smaller cart or use another payment method',
                'order_amount_too_low': 'The purchase amount is below the minimum amount required to use Tabby, try adding more items or use another payment method',
                'under_limit': 'Tabby currently unavailable, please use an alternative payment method for your order',
            }
            return {'error': rejection_reasons.get(response.get('rejection_reason_code'), '')}

    @http.route('/pos/redirect_to_payment', type='json', auth='user')
    def redirect_to_payment(self, **kw):
        return {'redirect_url': kw['result']['configuration']['available_products']['installments'][0]['web_url']}

    @http.route('/payment/success', type='http', auth='public', website=True)
    def payment_success(self, **kwargs):
        print(kwargs)
        return redirect(f'{request.httprequest.host_url}/pos/web')

    @http.route('/payment/cancel', type='http', auth='public', website=True)
    def payment_cancel(self, **kwargs):
        print(kwargs)
        return redirect(f'{request.httprequest.host_url}/pos/web')

    @http.route('/payment/failure', type='http', auth='public', website=True)
    def payment_failure(self, **kwargs):
        print(kwargs)
        return redirect(f'{request.httprequest.host_url}/pos/web')
