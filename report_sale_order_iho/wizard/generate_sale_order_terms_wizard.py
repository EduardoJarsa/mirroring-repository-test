# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).g

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class GenerateSaleOrderTermsWizard(models.TransientModel):
    _name = 'generate.sale.order.terms.wizard'
    _description = 'Add terms to Sale Order'

    term_id = fields.Many2one('sale.term')
    category_id = fields.Many2one('sale.term.category')
    order_id = fields.Many2one('sale.order')
    term_ids = fields.Many2many(
        'sale.term', string='Terms and Conditions')

    @api.model
    def default_get(self, res_fields):
        res = super().default_get(res_fields)
        order = self.env['sale.order'].browse(
            self._context.get('active_id', False))
        res['order_id'] = order.id
        res['term_ids'] = order.mapped('sale_order_term_ids.term_id').ids
        return res

    def add_term_to_sale_order(self):
        if self._context.get('active_model') != 'sale.order':
            return False
        if not self.term_id:
            raise ValidationError(_('There is not selected a sale term.'))
        context = {
            'lang': self.order_id.partner_id.lang
        }
        new_terms = []
        new_terms.append({
            'order_id': self.order_id.id,
            'term_id': self.term_id.id,
            'sequence': self.term_id.sequence,
            'name': safe_eval(
                self.term_id.with_context(context).name, {
                    'order': self.order_id.with_context(context),
                }),
        })
        self.env['sale.order.term'].create(new_terms)
