# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_version_ids = fields.One2many(
        'sale.order.version',
        'sale_id',
        'Sale Order Versions',
        copy=False,
    )
    has_lines = fields.Boolean(
        compute='_compute_has_lines',
    )
    active_version_name = fields.Char(
        readonly=True,
        copy=False,
    )

    @api.multi
    @api.depends('order_line')
    def _compute_has_lines(self):
        for rec in self:
            rec.has_lines = bool(rec.order_line)

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.active_version_name:
                order.order_version_ids.filtered(
                    lambda v: v.name ==
                    order.active_version_name).sudo().write({
                        'state': 'confirm',
                    })
        return res
