# Copyright 2018, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    iho_price_list = fields.Float(
        string='Price List',
        help='Vendor Catalog public price',
    )
    customer_discount = fields.Float(
        string='Customer Discount (%)',
        digits=dp.get_precision('Precision Sale Terms'),
        help='Discount (%) to the customer [0 - 100]',
    )
    iho_sell_1 = fields.Float(
        string='Sell 1',
        compute="_compute_sell_1",
        store=True,
    )
    iho_factor = fields.Float(
        string='Factor',
        digits=dp.get_precision('Precision Sale Terms'),
        default=1.0,
        help='IHO Factor',
    )
    iho_sell_2 = fields.Float(
        string="Sell 2",
        compute='_compute_sell_2',
        store=True,
    )
    iho_sell_3 = fields.Float(
        string="Sell 3",
        compute='_compute_sell_3',
        store=True,
    )
    iho_sell_4 = fields.Float(
        string="Sell 4",
        compute='_compute_sell_4',
        store=True,
    )
    iho_purchase_cost = fields.Float(
        compute='_compute_iho_purchase_cost',
        help='Calculated purchase cost',
    )
    iho_service_factor = fields.Float(
        string='Service Factor',
        default=1.06,
        digits=dp.get_precision('Precision Sale Terms'),
        help='Allowed Service Factor values [1 - 1.99], standard of 1.06'
             ' or $150 usd; and 1.125 or 250 usd for textiles.',
    )
    iho_currency_id = fields.Many2one(
        'res.currency',
        string='IHO Currency',
    )
    show_order_details = fields.Selection(
        selection=[('no-show', 'Not shown'), ('show', 'Show'), ],
        default='no-show', required=True,
        related='order_id.show_order_details',
    )
    is_bom_line = fields.Boolean(
        string="Is Bom?",
        compute="_compute_is_bom_line",
        store=True,
    )
    price_unit = fields.Float(
        'Unit Price',
        required=True,
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_price_unit"
    )
    dealer_discount = fields.Float(
        string="Dealer discount (%)",
        required=True,
        digits=dp.get_precision('Product Price'),
        default=0.0,
    )
    service_extended = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_service_extended",
        help="Total cost of the service of the order line",
    )
    discount_extended = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_discount_extended",
        help="Total value of the discount offered in the order line",
    )
    product_extended = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=0.0,
        compute="_compute_product_extended",
        help="Total value of the products offered in the order line",
    )
    iho_tc = fields.Float(
        related='order_id.iho_tc',
        store=True,
    )


    catalog_id = fields.Many2one('iho.catalog', string='Catalog')
    family_id = fields.Many2one('iho.family', string='Family')

    # Field level validation at entry time
    @api.onchange('customer_discount')
    def _onchange_customer_discount(self):
        if self.customer_discount < 0 or self.customer_discount > 100:
            raise ValidationError(
                _('Error: Customer discount must be [0-100]'))

    @api.onchange('iho_factor')
    def _onchange_iho_factor(self):
        if self.iho_factor < 1 or self.iho_factor > 3.99:
            raise ValidationError(
                _('Error: Factor must be [1-9.99]'))

    @api.onchange('iho_service_factor')
    def _onchange_iho_service_factor(self):
        if self.product_id.type in ('product', 'consu') and\
                (self.iho_service_factor < 1 or
                 self.iho_service_factor > 1.99):
            raise ValidationError(
                _('Error: Service factor must be [1-1.99]'))
        if self.product_id.type == 'service' and self.iho_service_factor != 1:
            raise ValidationError(_('Error: Service factor must be [1]'))


    #
    @api.model
    def _product_int_ref(self):
        int_ref = self.product_id.default_code
        if not int_ref or self.product_id == \
                self.env.ref('sif_interface.product_product_dummy'):
            int_ref = self.name[1:self.name.find(']')]
        return int_ref

    # Field level validation at saving time
    @api.constrains('dealer_discount')
    def _onchange_dealer_discount(self):
        if self.dealer_discount < 0 or self.dealer_discount > 100:
            raise ValidationError(
                _('Error: Column "Dealer discount" at [%s] has value of [%s] '
                  'and must be [0-100]') %
                (self._product_int_ref(), self.dealer_discount))

    @api.constrains('customer_discount')
    def _constrains_customer_discount(self):
        if self.customer_discount < 0 or self.customer_discount > 100:
            raise ValidationError(
                _('Error: Column "Customer discount" at [%s] has value '
                  ' of [%s] and must be [0-100]') %
                (self._product_int_ref(), self.customer_discount))

    @api.constrains('iho_factor')
    def _constrains_iho_factor(self):
        if self.iho_factor < 1 or self.iho_factor > 3.99:
            raise ValidationError(
                _('Error: Column "Factor" at [%s] has value of [%s] '
                  'and must be [1-3.99]') %
                (self._product_int_ref(), self.iho_factor))

    @api.constrains('iho_service_factor')
    def _constrains_iho_service_factor(self):
        if self.product_id.type in ('product', 'consu') and\
                (self.iho_service_factor < 1 or
                 self.iho_service_factor > 1.99):
            raise ValidationError(
                _('Error: Column "Service factor" at [%s] has value of [%s] '
                  'and must be [1-1.99]') %
                (self._product_int_ref(), self.iho_service_factor))
        if self.product_id.type == 'service' and \
                self.iho_service_factor != 1.0:
            raise ValidationError(
                _('Error: Column "Service factor" at [%s] has value of '
                  '[%s] and must be [1]') %
                (self._product_int_ref(), self.iho_service_factor))

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

    @api.multi
    @api.depends('product_id')
    def _compute_is_bom_line(self):
        for rec in self:
            rec.is_bom_line = bool(rec.product_id.bom_ids)

    @api.multi
    @api.depends('iho_price_list', 'iho_factor')
    def _compute_sell_1(self):
        for rec in self:
            rec.iho_sell_1 = \
                rec.iho_price_list * rec.iho_factor

    @api.multi
    @api.depends('iho_price_list', 'dealer_discount')
    def _compute_iho_purchase_cost(self):
        for rec in self:
            rec.iho_purchase_cost = \
                rec.iho_price_list * (1 - rec.dealer_discount/100)

    @api.multi
    @api.depends('iho_sell_1', 'customer_discount')
    def _compute_sell_2(self):
        for rec in self:
            rec.iho_sell_2 = \
                rec.iho_sell_1 * (1-rec.customer_discount/100)

    @api.multi
    @api.depends('iho_sell_2', 'iho_service_factor')
    def _compute_sell_3(self):
        for rec in self:
            rec.iho_sell_3 = rec.iho_sell_2 * rec.iho_service_factor

    @api.multi
    @api.depends('iho_sell_3', 'iho_tc')
    def _compute_sell_4(self):
        for rec in self:
            rec.iho_sell_4 = rec.iho_sell_3 * rec.iho_tc

    @api.multi
    @api.depends('iho_sell_4')
    def _compute_price_unit(self):
        for rec in self:
            if rec.iho_sell_4 and rec.iho_sell_4 != 0.0:
                rec.price_unit = rec.iho_sell_4
            else:
                rec.price_unit = rec.product_id.lst_price

    @api.multi
    @api.depends('product_id', 'iho_price_list', 'iho_factor',
                 'customer_discount', 'product_uom_qty')
    def _compute_discount_extended(self):
        for rec in self:
            rec.discount_extended = -\
                rec.iho_price_list * rec.iho_factor * \
                rec.customer_discount/100 * rec.iho_tc * rec.product_uom_qty

    @api.multi
    @api.depends(
        'product_id', 'iho_price_list',
        'iho_service_factor', 'product_uom_qty')
    def _compute_service_extended(self):
        for rec in self:
            if rec.product_id.type in ('product', 'consu'):
                rec.service_extended = \
                    rec.iho_price_list * rec.iho_factor * \
                    (1 - (rec.customer_discount / 100)) * \
                    (rec.iho_service_factor-1) * \
                    rec.product_uom_qty * rec.iho_tc
            else:
                rec.service_extended = \
                    rec.iho_price_list * rec.iho_factor * \
                    (1 - (rec.customer_discount / 100)) * \
                    rec.product_uom_qty * rec.iho_tc

    @api.multi
    @api.depends(
        'product_id', 'iho_price_list', 'product_uom_qty')
    def _compute_product_extended(self):
        for rec in self:
            if rec.product_id.type in ('product', 'consu'):
                rec.product_extended = \
                    rec.iho_price_list * rec.iho_factor * \
                    (1 - (rec.customer_discount / 100)) * \
                    rec.product_uom_qty * rec.iho_tc
            else:
                rec.product_extended = 0.0
