# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class ResCountry(models.Model):
    _inherit = 'res.country'

    def write(self, values):
        if 'demonym' not in values and not self.user_has_groups(
                'iho_security.group_manager_catalogs'):
            raise UserError(
                _("You don't have access to modify the country."))
        return super().write(values)
