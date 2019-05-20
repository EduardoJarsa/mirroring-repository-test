# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_feedback(self, feedback=False):
        so_obj = self.env['sale.order'].browse(
            self._context.get('params').get('id'))
        if so_obj or so_obj.active_version_id:
            so_obj.active_version_id.state = 'reviewed'
        return super(MailActivity, self).action_feedback(feedback)
