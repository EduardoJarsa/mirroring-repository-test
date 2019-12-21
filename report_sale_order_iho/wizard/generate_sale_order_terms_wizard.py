# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).g

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class GenerateSaleOrderTermsWizard(models.TransientModel):
    _name = 'generate.sale.order.terms.wizard'

    sale_order_term_id = fields.Many2one(
        'sale.term',
    )

    @api.multi
    def add_term_to_sale_order(self):
        if self._context.get('active_model') == 'sale.order':
            sale_order = self.env['sale.order'].browse(
                self._context.get('active_id'))
            context = {
                'lang': sale_order.partner_id.lang
            }
            new_terms = []
            new_terms.append({
                'name': safe_eval(
                    self.sale_order_term_id.with_context(context).name, {
                        'order': sale_order.with_context(context)
                    }),
                'order_id': sale_order.id,
                'term_id': self.sale_order_term_id.id,
                'sequence': self.sale_order_term_id.sequence,
            })
            sale_order.sale_order_term_ids.create(new_terms)
