# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    iho_purchase_cost = fields.Float()
    iho_customer_cost = fields.Float()
    vendor_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    iho_currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
    )

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        obj_sale_order = self.env['sale.order']
        if self.vendor_id:
            order_name = self.bom_id.product_tmpl_id.name.split('-')[1].strip()
            order = obj_sale_order.search([('name', '=', order_name)])
            partner = self.product_id.seller_ids.with_context(
                partner=self.vendor_id, order=order).filtered(
                lambda r: r.name == r._context.get('partner') and
                r.sale_order_id == r._context.get('order'))
            if not partner:
                self.product_id.seller_ids.create({
                    'name': self.vendor_id.id,
                    'delay': 1,
                    'min_qty': 0,
                    'price': self.iho_purchase_cost,
                    'currency_id': self.iho_currency_id.id,
                    'product_tmpl_id': self.product_id.product_tmpl_id.id,
                    'sale_order_id': order.id,
                })
                return res
            partner.write({
                'price': self.iho_purchase_cost,
                'currency_id': self.iho_currency_id.id,
            })
        return res

    @api.multi
    def create(self, vals):
        res = super().create(vals)
        obj_sale_order = self.env['sale.order']
        if self.vendor_id:
            order_name = self.bom_id.product_tmpl_id.name.split('-')[1].strip()
            order = obj_sale_order.search([('name', '=', order_name)])
            partner = self.product_id.seller_ids.with_context(
                partner=self.vendor_id, order=order).filtered(
                lambda r: r.name == r._context.get('partner') and
                r.sale_order_id == r._context.get('order'))
            if not partner:
                self.product_id.seller_ids.create({
                    'name': self.vendor_id.id,
                    'delay': 1,
                    'min_qty': 0,
                    'price': self.iho_purchase_cost,
                    'currency_id': self.iho_currency_id.id,
                    'product_tmpl_id': self.product_id.product_tmpl_id.id,
                    'sale_order_id': order.id,
                })
                return res
            partner.write({
                'price': self.iho_purchase_cost,
                'currency_id': self.iho_currency_id.id,
            })
        return res
