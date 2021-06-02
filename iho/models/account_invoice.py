# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    has_sdl = fields.Boolean(compute="_compute_has_sdl")

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
