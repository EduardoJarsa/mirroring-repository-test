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
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags',
    )

    @api.onchange('route_id')
    def _onchange_route_id(self):
        self.order_line.update({
            'route_id': self.route_id.id,
        })

    @api.onchange('analytic_tag_ids')
    def _onchange_analytic_ids(self):
        self.order_line.update({
            'analytic_tag_ids': False,
        })
        # We need to clear the cache to see correctly the tags in front-end
        self.order_line.invalidate_cache(
            fnames=['analytic_tag_ids'], ids=self.order_line.ids)
        self.order_line.update({
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        })


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def _onchange_product_id_set_route(self):
        self.route_id = self.order_id.route_id.id

    @api.onchange('product_id')
    def _onchange_product_id_set_analytic_tags(self):
        self.analytic_tag_ids = False
        # We need to clear the cache to see correctly the tags in front-end
        self.invalidate_cache(
            fnames=['analytic_tag_ids'], ids=[self.id])
        self.analytic_tag_ids = self.order_id.analytic_tag_ids.ids
