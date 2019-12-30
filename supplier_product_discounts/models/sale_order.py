# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import json


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    vendor_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain=[
            ('supplier', '=', True),
            ('ref', '!=', False), ('is_company', '=', True)]
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.vendor_id = self.product_id.maker_id.id


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discounts_ids = fields.One2many(
        'vendor.sale.order.discounts', 'sale_id',
        copy=False)

    @api.multi
    def _validate_discounts(self):
        order_lines = self.order_line
        makers = self.order_line.mapped('vendor_id')
        catalogs = self.order_line.mapped('catalog_id')
        families = self.order_line.mapped('family_id')
        combination_discounts = []
        # This method get de combination with percentage
        # to validate the discounts
        self._get_combinations_discounts(
            makers,
            catalogs,
            families,
            order_lines,
            combination_discounts
        )
        comb_disc_str = '\n'
        for rec in combination_discounts:
            # This structure is to create a json format
            # for combination discounts
            structure = {
                'maker': rec['maker'],
                'catalog': rec['catalog'],
                'family': rec['family'],
                'percentage': rec['percentage'],
            }
            app_json = json.dumps(structure, indent=4)
            comb_disc_str = comb_disc_str + str(app_json)
        catalog_error = []
        general_discounts = self.env[
            'vendor.product.discounts'].search(
                [('id', '!=', False)])
        for catalog in combination_discounts:
            # This get the combination from SO
            discount = self._get_array_of_discounts(
                catalog, self.discounts_ids, general_discounts)
            self._compare_discounts(discount, catalog, catalog_error)
        if catalog_error:
            msg = ''
            for rec in catalog_error:
                if rec['maker'] and rec['catalog'] and rec['family']:
                    message = (
                        _('{ maker %s catalog %s family %s'
                            '\n the offered discount is %s and the approved'
                            ' discount is %s}\n')
                        % (rec['maker'], rec['catalog'],
                            rec['family'],
                            rec['discount_offered'],
                            rec['discount_accepted'])
                    )
                    msg = msg + message
                if rec['maker'] and rec['catalog'] and not rec['family']:
                    message = (
                        _('{ maker %s catalog %s'
                            '\n The offered discount is %s and the approved'
                            ' discount is %s}\n')
                        % (rec['maker'], rec['catalog'],
                            rec['discount_offered'],
                            rec['discount_accepted'])
                    )
                    msg = msg + message
                if rec['maker'] and rec['family'] and not rec['catalog']:
                    message = (
                        _('{ maker %s family %s'
                            '\n The offered discount is %s and the approved'
                            ' discount is %s}\n')
                        % (rec['maker'], rec['family'],
                            rec['discount_offered'],
                            rec['discount_accepted'])
                    )
                    msg = msg + message
                if rec['maker'] and not rec['catalog'] and not rec['family']:
                    message = (
                        _('{ maker %s'
                            '\n the offered discount is %s and the approved'
                            ' discount is %s}\n')
                        % (rec['maker'],
                            rec['discount_offered'],
                            rec['discount_accepted'])
                    )
                    msg = msg + message
                if rec['catalog'] and not rec['maker'] and not rec['family']:
                    message = (
                        _('{ catalog %s'
                            '\n the offered discount is %s and the approved'
                            ' discount is %s}\n')
                        % (rec['catalog'],
                            rec['discount_offered'],
                            rec['discount_accepted'])
                    )
                    msg = msg + message
                if rec['family'] and not rec['catalog'] and not rec['maker']:
                    message = (
                        _('{ family %s'
                            '\n the offered discount is %s and the approved'
                            ' discount is %s}\n')
                        % (rec['family'],
                            rec['discount_offered'],
                            rec['discount_accepted'])
                    )
                    msg = msg + message
            raise ValidationError(msg)

    def _get_three_filter(
        self,
        catalog,
        discounts,
        general_discounts
    ):
        if (
            catalog['maker_id']
            and catalog['catalog_id']
            and catalog['family_id']
        ):
            filter_tree_comb = discounts.filtered(
                lambda l: l.partner_id == catalog['maker_id']
                and l.catalog_id == catalog['catalog_id']
                and l.family_id == catalog['family_id']
            )
            if filter_tree_comb:
                return filter_tree_comb
            filter_tree_comb = general_discounts.filtered(
                lambda l: l.partner_id == catalog['maker_id']
                and l.catalog_id == catalog['catalog_id']
                and l.family_id == catalog['family_id']
            )
            gral_discounts = filter_tree_comb
            if gral_discounts:
                return gral_discounts

    def _get_two_filter_comb_1(
        self,
        catalog,
        discounts_ids,
        general_discounts
    ):
        if catalog['maker_id'] and catalog['catalog_id']:
            filter_two_comb_1 = discounts_ids.filtered(
                lambda l: l.partner_id == catalog['maker_id']
                and l.catalog_id == catalog['catalog_id']
                and not l.family_id
            )
            if filter_two_comb_1:
                return filter_two_comb_1
            filter_two_comb_1 = general_discounts.filtered(
                lambda l: l.partner_id == catalog['maker_id']
                and l.catalog_id == catalog['catalog_id']
                and not l.family_id
            )
            gral_discounts = filter_two_comb_1
            if gral_discounts:
                return gral_discounts

    def _get_two_filter_comb_2(self, catalog, discounts, general_discounts):
        if catalog['maker_id'] and catalog['family_id']:
            filter_two_comb_2 = discounts.filtered(
                lambda l: l.partner_id == catalog['maker_id']
                and l.family_id == catalog['family_id']
                and not l.catalog_id)
            if filter_two_comb_2:
                return filter_two_comb_2
            filter_two_comb_2 = general_discounts.filtered(
                lambda l: l.partner_id == catalog['maker_id']
                and l.family_id == catalog['family_id']
                and not l.catalog_id)
            gral_discounts = filter_two_comb_2
            if gral_discounts:
                return gral_discounts

    def _filter_by_maker(self, catalog, discounts):
        filter_maker_id = discounts.filtered(
            lambda l: l.partner_id == catalog['maker_id']
            and not l.catalog_id
            and not l.family_id)
        return filter_maker_id

    def _get_global_discounts(self, catalog, discounts):
        filter_global_discounts = discounts.filtered(
            lambda l: not l.partner_id
            and not l.catalog_id
            and not l.family_id
        )
        return filter_global_discounts

    def _get_array_of_discounts(
        self,
        catalog,
        discounts_ids,
        general_discounts
    ):
        filter_discounts = False
        filter_discounts = self._get_three_filter(
            catalog, discounts_ids, general_discounts)
        if not filter_discounts:
            filter_discounts = self._get_two_filter_comb_1(
                catalog, discounts_ids, general_discounts)
        if not filter_discounts:
            filter_discounts = self._get_two_filter_comb_2(
                catalog, discounts_ids, general_discounts)
        if not filter_discounts:
            if catalog['maker_id']:
                filter_maker_id = self._filter_by_maker(
                    catalog, discounts_ids)
                if filter_maker_id:
                    return filter_maker_id
                gral_discounts = self._filter_by_maker(
                    catalog, general_discounts)
                if gral_discounts:
                    return gral_discounts
            if (
                not catalog['maker_id']
                and not catalog['catalog_id']
                and not catalog['family_id']
            ):
                global_discounts = self._get_global_discounts(
                    catalog, discounts_ids)
                if global_discounts:
                    return global_discounts
                gral_discounts_global_disc = self._get_global_discounts(
                    catalog, general_discounts)
                if gral_discounts_global_disc:
                    return gral_discounts_global_disc
        return filter_discounts

    def _compare_discounts(
        self,
        discount,
        catalog,
        catalog_error
    ):
        new_error_discount = False
        success = 0
        # major_discount = self._reduce_discounts(discounts, catalog)
        if discount:
            discount_conv = discount.discount / 100
            if discount_conv >= catalog['percentage']:
                success = success + 1
        else:
            if not discount and catalog['percentage'] == 0.0:
                success = success + 1
        if not success:
            exist = 0
            if catalog_error:
                for rec in catalog_error:
                    if (
                        rec['maker_id'] == catalog['maker_id']
                        and rec['catalog_id'] == catalog['catalog_id']
                            and rec['family_id'] == catalog['family_id']):
                        exist = exist + 1
            if not exist:
                new_error_discount = ({
                    'maker': catalog['maker'],
                    'maker_id': catalog['maker_id'],
                    'catalog': catalog['catalog'],
                    'catalog_id': catalog['catalog_id'],
                    'family': catalog['family'],
                    'family_id': catalog['family_id'],
                    'discount_offered': '{percent:.2%}'.format(
                        percent=catalog['percentage']),
                })
                if discount:
                    new_error_discount.update(
                        {'discount_accepted': '{percent:.2%}'.format(
                            percent=discount.discount / 100)})
                else:
                    new_error_discount.update(
                        {'discount_accepted': 0})
                catalog_error.append(new_error_discount)

    def _reduce_discounts(self, discounts, catalog):
        major = 0
        major_discount = []
        for discount in discounts:
            if discount['maker_id'] == catalog['maker_id']:
                discount_conv = discount['discount'] / 100
                if discount_conv > major:
                    major_discount = discount
                    major = major_discount['discount'] / 100
        return major_discount

    def _filter_all_combinations(
        self,
        family,
        maker,
        catalog,
        combination_discounts,
        order_lines,
    ):
        # filter maker , catalog, family
        filter_tree_comb = order_lines.filtered(
            lambda l: l.vendor_id == maker
            and l.catalog_id == catalog
            and l.family_id == family
        )
        if filter_tree_comb:
            self._add_combination_discount(
                filter_tree_comb,
                combination_discounts,
                maker,
                catalog,
                family
            )
        # filter maker , catalog, not family
        filter_two_comb_1 = order_lines.filtered(
            lambda l: l.vendor_id == maker
            and l.catalog_id == catalog
            and not l.family_id
        )
        if filter_two_comb_1:
            self._add_combination_discount(
                filter_two_comb_1,
                combination_discounts,
                maker,
                catalog,
                False
            )
        # filter maker , family not catalog
        filter_two_comb_2 = order_lines.filtered(
            lambda l: l.vendor_id == maker
            and l.family_id == family
            and not l.catalog_id
        )
        if filter_two_comb_2:
            self._add_combination_discount(
                filter_two_comb_2,
                combination_discounts,
                maker,
                False,
                family
            )
        filter_maker_id = order_lines.filtered(
            lambda l: l.vendor_id == maker
        )
        # filter only maker
        if filter_maker_id:
            self._add_combination_discount(
                filter_maker_id,
                combination_discounts,
                maker,
                False,
                False
            )

    def _get_combinations_discounts(
        self,
        makers,
        catalogs,
        families,
        order_lines,
        combination_discounts,
    ):
        for maker in makers:
            for catalog in catalogs:
                for family in families:
                    self._filter_all_combinations(
                        family,
                        maker,
                        catalog,
                        combination_discounts,
                        order_lines)

    def _add_combination_discount(
        self,
        sale_lines,
        combination_discounts,
        maker=False,
        catalog=False,
        family=False
    ):
        subtotal = 0
        new_subtotal = 0
        percentage = 0
        if sale_lines:
            for order_line in sale_lines:
                subtotal = (
                    subtotal + (order_line.product_uom_qty)
                    * (order_line.price_unit)
                )
                new_subtotal = (
                    new_subtotal + (order_line.price_subtotal))
            percentage = (1 - (new_subtotal / subtotal))
            combination = ({
                'original_sub': subtotal,
                'new_subtotal': new_subtotal,
                'percentage': percentage,
            })
            if maker:
                combination.update({
                    'maker': maker.name,
                    'maker_id': maker,
                })
            else:
                combination.update({
                    'maker': False,
                    'maker_id': False,
                })
            if catalog:
                combination.update({
                    'catalog': catalog.name,
                    'catalog_id': catalog,
                })
            else:
                combination.update({
                    'catalog': False,
                    'catalog_id': False,
                })
            if family:
                combination.update({
                    'family': family.name,
                    'family_id': family,
                })
            else:
                combination.update({
                    'family': False,
                    'family_id': False,
                })
            combination_discounts.append(combination)

    @api.multi
    def review_sale_order(self):
        res = super().review_sale_order()
        self._validate_discounts()
        return res


class SaleOrderVersionCreateWizard(models.TransientModel):
    _inherit = 'sale.order.version.create.wizard'

    @api.multi
    def create_version(self):
        res = super().create_version()
        self.sale_id._validate_discounts()
        return res
