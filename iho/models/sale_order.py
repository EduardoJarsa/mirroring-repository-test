# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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

    @api.onchange('product_id')
    def _onchange_product_id_set_analytic_tags(self):
        self.analytic_tag_ids = False
        # We need to clear the cache to see correctly the tags in front-end
        self.invalidate_cache(
            fnames=['analytic_tag_ids'], ids=[self.id])
        self.analytic_tag_ids = self.order_id.analytic_tag_ids.ids

    @api.constrains('price_unit')
    def _onchange_price_unit(self):
        if self.price_unit == 1.0:
            raise ValidationError(
                _('Error: Column "Price Unit" at [%s] has value of [%s] '
                  'and must NOT be [1]') %
                (self._product_int_ref(), self.price_unit))
