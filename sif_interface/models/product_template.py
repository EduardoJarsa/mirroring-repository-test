# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    """We need to override the original field from Odoo because is a
    compute field and the behavior do not satisfy the requiriments
    of this module"""
    default_code = fields.Char(
        'Internal Reference',
        compute=None,
        inverse=None,)
