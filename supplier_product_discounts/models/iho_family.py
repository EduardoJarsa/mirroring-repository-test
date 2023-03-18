# Copyright 2019, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class IhoFamily(models.Model):
    _name = "iho.family"
    _description = "iho catalog of product families"

    name = fields.Char(required=True)
