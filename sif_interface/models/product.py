# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2021, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # removing compute and inverse
    default_code = fields.Char(
        'Internal Reference',
        compute=None,
        inverse=None,
        )

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        default_value = False
        if 'maker_id' not in res or not res.get('maker_id'):
            default_value = self.env.ref('sif_interface.nd_res_partner').id
        if default_value:
            res['maker_id'] = default_value
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        default_value = False
        if 'maker_id' not in res or not res.get('maker_id'):
            default_value = self.env.ref('sif_interface.nd_res_partner').id
        if default_value:
            res['maker_id'] = default_value
        return res
