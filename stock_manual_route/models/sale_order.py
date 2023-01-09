# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _unlink_pincking_int(self, picking_int):
        if picking_int:
            picking_int.write(
                {
                    "state": "draft",
                }
            )
            picking_int.move_lines.write(
                {
                    "state": "draft",
                }
            )
            picking_int.unlink()

    def _put_account_and_tags_in_moves(self, picking_out):
        if picking_out:
            picking_out.move_ids_without_package.write(
                {
                    "analytic_tag_ids": self.analytic_tag_ids.ids,
                    "analytic_account_id": self.analytic_account_id.id,
                }
            )

    def action_confirm(self):
        res = super().action_confirm()
        picking_int = self.picking_ids.filtered(
            lambda l: l.picking_type_id.code == "internal" and l.picking_type_id.sequence_code == "INT"
        )
        picking_out = self.picking_ids.filtered(
            lambda l: l.picking_type_id.code == "outgoing" and l.picking_type_id.sequence_code == "OUT"
        )
        self._unlink_pincking_int(picking_int)
        self._put_account_and_tags_in_moves(picking_out)
        return res
