# Copyright 2019, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    analytic_tag_ids = fields.Many2many(
        "account.analytic.tag",
        string="Analytic Tags",
    )
