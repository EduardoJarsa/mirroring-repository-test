# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    has_sdl = fields.Boolean(compute="_compute_has_sdl")
    hide_post_button = fields.Boolean(compute="_compute_hide_post_button")

    def action_view_landed_costs(self):
        self.ensure_one()
        action = self.env.ref('stock_landed_costs.action_stock_landed_cost').read()[0]
        sdl_model = self.env['stock.landed.cost']
        sdl = self.env['stock.landed.cost'].search(
            [('vendors_bill_ids', 'in', [self.id])])
        sdl_model |= sdl
        sdl_model |= self.landed_costs_ids
        domain = [('id', 'in', sdl_model.ids)]
        context = dict(self.env.context, default_vendor_bill_id=self.id)

        views = [
            (self.env.ref('stock_landed_costs.view_stock_landed_cost_tree2').id, 'tree'),
            (False, 'form'), (False, 'kanban')]
        return dict(action, domain=domain, context=context, views=views)

    def _compute_has_sdl(self):
        for rec in self:
            has_sdl = False
            sdl = self.env['stock.landed.cost'].search(
                [('vendors_bill_ids', 'in', [self.id])])
            if sdl:
                has_sdl = True
            rec.has_sdl = has_sdl

    def button_create_landed_costs(self):
        res = super().button_create_landed_costs()
        sdl = self.env['stock.landed.cost'].browse(res['res_id'])
        sdl.write({
            'vendors_bill_ids': [self.id],
        })
        return res

    def _compute_hide_post_button(self):
        for rec in self:
            hide_post = not \
                self.user_has_groups('iho.group_view_account_move_post')
            rec.hide_post_button = hide_post

    def action_post(self):
        for rec in self:
            cust_invoice = \
                rec.type in ['out_invoice', 'out_refund', 'out_receipt']
            cust_country_mx = False
            if cust_invoice:
                cust_country_mx = (
                    rec.partner_id.country_id
                    if not rec.partner_id.parent_id
                    else rec.partner_id.parent_id.country_id
                ) == self.env.ref("base.mx")
            if cust_invoice and cust_country_mx:
                cust_rfc = (
                    rec.partner_id.vat
                    if not rec.partner_id.parent_id
                    else rec.partner_id.parent_id.vat
                )
                if not cust_rfc:
                    raise ValidationError(_(
                        'Can not POST an invoice without Mexican RFC defined'))
            return super().action_post()
