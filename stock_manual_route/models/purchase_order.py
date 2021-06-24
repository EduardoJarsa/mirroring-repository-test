# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# Copyright 2021, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        res[0]['move_dest_ids'] = []
        for rec in res:
            rec['analytic_account_id'] = self.account_analytic_id.id
            rec['analytic_tag_ids'] = self.analytic_tag_ids
        return res


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_picking(self):
        res = super()._prepare_picking()
        if self.origin:
            res['origin'] = (
                res['origin'] + " (" + self.origin + ")"
            )
        return res
