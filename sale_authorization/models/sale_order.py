# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    authorized = fields.Boolean()
    authorized_version = fields.Boolean(compute='_compute_authorized_version')

    @api.multi
    @api.depends('order_version_ids')
    def _compute_authorized_version(self):
        for rec in self:
            if rec.active_version_id.state == 'reviewed':
                self.authorized_version = True

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
        if self.active_version_modified:
            raise ValidationError(
                _('You cannot confirm a quotation without a review.'))
        new_name = self.team_id.confirmed_sequence_id.next_by_id()
        self.active_version_id.sudo().state = 'approved'
        analytic_account = self.env[
            'account.analytic.account'].sudo().create(
                {
                    'name': '%s - %s' % (
                        new_name, self.active_version_name),
                    'partner_id': self.partner_id.id,
                })
        new_order = self.copy({
            'authorized': True,
            'origin': '%s %s' % (self.name, self.active_version_id.name),
            'name': new_name,
            'analytic_account_id': analytic_account.id
        })
        message = _('Version %s %s approved.') % (
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
