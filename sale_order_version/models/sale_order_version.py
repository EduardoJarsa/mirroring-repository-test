# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class SaleOrderVersion(models.Model):
    _name = 'sale.order.version'
    _inherit = 'sale.order'

    name = fields.Char(
        string='Version',
    )
    prefix = fields.Integer()
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string="Sale Order Version",
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name='sale.order.version.line',
        inverse_name='sale_version_id',
        string='Sale Version Lines',
    )


class SaleOrderVersionLine(models.Model):
    _name = 'sale.order.version.line'
    _inherit = 'sale.order.line'

    sale_version_id = fields.Many2one(
        comodel_name="sale.order.version",
        string="Sale Version",
    )
