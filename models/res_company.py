from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    use_tabby = fields.Boolean(string='Use Tabby')
    x_api_token = fields.Char(string='API Key')
    x_api_secret = fields.Char(string='API Secret')
    x_merchant_code = fields.Char(string='Merchant Code')