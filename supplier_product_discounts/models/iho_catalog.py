# Copyright 2019, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class IhoCatalog(models.Model):
    _name = "iho.catalog"
    _description = "iho catalog of models"

    name = fields.Char(required=True)
