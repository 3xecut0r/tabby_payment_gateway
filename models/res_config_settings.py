from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_tabby = fields.Boolean('Is Tabby Payment Method', related='company_id.use_tabby', readonly=False)
    api_token = fields.Char('API Token', related='company_id.x_api_token', readonly=False)
    api_secret = fields.Char('API Secret', related='company_id.x_api_secret', readonly=False)
    merchant_code = fields.Char('Merchant Code', related='company_id.x_merchant_code', readonly=False)

    @api.onchange('is_tabby')
    def _onchange_is_tabby(self):
        if self.is_tabby:
            if self.company_id.currency_id.display_name not in ['AED', 'SAR', 'KWD', 'BHD', 'QAR']:
                raise ValidationError(
                    f"Tabby cannot be enabled because the company currency '{self.company_id.currency_id.display_name}' is not supported. Supported currencies are: {', '.join(['AED', 'SAR', 'KWD', 'BHD', 'QAR'])}.")

        # if self.is_tabby and not self.env['pos.payment.method'].search([('is_tabby', '=', True)], limit=1):
        #     tabby_journal = self.env['account.journal'].search([('name', '=', 'Tabby Journal'), ('type', '=', 'bank')],
        #                                                        limit=1)
        #     if not tabby_journal:
        #         tabby_journal = self.env['account.journal'].create({
        #             'name': 'Tabby Journal',
        #             'code': 'TABBY',
        #             'type': 'bank',
        #             'company_id': self.env.company.id,
        #             'currency_id': self.env.company.currency_id.id,
        #         })
        #
        #     self.env['pos.payment.method'].create({
        #         'name': 'Tabby',
        #         'is_tabby': self.is_tabby,
        #         'journal_id': tabby_journal.id,
        #     })
