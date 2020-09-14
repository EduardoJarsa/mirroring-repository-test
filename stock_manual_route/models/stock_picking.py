# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.addons.stock.models.product import OPERATORS
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = 'id asc'

    no_route = fields.Boolean(
        compute='_compute_no_route',
        search='_search_no_route',
        help='Field used to identify pickings without destination moves.'
    )

    def _compute_no_route(self):
        for rec in self:
            rec.no_route = (
                all(not move.move_dest_ids for move in rec.move_lines) and
                rec.state not in ['draft', 'cancel'])

    def _search_no_route(self, operator, value):
        if operator not in OPERATORS:
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, bool):
            raise UserError(_('Invalid domain right operand %s') % value)

        ids = []
        for move in self.search([]):
            if OPERATORS[operator](move.no_route, value):
                ids.append(move.id)
        return [('id', 'in', ids)]
