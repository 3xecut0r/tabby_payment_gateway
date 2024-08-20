from odoo import models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _default_payment_methods(self):
        payment_methods = super(PosConfig, self)._default_payment_methods()

        tabby_payment_method = self.env['pos.payment.method'].search(
            [('is_tabby', '=', True), ('company_id', '=', self.env.company.id)], limit=1)

        if tabby_payment_method:
            if self.env.company.use_tabby and tabby_payment_method not in payment_methods:
                payment_methods |= tabby_payment_method
            elif not self.env.company.use_tabby and tabby_payment_method in payment_methods:
                payment_methods -= tabby_payment_method

        return payment_methods
