# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    designer_ids = fields.Many2many(
        'res.users',
        string='Designer',
    )
    route_id = fields.Many2one(
        'stock.location.route',
        string='Route',
        domain=[('sale_selectable', '=', True)],
        ondelete='restrict',
        help='The route selected on this field will be passed '
        'to all the sale order lines of this quotation.',)

    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.route_id:
            self.order_line.update({
                'route_id': self.route_id.id,
            })


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def _onchange_product_id_set_route(self):
        if self.order_id.route_id:
            self.route_id = self.order_id.route_id.id
