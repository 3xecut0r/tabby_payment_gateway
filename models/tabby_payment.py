from odoo import api, fields, models


class TebbyPayment(models.Model):
    _name = 'tabby.payment'
    _description = 'Tabby Payment'
    _order = 'create_date desc'

    name = fields.Char(string='ID of response')
    payment_id = fields.Char(string='Payment ID')
    customer_phone = fields.Char(string='Customer Phone')
    reference_id = fields.Char(string='Reference ID')
    amount = fields.Float(string='Amount')
    payment_date = fields.Datetime(string='Payment Date', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if 'name' not in vals or not vals['name']:
            vals['name'] = self.env['ir.sequence'].next_by_code('tabby.payment') or 'New'
        return super(TebbyPayment, self).create(vals)

    def write(self, vals):
        return super(TebbyPayment, self).write(vals)
