# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    display_on_footer = fields.Boolean()
