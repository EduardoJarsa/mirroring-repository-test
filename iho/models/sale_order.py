# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags',
    )

    @api.onchange('analytic_tag_ids')
    def _onchange_analytic_ids(self):
        self.order_line.update({
            'analytic_tag_ids': False,
        })
        # We need to clear the cache to see correctly the tags in front-end
        self.order_line.invalidate_cache(
            fnames=['analytic_tag_ids'], ids=self.order_line.ids)
        self.order_line.update({
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        })


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
