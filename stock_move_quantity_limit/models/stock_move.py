# Copyright 2018, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange("quantity_done")
    def _onchange_quantity_done(self):
        if self.quantity_done > self.product_uom_qty:
            raise ValidationError(_("The qty done must be lower or equal than the initial demand."))
