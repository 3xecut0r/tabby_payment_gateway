import logging

import requests
from soupsieve.util import lower

from odoo import http, fields
from odoo.addons.point_of_sale.controllers.main import PosController
from odoo.http import request

_logger = logging.getLogger(__name__)


class TabbyPosController(PosController):
    @http.route('/pos/retrieve_data', type='json', auth='user')
    def retrieve_data(self, **kw):
        company_id = request.env['res.company'].search([('id', '=', kw['company_id'])])
        headers = {
            'Authorization': f'Bearer {company_id.x_api_secret}',
            'Content-Type': 'application/json',
        }
        response = requests.get(f'https://api.tabby.ai/api/v2/payments/{kw["payment_id"]}', headers=headers).json()
        if lower(response.get('status')) in ['authorized', 'closed']:
            return {'status': 'Success', 'data': response}
        elif lower(response.get('status')) in ['rejected', 'expired']:
            return {'status': 'Cancelled'}
        return {'status': 'In progress'}

    @http.route('/pos/save_customer_data', type='json', auth='user')
    def save_customer_data(self, **kw):
        company_id = request.env['res.company'].search([('id', '=', kw['company_id'])])
        headers = {
            'Authorization': f'Bearer {company_id.x_api_secret}',
            'Content-Type': 'application/json',
        }
        data = {
            'payment': {
                'amount': '{:.2f}'.format(kw['amount']),
                'currency': company_id.currency_id.display_name,
                'buyer': {
                    'phone': kw['x_phone'],
                },
                'order': {
                    'reference_id': kw['reference_id'],
                    'items': kw['items'],
                },
            },
            'lang': 'en',
            'merchant_code': company_id.x_merchant_code,
        }
        response = requests.post('https://api.tabby.ai/api/v2/checkout', headers=headers, json=data).json()

        if response.get('status') == 'created':
            payment_data = {
                'id': response.get('id'),
                'payment_id': response.get('payment', {}).get('id'),
                'customer_phone': kw['x_phone'],
                'amount': kw['amount'],
                'payment_date': fields.Datetime.now(),
                'company_id': company_id.id,
            }
            request.env['tabby.payment'].sudo().create(payment_data)
            return {'qr_code': response['configuration']['available_products']['installments'][0]['qr_code'],
                    'payment_id': response['payment'].get('id'),
                    'company_id': company_id.id}
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
