# Copyright 2020, MtNet Services, S.A. de C.V.
# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    block_ui_crm = fields.Boolean(
        string="Block UI CRM",
        compute='_compute_block_ui_crm',
        default=True)

    def _compute_block_ui_crm(self):
        for record in self:
            record.block_ui_crm = \
                not self.user_has_groups(
                    'ui_simplification.group_show_blocked_fields_CRM')
