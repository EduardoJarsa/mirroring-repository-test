# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    authorized = fields.Boolean()

    @api.multi
    def authorize_sale_order(self):
        self.ensure_one()
        if not self.message_is_follower:
            raise ValidationError(
                _('You are not allowed to authorize this Sale Order'))
        if not self.active_version_id:
            raise ValidationError(
                _('You cannot confirm a quotation with no version defined'))
        if self.active_version_id.state == 'confirmed':
            raise ValidationError(
                _('You cannot confirm a quotation with a version that is '
                  'already authorized.'))
        if not self.team_id.confirmed_sequence_id:
            raise ValidationError(
                _('You need to define a confirmation sequence to the '
                  'Sales Team'))
        new_name = self.team_id.confirmed_sequence_id.next_by_id()
        self.active_version_id.sudo().state = 'confirmed'
        new_order = self.copy({
            'authorized': True,
            'origin': '%s %s' % (self.name, self.active_version_id.name),
            'name': new_name,
        })
        message = _('Version %s %s confirmed.') % (
            self.name, self.active_version_id.name)
        self.message_post(body=message)
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': new_order.id,
        }
