# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval


class SaleTerm(models.Model):
    _name = "sale.term"
    _description = "Sale Terms and Conditions"
    _order = "sequence asc"
    _rec_name = "code"

    name = fields.Text(
        required=True,
        translate=True,
        help="Python code field using 'order' as model",
    )
    sequence = fields.Integer(required=True, default=10)
    default = fields.Boolean()
    order_id = fields.Many2one("sale.order")
    name_validation = fields.Html(readonly=True)
    invalid_term_ids = fields.Many2many(
        comodel_name="sale.term",
        relation="invalid_sale_term_rel",
        column1="col1",
        column2="col2",
        string="Invalid Combination",
    )
    category_id = fields.Many2one("sale.term.category", required=True)
    code = fields.Char(
        required=True,
    )

    _sql_constraints = [
        ("sequence_uniq", "unique(code,category_id)", _("The code and category must be unique !")),
    ]

    def name_get(self):
        result = []
        for rec in self:
            name = "[%s] %s" % (rec.category_id.name, rec.code)
            result.append((rec.id, name))
        return result

    @api.onchange("name", "order_id")
    def _onchange_name_order_id(self):
        if self.order_id and self.name:
            self.name_validation = safe_eval(
                self.name,
                {
                    "order": self.order_id,
                },
            )
