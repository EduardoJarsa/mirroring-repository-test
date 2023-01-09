# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleTermCategory(models.Model):
    _name = "sale.term.category"
    _description = "Categories of Sale Terms"
    _order = "sequence asc"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(required=True, default=10)
