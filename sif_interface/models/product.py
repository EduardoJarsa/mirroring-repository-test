# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2021, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # removing compute and inverse
    default_code = fields.Char(
        'Internal Reference',
        compute=None,
        inverse=None,
        )

    def _get_default_maker_id(self):
        default_value = self.env.ref('sif_interface.nd_res_partner')
        return default_value
    maker_id = fields.Many2one(
        default=_get_default_maker_id
        )


class ProductProduct(models.Model):
    _inherit = "product.product"

    # adding default value
    def _get_default_maker_id(self):
        default_value = self.env.ref('sif_interface.nd_res_partner')
        return default_value
    maker_id = fields.Many2one(
        default=_get_default_maker_id
        )
