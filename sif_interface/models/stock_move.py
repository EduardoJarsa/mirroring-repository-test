# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        res = super(StockMove, self)._prepare_procurement_values()
        res['sale_line_id'] = self.sale_line_id
        return res
