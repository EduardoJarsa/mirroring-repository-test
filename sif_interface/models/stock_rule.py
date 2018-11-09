# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_select_supplier(self, values, suppliers):
        res = super(StockRule, self)._make_po_select_supplier(
            values, suppliers)
        supplier = suppliers.with_context(values=values).filtered(
            lambda r: r.sale_order_id == r._context.get(
                'values').get('group_id').sale_id and r.sale_order_id) or res
        return supplier

    @api.multi
    def _prepare_purchase_order_line(
            self, product_id, product_qty, product_uom, values, po, partner):
        res = super(StockRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner)
        res['sale_line_id'] = values.get('sale_line_id').id
        return res
