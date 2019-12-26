# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_sol = fields.Binary('Add image', attachment=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.image_medium:
            self.image_sol = self.product_id.image_medium


class SaleOrderTerm(models.Model):
    _name = 'sale.order.term'
    _description = 'Terms and Conditions for Sales Order'
    _order = 'sequence asc'

    name = fields.Html(required=True)
    order_id = fields.Many2one('sale.order', required=True)
    term_id = fields.Many2one('sale.term', required=True)
    sequence = fields.Integer(required=True, default=10)

    @api.model
    def create(self, values):
        res = False
        order = self.env['sale.order'].browse(values['order_id'])
        term_to_compare = self.env['sale.term'].browse(
            values['term_id'])
        invalid_terms = ''
        terms_sale_order = order.mapped(
            'sale_order_term_ids.term_id')
        if 'sale_version_id' not in values:
            if term_to_compare in terms_sale_order:
                raise ValidationError(_('This term is already in Sale Order'))
        else:
            values.pop('sale_version_id', None)
        # Compare with invalid combination of sale order
        for rec in terms_sale_order:
            for so_term in rec.invalid_term_ids.ids:
                if so_term == term_to_compare.id:
                    invalid_terms = invalid_terms + rec.name + ','
        if invalid_terms:
            raise ValidationError(
                _('Unable to add this term, it is not compatible '
                    'with the terms. %s') % invalid_terms[:-1])
        # Compare with invalid combination of term than you want add
        for rec in term_to_compare:
            for so_term in terms_sale_order:
                if so_term.id in rec.invalid_term_ids.ids:
                    invalid_terms = invalid_terms + so_term.name + ','
        if invalid_terms:
            raise ValidationError(
                _('Unable to add this term, it is not compatible '
                    'with the terms. %s') % invalid_terms[:-1])
        res = super().create(values)
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery = fields.Text('Delivery time')
    sale_order_term_ids = fields.One2many(
        'sale.order.term', 'order_id', string='Terms and Conditions')

    @api.multi
    def generate_terms(self):
        for rec in self:
            context = {
                'lang': rec.partner_id.lang
            }
            if rec.sale_order_term_ids:
                for term in rec.sale_order_term_ids:
                    term.name = safe_eval(
                        term.with_context(context).name, {
                            'order': rec.with_context(context)
                        })
                return True
            terms = self.env['sale.term'].search(
                [('default', '=', True)], order='sequence asc')
            new_terms = []
            # Use context to allow to get translation from terms.
            for term in terms:
                new_terms.append({
                    'name': safe_eval(
                        term.with_context(context).name, {
                            'order': rec.with_context(context)
                        }),
                    'order_id': rec.id,
                    'term_id': term.id,
                    'sequence': term.sequence,
                })
            rec.sale_order_term_ids.create(new_terms)

    @api.multi
    def get_product_freight(self):
        for rec in self.mapped('order_line'):
            fleet_product = self.env.ref(
                'sale_fleet_service.product_product_fleet_service')
            if rec.product_id.id == fleet_product.id:
                return {
                    'unit_price': rec.price_unit,
                    'product_id': rec.product_id.id
                }

    @api.multi
    def find_images(self):
        images = []
        for rec in self.mapped('order_line'):
            if rec.image_sol:
                images.append(rec.product_id)
        if not images:
            return False

    amount_services = fields.Float(
        compute='_compute_amount_services')

    @api.depends('order_line')
    def _compute_amount_services(self):
        for rec in self:
            order_lines = rec.order_line
            services = 0
            for line in order_lines:
                percentage_service = line.iho_service_factor - 1
                services += (
                    line.iho_sell_3 * percentage_service
                    * line.product_uom_qty
                    * (1 - (line.discount / 100))
                )
            rec.amount_services = services

    def _return_code(self, code):
        str_descr = ''
        for char in code:
            if char != "]":
                str_descr = str_descr + char
            else:
                break
        return str_descr[1:]

    def _return_description(self, descr):
        count_char = 0
        for char in descr:
            if char != "]":
                count_char += 1
            else:
                break
        count_char += 1
        return descr[count_char:]
