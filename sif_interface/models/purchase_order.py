# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _merge_in_existing_line(self, product_id, product_qty, product_uom,
                                location_id, name, origin, values):
        """Method overrided from odoo to avoid the purchase order line merging.
           This functionallity is not necessary because the company needs to
           keep the product separated in different order lines"""
        return False

    @api.model
    def create(self, vals):
        sale_order = False
        if self._context.get('active_model') == 'sale.order':
            sale_order = self.env['sale.order'].browse(
                self._context.get('active_id'))
        res = super().create(vals)
        res.write({
            'account_analytic_id': sale_order.analytic_account_id.id,
            'analytic_tag_ids': [
                (6, 0, sale_order.analytic_tag_ids.ids)],
        })
        return res
