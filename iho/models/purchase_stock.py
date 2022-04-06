# Copyright 2022, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
# pylint: disable=R1725


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_picking(self):
        picking_vals = super(PurchaseOrder, self)._prepare_picking()
        if self.origin:
            picking_vals.update({"origin": self.name + " (" + self.origin + ")"})
        return picking_vals


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if self.order_id.origin:
            for v in res:
                v['origin'] = self.order_id.name + " (" + self.order_id.origin + ")"
        return res
