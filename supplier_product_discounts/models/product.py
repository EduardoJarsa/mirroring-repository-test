# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    catalog_id = fields.Many2one('iho.catalog', string='Catalog')
    line_id = fields.Many2one('iho.line', string='Line')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    catalog_id = fields.Many2one('iho.catalog', string='Catalog')
    line_id = fields.Many2one('iho.line', string='Line')
