# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("qty_done")
    def _onchange_qty_done(self):
        if self.qty_done > self.product_uom_qty:
            raise ValidationError(_("The qty done must be lower or" " equal than the initial demand."))
