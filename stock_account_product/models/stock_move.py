# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value,
                                       credit_value, debit_account_id,
                                       credit_account_id):
        res = super()._generate_valuation_lines_data(
            partner_id, qty, debit_value, credit_value,
            debit_account_id, credit_account_id)
        res['debit_line_vals']['name'] = self.product_id.name or self.name
        res['credit_line_vals']['name'] = self.product_id.name or self.name
        return res
