# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=C8108
# pylint: disable=C8110


from odoo import fields, models, api
from lxml import etree


class Partner(models.Model):
    _inherit = 'res.partner'

    street_number = fields.Char(
        'External', compute='_split_street',
        help="House Number",
        inverse='_set_street', store=True
        )
    street_number2 = fields.Char(
        'Internal', compute='_split_street',
        help="Door Number",
        inverse='_set_street', store=True)

    @api.model
    def _fields_view_get_address(self, arch):
        arch = super(Partner, self)._fields_view_get_address(arch)
        # render the partner address accordingly to address_view_id
        doc = etree.fromstring(arch)
        lang = self.env.user.lang
        if doc.xpath("//field[@name='city_id']"):
            if "es_" in lang:
                city_placeholder = (
                    '<field name="city" '
                    'placeholder="Ciudad"'
                    )
                city_placeholder_mod = (
                    '<field name="city" '
                    'placeholder=""'
                    )
                arch = arch.replace(
                    city_placeholder,
                    city_placeholder_mod
                )
                city_id_placeholder = (
                    '<field name="city_id" '
                    'placeholder="Ciudad"'
                )
                city_id_placeholder_mod = (
                    '<field name="city_id" '
                    'placeholder="Delegacion/Ciudad"'
                )
                arch = arch.replace(
                    city_id_placeholder,
                    city_id_placeholder_mod)
            return arch
