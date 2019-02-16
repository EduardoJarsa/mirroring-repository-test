# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    authorized = fields.Boolean()

    @api.multi
    def authorize_sale_order(self):
        self.ensure_one()
        new_name = self.team_id.confirmed_sequence_id.next_by_id()
        new_order = self.copy({
            'authorized': True,
            'origin': self.name,
            'name': new_name,
        })
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': new_order.id,
        }
