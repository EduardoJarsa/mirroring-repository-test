# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_sol = fields.Binary('Add image', attachment=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.image_medium:
            self.image_sol = self.product_id.image_medium


class SaleOrderTerm(models.Model):
    _name = 'sale.order.term'
    _description = 'Terms and Conditions for Sales Order'
    _order = 'sequence asc'

    name = fields.Html(required=True)
    order_id = fields.Many2one('sale.order', required=True)
    term_id = fields.Many2one('sale.term', required=True)
    sequence = fields.Integer(required=True, default=10)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery = fields.Text('Delivery time')
    sale_order_term_ids = fields.One2many(
        'sale.order.term', 'order_id', string='Terms and Conditions')

    @api.multi
    def generate_terms(self):
        for rec in self:
            terms = self.env['sale.term'].search([('default', '=', True)])
            rec.sale_order_term_ids.unlink()
            new_terms = []
            # Use context to allow to get translation from terms.
            context = {
                'lang': rec.partner_id.lang
            }
            for term in terms:
                new_terms.append({
                    'name': safe_eval(
                        term.with_context(context).name, {
                            'order': rec.with_context(context)
                        }),
                    'order_id': rec.id,
                    'term_id': term.id,
                    'sequence': term.sequence,
                })
            rec.sale_order_term_ids.create(new_terms)

    @api.multi
    def get_product_freight(self):
        for rec in self.mapped('order_line'):
            fleet_product = self.env.ref(
                'sale_fleet_service.product_product_fleet_service')
            if rec.product_id.id == fleet_product.id:
                return {
                    'unit_price': rec.price_unit,
                    'product_id': rec.product_id.id
                }

    @api.multi
    def find_images(self):
        images = []
        for rec in self.mapped('order_line'):
            if rec.image_sol:
                images.append(rec.product_id)
        if not images:
            return False
