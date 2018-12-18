# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _merge_in_existing_line(self, product_id, product_qty, product_uom,
                                location_id, name, origin, values):
        """Method overrided from odoo to avoid the purchase order line merging.
           This functionallity is not necessary because the company needs to
           keep the product separated in different order lines"""
        return False
