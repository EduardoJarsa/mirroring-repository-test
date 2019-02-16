# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    currency_agreed_rate = fields.Float(default=1.0,)
    is_bom = fields.Boolean(
        string="Is Bom?",
        compute="_compute_is_bom",
    )

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
            rec.is_bom = any(self.order_line.mapped('product_id.bom_ids'))


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
    iho_purchase_cost = fields.Float()
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    iho_currency_id = fields.Many2one(
        'res.currency',
        string='IHO Currency',
    )
    is_bom_line = fields.Boolean(
        string="Is Bom?",
        compute="_compute_is_bom_line",
        store=True,
    )

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        if self.filtered('partner_id'):
            for rec in self.filtered('partner_id'):
                partner = rec.product_id.seller_ids.with_context(
                    partner=rec.partner_id, order=rec.order_id).filtered(
                    lambda r: r.name == r._context.get('partner') and
                    r.sale_order_id == r._context.get('order'))
                if not partner:
                    rec.product_id.seller_ids.create({
                        'name': rec.partner_id.id,
                        'delay': 1,
                        'min_qty': 0,
                        'price': rec.iho_purchase_cost,
                        'currency_id': rec.iho_currency_id.id,
                        'product_tmpl_id': rec.product_id.product_tmpl_id.id,
                        'sale_order_id': rec.order_id.id,
                    })
                    return res
                else:
                    partner.write({
                        'price': rec.iho_purchase_cost,
                        'currency_id': rec.iho_currency_id.id,
                    })
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.partner_id:
                partner = rec.product_id.seller_ids.with_context(
                    partner=rec.partner_id, order=rec.order_id).filtered(
                    lambda r: r.name == r._context.get('partner') and
                    r.sale_order_id == r._context.get('order'))
                if not partner:
                    rec.product_id.seller_ids.create({
                        'name': rec.partner_id.id,
                        'delay': 1,
                        'min_qty': 0,
                        'price': rec.iho_purchase_cost,
                        'currency_id': rec.iho_currency_id.id,
                        'product_tmpl_id': rec.product_id.product_tmpl_id.id,
                        'sale_order_id': rec.order_id.id,
                    })
                    return res
                else:
                    partner.write({
                        'price': rec.iho_purchase_cost,
                        'currency_id': rec.iho_currency_id.id,
                    })
        return res

    @api.multi
    @api.depends('product_id')
    def _compute_is_bom_line(self):
        for rec in self:
            rec.is_bom_line = bool(rec.product_id.bom_ids)

    @api.multi
    @api.depends('iho_price_list', 'iho_discount')
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
