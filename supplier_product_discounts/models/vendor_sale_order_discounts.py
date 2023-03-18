# Copyright 2019, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class VendorSaleOrderDiscounts(models.Model):
    _name = "vendor.sale.order.discounts"
    _description = "Discounts set per Sale Order"

    name = fields.Char()
    sale_id = fields.Many2one(comodel_name="sale.order")
    partner_id = fields.Many2one("res.partner", string="Partner")
    catalog_id = fields.Many2one("iho.catalog", string="Catalog")
    family_id = fields.Many2one("iho.family", string="Family")
    discount = fields.Float(
        string="Discount (%)",
    )
