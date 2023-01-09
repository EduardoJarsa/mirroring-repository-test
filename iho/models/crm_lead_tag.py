# Copyright 2020, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class CrmLeadTag(models.Model):
    _inherit = "crm.lead.tag"
    _order = "name"
