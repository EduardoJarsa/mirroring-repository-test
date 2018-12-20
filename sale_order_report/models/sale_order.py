# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image_sol = fields.Binary('Add image', attachment=True)

    @api.multi
    def _get_product_freight(self):
        for rec in self:
            fleet_product = self.env.ref(
                'sale_fleet_service.product_product_fleet_service')
            if rec.product_id.id == fleet_product.id:
                return rec.product_id.price_unit
