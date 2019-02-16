# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "crm.team"

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence',
        ondelete='restrict',
        help='The sequence selected on this field will be passed '
        'to the sale team selected in the Sale Order.')
    confirmed_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Confirmed Sequence',
        ondelete='restrict',
        help='The sequence selected on this field will be passed '
        'to the Sale Order when is confirmed')
