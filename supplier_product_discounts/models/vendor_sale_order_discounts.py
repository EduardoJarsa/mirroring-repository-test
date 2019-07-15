# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class VendorSaleOrderDiscounts(models.Model):
    _name = 'vendor.sale.order.discounts'

    name = fields.Char()
    sale_id = fields.Many2one(comodel_name='sale.order')
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        related="sale_id.partner_id")
    catalog_id = fields.Many2one('iho.catalog', string='Catalog')
    line_id = fields.Many2one('iho.line', string='line')
    discount = fields.Float(string='Discount (%)',)
