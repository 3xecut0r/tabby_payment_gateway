from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_tabby = fields.Boolean(string='Is Tabby Payment Method', default=False)
