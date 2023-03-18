# Copyright 2019, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    maker_id = fields.Many2one("res.partner", related="product_tmpl_id.maker_id", readonly=False, string="Maker")
    catalog_id = fields.Many2one("iho.catalog", related="product_tmpl_id.catalog_id", readonly=False, string="Catalog")
    family_id = fields.Many2one("iho.family", related="product_tmpl_id.family_id", readonly=False, string="Family")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    maker_id = fields.Many2one("res.partner", string="Maker")
    catalog_id = fields.Many2one("iho.catalog", string="Catalog")
    family_id = fields.Many2one("iho.family", string="Family")
