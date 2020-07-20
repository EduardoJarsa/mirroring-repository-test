# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


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
    show_order_details = fields.Selection(
        selection=[('no-show', 'Not shown'), ('show', 'Show'), ],
        default='no-show', required=True,
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

    @api.onchange('iho_tc')
    def _onchange_iho_tc(self):
        if self.iho_tc < 1 or self.iho_tc > 39.99:
            raise ValidationError(
                _('Error: TC Agreed must be [1-39.99]'))

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
                sum(line.service_extended for line in rec.order_line) + \
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
        if self.iho_tc < 1 or self.iho_tc > 39.99:
            raise ValidationError(
                _('Error: TC Agreed must be 1-39.99'))
