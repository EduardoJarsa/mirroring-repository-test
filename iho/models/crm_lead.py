# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def write(self, vals):
        # Name change: Message for the user
        # if no have the group access to modify.
        for rec in self:
            if "name" in vals:
                if vals.get("name") == rec.name:
                    break
                if not self.user_has_groups("iho.group_sale_salesman_opportunities"):
                    raise ValidationError(_("You cannot modify the name, contact to your admin."))
        return super().write(vals)
