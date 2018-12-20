# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image_sol = fields.Binary()

    #for line fleet
    def _get_product_sale(self):
        for rec in self:
            import ipdb; ipdb.set_trace()
            fleet_product = self.env.ref(
                'sale_fleet_service.product_product_fleet_service')
            if product_id == fleet_product.id:
                return product_id.price_unit

class SaleOrderLine(models.Model):
    _inherit = "sale.order"

    #for replace fields
    @api.onchange('note')
    def onchange_replace_strings(self):
        for rec in self:
            import ipdb; ipdb.set_trace()
            currency_id = rec.pricelist_id.currency_id.currency_unit_label
            if rec.note:
                rec.note.replace('place_name', 'x').replace(
                    'currency_id', currency_id if currency_id else '').replace(
                    'conditions_id', 'x').replace(
                    'datetime_del', 'tiempo')
