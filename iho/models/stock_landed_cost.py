# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    vendors_bill_ids = fields.Many2many(
        'account.move',
    )

    @api.constrains('vendors_bill_ids')
    def _change_vendors_bill_ids(self):
        landed_costs_lines = self.vendors_bill_ids.line_ids.filtered(
            lambda line: line.is_landed_costs_line)
        cost_lines = self._prepare_invoces_lines(landed_costs_lines)
        self.mapped('cost_lines').unlink()
        self.write({
            'cost_lines': cost_lines
        })

    def _prepare_invoces_lines(self, lines):
        cost_lines = []
        for line in lines:
            line_element = self._prepare_line_element(line)
            cost_lines.append(line_element)
        return cost_lines

    def _prepare_line_element(self, line):
        return (0, 0, {
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'account_id': line.product_id.product_tmpl_id.get_product_accounts(
                )['stock_input'].id,
            'price_unit': line.currency_id._convert(
                line.price_subtotal,
                line.company_currency_id,
                line.company_id,
                line.move_id.date),
            'split_method': 'by_current_cost_price',
            })


class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    split_method = fields.Selection(default='by_current_cost_price')
