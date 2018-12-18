# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, product_id, product_qty,
                                product_uom, origin, values, partner):
        """Method overridden from odoo to set the sale order currency
        as purchase order currency"""
        res = super()._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, partner)
        if values.get('sale_line_id'):
            sale_order = self.env['sale.order'].search(
                [('order_line', 'in', values.get('sale_line_id'))])
            res['currency_id'] = sale_order.currency_id.id
        return res
