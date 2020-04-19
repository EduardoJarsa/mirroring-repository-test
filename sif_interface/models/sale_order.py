# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    currency_agreed_rate = fields.Float(default=1.0,)
    extra_expenses = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        help="Expenses to add to the total of the order",
    )
    service_total = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_service_total",
        store=True,
        help="Total cost of the service of the order",
    )
    show_service_total = fields.Selection(
        selection=[('not-shown', 'Not shown'), ('at-lines', 'At each line'),
                   ('sub-total', 'As a subtotal'), ],
        default='at-lines', required=True, )
    is_bom = fields.Boolean(
        string="Is Bom?",
        compute="_compute_is_bom",
    )

    @api.onchange('extra_expenses')
    def _onchange_extra_expenses(self):
        if self.extra_expenses < 0:
            raise ValidationError(_('Extra Expenses cannot be negative'))

    @api.onchange('currency_agreed_rate')
    def _onchange_currency_agreed_rate(self):
        if self.currency_agreed_rate <= 0:
            raise ValidationError(
                _('Currency Agreed Rate illegal value entered'))

    @api.constrains('currency_agreed_rate', 'extra_expenses')
    def _check_negative_values_header(self):
        if self.currency_agreed_rate <= 0 or self.extra_expenses < 0:
            raise ValidationError(
                _('Negative values are not allowed for Currency'
                  ' or Extra expenses'))

    @api.onchange('currency_agreed_rate', 'pricelist_id', 'company_id')
    def _onchange_currency_agreed_rate(self):
        if (self.currency_agreed_rate > 1 and
                self.pricelist_id.currency_id != self.company_id.currency_id):
            raise ValidationError(
                _('You cannot set an agreed rate when the Sale Order currency '
                  'is different from the company currency'))

    @api.constrains('pricelist_id', 'currency_agreed_rate')
    def _check_currency_agreed_rate(self):
        if (self.currency_agreed_rate > 1 and
                self.pricelist_id.currency_id != self.company_id.currency_id):
            raise ValidationError(
                _('You cannot set an agreed rate when the Sale Order currency '
                  'is different from the company currency'))

    @api.multi
    @api.depends('order_line')
    def _compute_is_bom(self):
        for rec in self:
            rec.is_bom = any(rec.order_line.mapped('product_id.bom_ids'))

    @api.multi
    @api.depends('order_line')
    def _compute_service_total(self):
        for rec in self:
            rec.service_total = sum(
                line.service_extended for line in rec.order_line)
