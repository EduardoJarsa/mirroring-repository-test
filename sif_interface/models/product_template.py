# Copyright 2021, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends("product_variant_ids", "product_variant_ids.default_code")
    def _compute_default_code(self):
        return True
