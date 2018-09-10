# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    kanban_state = fields.Selection([
        ('normal', 'Unauthored'),
        ('done', 'Authorized'),
        ('blocked', 'Blocked')],
        copy=False, default='normal', required=True,)
