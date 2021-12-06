# Copyright 2021, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_executive = fields.Char(compute="_compute_default_get")

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        res = super()._onchange_picking_type_id()
        if not self.delivery_address and self.picking_type_id:
            self.delivery_address = self.picking_type_id.warehouse_id.partner_id
        return res

    delivery_address = fields.Many2one('res.partner')

    @api.depends('order_line')
    def _compute_default_get(self):
        domain = [
            ('name', '=', self.origin),
        ]
        candidates = self.env['sale.order'].search(domain).user_id.name
        self.sale_executive = candidates
