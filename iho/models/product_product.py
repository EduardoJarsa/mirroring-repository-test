# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        product_template = self.env[
            'product.template'].browse(vals[
                'product_tmpl_id'])
        res = super().create(vals)
        prod_variants = self.search(
            [
                ('product_tmpl_id', '=', vals['product_tmpl_id'])
            ])
        if len(prod_variants) == 1:
            res.default_code = product_template.default_code
        return res
