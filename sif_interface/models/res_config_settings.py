# Copyright 2020, MtNet, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    order_service_total_minimum_usd = fields.Float(
        default=150.0,
        help="Minimum USD Service total to include in an Order",
        config_parameter="minimum_service_order_usd",
    )
