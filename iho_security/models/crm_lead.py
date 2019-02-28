# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.multi
    def write(self, vals):
        # Name change: Message for the user
        # if no have the group access to modify.
        if 'name' in vals:
            if not self.user_has_groups(
                    'iho_security.group_sale_salesman_opportunities'):
                raise ValidationError(_(
                    'You cannot modify the name, contact to your admin.'))
        return super().write(vals)
