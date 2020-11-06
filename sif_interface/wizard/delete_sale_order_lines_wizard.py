# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class DeleteSaleOrderLinesWizard(models.TransientModel):
    _name = "delete.sale.order.lines.wizard"
    _description = "Deletes all lines of the sale order"

    def run_delete_all_lines(self):
        self.ensure_one()
        sale_order = self.env[
            self._context.get('active_model')].browse(
                self._context.get('active_id'))
        sale_order.write({
            'order_line': [(5, 0, 0)]
            })
