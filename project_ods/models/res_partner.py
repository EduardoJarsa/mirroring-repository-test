# Copyright 2021, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    service_order_sequence_id = fields.Many2one(
        'ir.sequence',
        help='Service Orders Sequence for the service center',
    )
