# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


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
            rec.is_bom = any(rec.order_line.mapped('product_id.bom_ids'))


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
    iho_sell_4 = fields.Float(
        string="Sell 4",
        compute='_compute_sell_4',
        store=True,)
    iho_sell_5 = fields.Float(
        string="Sell 5",
        compute='_compute_sell_5',
        store=True,)
    iho_purchase_cost = fields.Float(
        compute='_compute_iho_purchase_cost')
    factor_extra_expense = fields.Float(
        default=1.0,
    )
    iho_service_factor = fields.Float(
        string='Service Factor',
        default=1.0,)

    iho_currency_id = fields.Many2one(
        'res.currency',
        string='IHO Currency',
    )
    is_bom_line = fields.Boolean(
        string="Is Bom?",
        compute="_compute_is_bom_line",
        store=True,
    )
    iho_tc = fields.Float(
        string="TC Agreed",
        default=1.0,
    )
    price_unit = fields.Float(
        'Unit Price',
        required=True,
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_price_unit"
    )
    catalog_id = fields.Many2one('iho.catalog', string='Catalog')
    family_id = fields.Many2one('iho.family', string='Family')
    services = fields.Float(
        string='Calculo de Servicio',
    )

    @api.multi
    def _process_product_supplierinfo(self):
        for rec in self:
            if not rec.order_id.partner_id:
                continue
            if not rec.iho_currency_id:
                raise ValidationError(_(
                    'You need to define a purchase currency for the '
                    'product [%s]%s') % (
                        rec.product_id.default_code, rec.product_id.name))
            context = {
                'partner': rec.order_id.partner_id,
                'order': rec.order_id,
            }
            partner = rec.product_id.seller_ids.with_context(
                context).filtered(
                lambda r: r.name == r._context.get('partner') and
                r.sale_order_id == r._context.get('order'))
            if not partner:
                rec.product_id.seller_ids.create({
                    'name': rec.order_id.partner_id.id,
                    'delay': 1,
                    'min_qty': 0,
                    'price': rec.iho_purchase_cost,
                    'currency_id': rec.iho_currency_id.id,
                    'product_tmpl_id': rec.product_id.product_tmpl_id.id,
                    'sale_order_id': rec.order_id.id,
                })
            else:
                partner.write({
                    'price': rec.iho_purchase_cost,
                    'currency_id': rec.iho_currency_id.id,
                })

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        res._process_product_supplierinfo()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        self._process_product_supplierinfo()
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # set value from sale prder
        self.iho_tc = self.order_id.currency_agreed_rate

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
    @api.depends('iho_sell_1')
    def _compute_iho_purchase_cost(self):
        for rec in self:
            rec.iho_purchase_cost = rec.iho_sell_1

    @api.multi
    @api.depends('iho_sell_1', 'iho_factor')
    def _compute_sell_2(self):
        for rec in self:
            rec.iho_sell_2 = rec.iho_sell_1 * rec.iho_factor

    @api.multi
    @api.depends('iho_tc', 'iho_sell_2')
    def _compute_sell_3(self):
        for rec in self:
            rec.iho_sell_3 = rec.iho_sell_2 * rec.iho_tc

    @api.multi
    @api.depends('iho_service_factor', 'iho_sell_3')
    def _compute_sell_4(self):
        for rec in self:
            rec.iho_sell_4 = rec.iho_sell_3 * rec.iho_service_factor

    @api.multi
    @api.depends('iho_sell_4', 'factor_extra_expense')
    def _compute_sell_5(self):
        for rec in self:
            amount = rec.iho_sell_4 * rec.factor_extra_expense
            if amount:
                rec.iho_sell_5 = amount
                rec._compute_price_unit()
            else:
                rec.price_unit = rec.product_id.lst_price

    @api.multi
    @api.depends('product_id')
    def _compute_price_unit(self):
        for rec in self:
            if rec.iho_sell_5 and rec.iho_sell_5 != 0.0:
                rec.price_unit = rec.iho_sell_5
            else:
                rec.price_unit = rec.product_id.lst_price
            # This code fix a problem with the calcule of subtotal
            discount = (
                (rec.product_uom_qty * rec.price_unit) *
                (rec.discount / 100))
            subtotal = (rec.product_uom_qty * rec.price_unit) - discount
            rec.price_subtotal = subtotal

    @api.onchange('product_uom', 'product_uom_qty', 'product_id')
    def product_uom_change(self):
        res = super().product_uom_change()
        if self.iho_sell_4:
            self.price_unit = self.iho_sell_4
        return res
