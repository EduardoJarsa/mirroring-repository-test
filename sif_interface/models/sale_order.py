# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    extra_expenses = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_extra_expenses",
        store=True,
        help="Expenses to add to the total of the order",
    )
    service_total = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_service_total",
        store=True,
        help="Total cost of the service of the order",
    )
    discount_total = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_discount_total",
        store=True,
        help="Total value of discount of the order",
    )
    product_total = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_product_total",
        store=True,
        help="Total cost of the products of the order",
    )
    show_order_details = fields.Boolean(
        default=False,
    )
    is_bom = fields.Boolean(
        string="Is Bom?",
        compute="_compute_is_bom",
    )
    iho_tc = fields.Float(
        string="TC Agreed",
        default=1.0,
        digits=dp.get_precision('Precision Sale Terms'),
    )
    show_errors = fields.Char(
        default=False,
    )

    @api.onchange('iho_tc')
    def _onchange_iho_tc(self):
        if self.iho_tc < 1 or self.iho_tc > 49.99:
            raise ValidationError(
                _('Error: TC Agreed must be [1-49.99]'))

    @api.onchange('extra_expenses')
    def _onchange_extra_expenses(self):
        if self.extra_expenses < 0:
            raise ValidationError(_('Extra Expenses cannot be negative'))

    @api.constrains('extra_expenses')
    def _check_negative_values_header(self):
        for rec in self:
            if rec.extra_expenses < 0:
                raise ValidationError(
                    _('Extra Expenses cannot be negative'))

    @api.constrains('service_total')
    def _check_minimum_service_total(self):
        for rec in self:
            usd = self.env.ref('base.USD')
            mxn = self.env.ref('base.MXN')
            curr_rate_usd = \
                usd._convert(1, mxn, rec.company_id, datetime.today())
            # curr_rate_usd = 20
            if not curr_rate_usd:
                curr_rate_usd = 20
            min_service_usd = float(
                self.env['ir.config_parameter'].sudo().get_param(
                    'minimum_service_order_usd'))
            if not min_service_usd:
                min_service_usd = 0.0
            rec.show_errors = False
            if rec.pricelist_id.currency_id == self.env.ref("base.USD"):
                if rec.service_total < min_service_usd:
                    rec.show_errors = (
                        _('Service total is less than %s USD') %
                        min_service_usd)
            else:
                if rec.service_total < min_service_usd * curr_rate_usd:
                    rec.show_errors = (
                        _('Service total is less than the equivalent'
                            ' of %s USD') % min_service_usd)

    @api.depends('order_line')
    def _compute_is_bom(self):
        for rec in self:
            rec.is_bom = any(rec.order_line.mapped('product_id.bom_ids'))

    @api.depends('order_line')
    def _compute_service_total(self):
        product_product_service = \
            self.env.ref('sif_interface.product_product_service',
                         raise_if_not_found=False)
        for rec in self:
            if not product_product_service:
                rec.service_total = 0
                continue
            rec.service_total = \
                sum(line.service_extended
                    for line in rec.order_line.filtered(
                        lambda l: l.product_id != product_product_service)) + \
                sum(line.price_subtotal
                    for line in rec.order_line.filtered(
                        lambda l: l.product_id == product_product_service)
                    )

    @api.depends('order_line')
    def _compute_discount_total(self):
        for rec in self:
            rec.discount_total = sum(
                line.discount_extended for line in rec.order_line)

    @api.depends('order_line')
    def _compute_product_total(self):
        for rec in self:
            rec.product_total = sum(
                line.product_extended for line in rec.order_line)

    @api.depends('order_line')
    def _compute_extra_expenses(self):
        product_product_extraexpenses = \
            self.env.ref('sif_interface.product_product_extraexpenses',
                         raise_if_not_found=False)
        for rec in self:
            if not product_product_extraexpenses:
                rec.extra_expenses = 0
                continue
            rec.extra_expenses = \
                sum(line.price_subtotal
                    for line in rec.order_line.filtered(
                        lambda l:
                        l.product_id == product_product_extraexpenses)
                    )

    @api.constrains('iho_tc')
    def _constrains_iho_tc(self):
        if self.iho_tc < 1 or self.iho_tc > 49.99:
            raise ValidationError(
                _('Error: TC Agreed must be 1-49.99'))
