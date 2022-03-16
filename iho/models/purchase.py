# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_view_picking(self):
        vals = super().action_view_picking()
        self.message_unsubscribe([self.partner_id.id])
        return vals

    amount_untaxed_usd = fields.Float(
        string='usd Untaxed',
        compute='_compute_amount_untaxed_usd',
        store=True,
    )
    amount_total_usd = fields.Float(
        string='usd Total',
        compute='_compute_amount_total_usd',
        store=True,
    )

    @api.depends('amount_untaxed')
    def _compute_amount_untaxed_usd(self):
        for rec in self:
            rec.amount_untaxed_usd = rec.currency_id._convert(
                rec.amount_untaxed,
                self.env.ref('base.USD'),
                rec.company_id,
                rec.date_approve or fields.Date.today()
            )

    @api.depends('amount_total')
    def _compute_amount_total_usd(self):
        for rec in self:
            rec.amount_total_usd = rec.currency_id._convert(
                rec.amount_total,
                self.env.ref('base.USD'),
                rec.company_id,
                rec.date_approve or fields.Date.today()
            )
