# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        picking = self.picking_ids.filtered(
            lambda l: l.picking_type_id.code == 'internal'
            and l.picking_type_id.sequence_code == 'INT')
        if picking:
            picking.write({
                'state': 'draft',
            })
            picking.move_lines.write({
                'state': 'draft',
            })
            picking.unlink()
        return res
