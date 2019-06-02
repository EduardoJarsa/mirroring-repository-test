# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image_sol = fields.Binary('Add image', attachment=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.image_medium:
            self.image_sol = self.product_id.image_medium


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery = fields.Text('Delivery time')

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
