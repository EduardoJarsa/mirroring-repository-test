# Copyright 2021, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_address = fields.Many2one('res.partner',)
