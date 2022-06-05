# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class VendorProductDiscounts(models.Model):
    _name = 'vendor.product.discounts'
    _description = 'Discounts allowed per vendor/product'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', string='Partner')
    catalog_id = fields.Many2one('iho.catalog', string='Catalog')
    family_id = fields.Many2one('iho.family', string='Family')
    discount = fields.Float(string='Discount (%)',)
    active = fields.Boolean(default=True)
