# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleTerm(models.Model):
    _name = 'sale.term'
    _description = 'Catalog of Sale Terms'
    _order = 'sequence asc'
    _rec_name = 'code'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(required=True, default=10)
    default = fields.Boolean()
    invalid_term_ids = fields.Many2many(
        comodel_name='sale.term',
        relation='invalid_sale_term_rel',
        column1='col1',
        column2='col2',
        string='Invalid Combination')
    category_id = fields.Many2one('sale.term.category', required=True)
    code = fields.Char(required=True,)

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = '[%s] %s' % (rec.category_id.name, rec.code)
            result.append((rec.id, name))
        return result
