# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_lower_total = fields.Float(
        readonly=False,
        related="company_id.sale_lower_total",
        help="""Technical field to determine the lower total for the
        quotations used to create the fleet service line. If the amount
        total of one sale order is lower / equal than this total
        the price of the fleet service will be the value of this field.
        Otherwise the price will be 8 percent of the total order.""")
