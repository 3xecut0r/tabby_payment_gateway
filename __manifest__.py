{
    'name': 'Tabby Payment Gateway',
    'version': '15.0.1.0.1',
    'summary': 'Integrate Tabby Payment Gateway with Odoo POS',
    'description': """
    This module integrates Tabby Payment Gateway with Odoo POS, allowing customers to use Tabby as a payment method.
    """,
    'category': 'Point of Sale',
    'author': 'Oleksii Panpukha',
    'website': 'Website',
    'depends': [
        'base',
        'point_of_sale'
    ],
    'data': [
        'views/pos_config_views.xml',
        'views/tabby_payment_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'tabby_payment_gateway/static/src/js/payment_screen.js',
            'tabby_payment_gateway/static/src/js/tabby_popup.js',
        ],
        'web.assets_qweb': [
            'tabby_payment_gateway/static/src/xml/tabby_popup.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
