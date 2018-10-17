# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    currency_agreed_rate = fields.Float(default=1.0,)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    iho_price_list = fields.Float(string='Price List',)
    iho_discount = fields.Float(string='IHO Discount (%)',)
    iho_sell_1 = fields.Float(
        string='Sell 1',
        compute="_compute_sell_1",
        store=True,)
    iho_factor = fields.Float(
        string='Factor',
        default=1.0,)
    iho_sell_2 = fields.Float(
        string="Sell 2",
        compute='_compute_sell_2',
        store=True,)
    iho_sell_3 = fields.Float(
        string="Sell 3",
        compute='_compute_sell_3',
        store=True,)

    @api.multi
    @api.depends('iho_price_list')
    def _compute_sell_1(self):
        for rec in self:
            rec.iho_sell_1 = rec.iho_price_list * (1 - rec.iho_discount / 100)

    @api.multi
    @api.depends('iho_sell_1', 'iho_factor')
    def _compute_sell_2(self):
        for rec in self:
            rec.iho_sell_2 = rec.iho_sell_1 * rec.iho_factor

    @api.multi
    @api.depends('order_id.currency_agreed_rate', 'iho_sell_2')
    def _compute_sell_3(self):
        for rec in self:
            amount = rec.iho_sell_2 * rec.order_id.currency_agreed_rate
            rec.update({
                'iho_sell_3': amount,
                'price_unit': amount,
            })
