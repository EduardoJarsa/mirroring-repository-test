# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_version_ids = fields.One2many("sale.order.version", "sale_id", "Sale Order Versions", copy=False)
    has_lines = fields.Boolean(compute="_compute_has_lines")
    active_version_name = fields.Char(related="active_version_id.name")
    active_version_id = fields.Many2one("sale.order.version", string="Active Version", readonly=True)
    active_version_modified = fields.Boolean(
        string="Different from Active Version",
        readonly=True,
        help="This field helps to identify if a sales order was modified and " "is different from the active version.",
    )
    origin_sale_order_id = fields.Many2one(
        "sale.order", related="active_version_id.sale_id", string="Source Quotation"
    )

    @api.depends("order_line")
    def _compute_has_lines(self):
        for rec in self:
            rec.has_lines = bool(rec.order_line)

    def write(self, vals):
        for rec in self:
            if rec.active_version_id:
                if vals.get("active_version_modified", True):
                    vals["active_version_modified"] = True
        return super().write(vals)
