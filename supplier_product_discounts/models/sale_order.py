# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    discounts_ids = fields.One2many(
        'vendor.sale.order.discounts', 'sale_id', copy=False)
