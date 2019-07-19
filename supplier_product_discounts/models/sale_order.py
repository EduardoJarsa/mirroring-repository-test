# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    vendor_id = fields.Many2one(
        'res.partner',
        string='Partner',
        related="product_id.maker_id",
        domain=[
            ('supplier', '=', True),
            ('ref', '!=', False), ('is_company', '=', True)]
    )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discounts_ids = fields.One2many(
        'vendor.sale.order.discounts', 'sale_id',
        copy=False)

    @api.multi
    def get_discounts(self, lines):
        catalog_disc = {}
        for line in lines:
            if line.discount:
                vendor = (
                    line.product_id.maker_id.name
                    if line.product_id.maker_id else '')
                catalog = (
                    line.product_id.catalog_id.name
                    if line.product_id.catalog_id else '')
                family = (line.product_id.family_id.name
                          if line.product_id.family_id else '')
                key = (vendor + ' ' + catalog + ' ' + family)
                amount_with_tax = ((line.product_uom_qty *
                                    line.price_unit) + line.price_tax)
                discounts = float(
                    amount_with_tax - (amount_with_tax * (
                        1.0 - line.discount / 100.0)))
                if key not in catalog_disc.keys():
                    catalog_disc[key] = {
                        'catalog': line.product_id.catalog_id.name,
                        'family': line.product_id.family_id.name,
                        'partner': line.vendor_id.id,
                        'total': 0.00,
                        'discount': 0.00,
                    }
                catalog_disc[key]['discount'] += discounts
                catalog_disc[key]['total'] += (amount_with_tax)
        return catalog_disc

    @api.multi
    def get_levels(self, gt_lvl3, gt_lvl4, so_lvl3, so_lvl4):
        general_table = gt_lvl3
        sale_order_table = so_lvl3
        if not general_table and not sale_order_table:
            general_table = gt_lvl4
            sale_order_table = so_lvl4
        return {
            'general_table': general_table,
            'sale_order_table': sale_order_table}

    @api.multi
    def compare_discounts(self):
        message = _(
            'You exceded limit discount '
            'for: %s , discount: %s')
        for k, v in self.get_discounts(self.order_line).items():
            general_discount = (
                self.env['vendor.product.discounts'].search(
                    [('partner_id.id', '=', v['partner'])]))
            sale_discount = self.env['vendor.sale.order.discounts'].search(
                [('partner_id.id', '=', v['partner']),
                 ('sale_id.id', '=', self.id)])
            general_discount_lvl1 = (
                general_discount.filtered(
                    lambda l: l.family_id.name == v['family'] and
                    l.catalog_id.name == v['catalog']))
            sale_discount_lvl1 = sale_discount.filtered(
                lambda l: l.family_id.name == v['family'] and
                l.catalog_id.name == v['catalog'])
            general_discount_lvl2 = (
                general_discount.filtered(
                    lambda l: not l.family_id and
                    l.catalog_id.name == v['catalog']))
            sale_discount_lvl2 = sale_discount.filtered(
                lambda l: not l.family_id and
                l.catalog_id.name == v['catalog'])
            general_discount_lvl3 = general_discount.filtered(
                lambda l: not l.family_id and
                not l.catalog_id)
            sale_discount_lvl3 = sale_discount.filtered(
                lambda l: not l.family_id and
                not l.catalog_id)
            general_discount_lvl4 = (
                self.env['vendor.product.discounts'].search(
                    [('partner_id', '=', False),
                     ('catalog_id', '=', False),
                     ('family_id', '=', False),
                     ('discount', '!=', False)]))
            sale_discount_lvl4 = (
                self.env['vendor.sale.order.discounts'].search(
                    [('partner_id', '=', False),
                     ('catalog_id', '=', False),
                     ('family_id', '=', False),
                     ('discount', '!=', False),
                     ('sale_id.id', '=', self.id)]))
            general_table = False
            sale_order_table = False
            catalog_disc = (
                ((v['discount'] / v['total']) * 100.00)
                if (v['discount'] or v['total']) else 0.00)
            if not general_discount and not sale_discount:
                general_table = general_discount_lvl4
                sale_order_table = sale_discount_lvl4
                if not general_table and not sale_order_table:
                    raise ValidationError(
                        message % (k, round(catalog_disc, 2)))
            if v['catalog'] is not False and v['family'] is not False:
                general_table = general_discount_lvl1
                sale_order_table = sale_discount_lvl1
                if not general_table and not sale_order_table:
                    general_table = general_discount_lvl2
                    sale_order_table = sale_discount_lvl2
                    if not general_table and not sale_order_table:
                        general_table = self.get_levels(
                            general_discount_lvl3,
                            sale_discount_lvl3, general_discount_lvl4,
                            sale_discount_lvl4,)['general_table']
                        sale_order_table = self.get_levels(
                            general_discount_lvl3,
                            sale_discount_lvl3, general_discount_lvl4,
                            sale_discount_lvl4,)['sale_order_table']
            elif v['catalog'] is not False and not v['family']:
                general_table = general_discount_lvl2
                sale_order_table = sale_discount_lvl2
                if not general_table and not sale_order_table:
                    general_table = self.get_levels(
                        general_discount_lvl3,
                        sale_discount_lvl3, general_discount_lvl4,
                        sale_discount_lvl4,)['general_table']
                    sale_order_table = self.get_levels(
                        general_discount_lvl3,
                        sale_discount_lvl3, general_discount_lvl4,
                        sale_discount_lvl4,)['sale_order_table']
            elif (
                (not v['catalog'] and not v['family']) or
                    (v['catalog'] is not False and
                        v['family'] is not False)):
                general_table = self.get_levels(
                    general_discount_lvl3,
                    sale_discount_lvl3, general_discount_lvl4,
                    sale_discount_lvl4,)['general_table']
                sale_order_table = self.get_levels(
                    general_discount_lvl3,
                    sale_discount_lvl3, general_discount_lvl4,
                    sale_discount_lvl4,)['sale_order_table']
            if general_table.discount < sale_order_table.discount:
                if round(catalog_disc, 2) > sale_order_table.discount:
                    raise ValidationError(
                        message % (k, round(catalog_disc, 2)))
            elif round(catalog_disc, 2) > general_table.discount:
                raise ValidationError(message % (k, round(catalog_disc, 2)))

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
