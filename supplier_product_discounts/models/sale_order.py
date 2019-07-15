# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discounts_ids = fields.One2many(
        'vendor.sale.order.discounts', 'sale_id',
        copy=False)

    @api.multi
    def get_discounts(self, lines):
        catalog_disc = {}
        for line in lines:
            key = (
                line.product_id.catalog_id.name + '/' +
                line.product_id.line_id.name)
            import ipdb; ipdb.set_trace()
            # discount = (
            #     (line.product_uom_qty line.price_unit) * line.discount)
            if key not in catalog_disc.keys():
                catalog_disc[key] = {
                    'partner_id': line.order_id.partner_id.id,
                    'catalog': line.product_id.catalog_id.name,
                    'line': line.product_id.line_id.name,
                    'discount': 0.00,
                }
            catalog_disc[key]['discount'] += (
                line.discount)
        return catalog_disc

    @api.multi
    def _action_confirm(self):
        for rec in self:

            for k, v in self.get_discounts(self.order_line).items():
                general_discount = (
                    self.env['vendor.product.discounts'].search(
                        [('partner_id.id', '=', v['partner_id']),
                         ('catalog_id.name', '=', v['catalog']),
                         ('line_id.name', '=', v['line'])]))
                disc = self.env['vendor.sale.order.discounts'].search(
                    [('sale_id.id', '=', self.id),
                     ('partner_id.id', '=', v['partner_id']),
                     ('catalog_id.name', '=', v['catalog']),
                     ('line_id.name', '=', v['line'])])
                if (general_discount) or (disc):
                    if general_discount.discount > disc.discount:
                        if round(v['discount'], 2) > general_discount.discount:
                            raise Warning(_(
                                'You exceded limit discount '
                                'for the catalog: %s '
                                % (v['catalog'])))
                        if disc:
                            if round(v['discount'], 2) > disc.discount:
                                raise Warning(_(
                                    'You exceded limit discount '
                                    'for the catalog: %s '
                                    % (v['catalog'])))
        super(SaleOrder, self)._action_confirm()
