# Copyright 2020, MTNET Services, S.A. de C.V.
# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CrmLeadBlockUI(models.Model):
    _inherit = 'utm.source'

    _order = 'name asc'
