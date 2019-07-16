# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
            amount_with_tax = ((line.product_uom_qty *
                                line.price_unit) + line.price_tax)
            discounts = float(
                amount_with_tax - (amount_with_tax * (
                    1.0 - line.discount / 100.0)))
            if key not in catalog_disc.keys():
                catalog_disc[key] = {
                    'catalog': line.product_id.catalog_id.name,
                    'line': line.product_id.line_id.name,
                    'total': 0.00,
                    'discount': 0.00,
                }
            catalog_disc[key]['discount'] += discounts
            catalog_disc[key]['total'] += (amount_with_tax)
        return catalog_disc

    @api.multi
    def compare_discounts(self):
        message = _(
            'You exceded limit discount '
            'for: %s , discount: %s')
        for k, v in self.get_discounts(self.order_line).items():
            general_discount = (
                self.env['vendor.product.discounts'].search(
                    [('catalog_id.name', '=', v['catalog']),
                     ('line_id.name', '=', v['line'])]))
            sale_discount = self.env['vendor.sale.order.discounts'].search(
                [('sale_id.id', '=', self.id),
                 ('catalog_id.name', '=', v['catalog']),
                 ('line_id.name', '=', v['line'])])
            catalog_disc = (v['discount'] / v['total']) * 100.0
            for line_disc in general_discount:
                if line_disc.discount < sale_discount.discount:
                    if catalog_disc > sale_discount.discount:
                        raise ValidationError(message % (k, catalog_disc))
                elif catalog_disc > line_disc.discount:
                    raise ValidationError(message % (k, catalog_disc))

    @api.multi
    def review_sale_order(self):
        res = super().review_sale_order()
        self.compare_discounts()
        return res


class SaleOrderVersionCreateWizard(models.TransientModel):
    _inherit = 'sale.order.version.create.wizard'

    @api.multi
    def create_version(self):
        res = super().create_version()
        self.sale_id.compare_discounts()
        return res
