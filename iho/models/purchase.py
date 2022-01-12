# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_view_picking(self):
        vals = super().action_view_picking()
        self.message_unsubscribe([self.partner_id.id])
        return vals
