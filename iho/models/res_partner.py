# Copyright 2019, Jarsa
# Copyright 2021, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=method-compute
# pylint: disable=method-inverse


from lxml import etree

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    street_number = fields.Char(
        "External", compute="_split_street", help="House Number", inverse="_set_street", store=True
    )
    street_number2 = fields.Char(
        "Internal", compute="_split_street", help="Door Number", inverse="_set_street", store=True
    )
    property_purchase_currency_id = fields.Many2one(
        default=lambda self: self.env.ref("base.USD"),
    )

    @api.onchange("state_id")
    def _onchange_country_id(self):
        res = {"domain": {"city_id": []}}
        if self.state_id:
            res["domain"]["city_id"] = [("state_id", "in", [self.state_id.id, False])]
        return res

    @api.model
    def _fields_view_get_address(self, arch):
        arch = super()._fields_view_get_address(arch)
        # arch = super(Partner, self)._fields_view_get_address(arch)
        # render the partner address accordingly to address_view_id
        doc = etree.fromstring(arch)
        lang = self.env.user.lang
        if doc.xpath("//field[@name='city_id']"):
            if "es_" in lang:
                city_placeholder = (
                    '<field name="city" '
                    'placeholder="Ciudad" '
                    'class="o_address_city" '
                    'attrs="{                         '
                    "'invisible': [('country_enforce_cities', '=', True), "
                    "('city_id', '!=', False)],                         "
                    "'readonly': [('type', '=', 'contact')"
                    ", ('parent_id', '!=', False)]"
                    '                     }"/>\n                '
                    '<field name="city_id" placeholder="Ciudad" '
                    'string="Ciudad" class="o_address_city"'
                    ' context="{'
                    "'default_country_id': country_id,"
                    "                               "
                    "'default_name': city,"
                    "                               "
                    "'default_zipcode': zip,"
                    "                               "
                    "'default_state_id':"
                    ' state_id}" domain="[('
                    "'country_id', '=', country_id)]"
                    '" attrs="{                         '
                    "'invisible': [('country_enforce_cities', '=', False)],"
                    "                         'readonly':"
                    " [('type', '=', 'contact'),"
                    " ('parent_id', '!=', False)]                     }"
                    '"/>'
                )
                city_placeholder_mod = (
                    '<field name="city_id" placeholder="Delegacion/Ciudad" '
                    'string="Ciudad" class="o_address_city"'
                    ' context="{'
                    "'default_country_id': country_id,"
                    "                               "
                    "'default_name': city,"
                    "                               "
                    "'default_zipcode': zip,"
                    "                               "
                    "'default_state_id':"
                    ' state_id}" domain="[('
                    "'country_id', '=', country_id)]"
                    '" attrs="{                         '
                    "'invisible': [('country_enforce_cities', '=', False)],"
                    "                         'readonly':"
                    " [('type', '=', 'contact'),"
                    " ('parent_id', '!=', False)]                     }"
                    '"/>'
                    "\n                "
                    '<field name="city" '
                    'placeholder="" '
                    'class="o_address_city" '
                    'attrs="{                         '
                    "'invisible': [('country_enforce_cities', '=', True), "
                    "('city_id', '!=', False)],                         "
                    "'readonly': [('type', '=', 'contact')"
                    ", ('parent_id', '!=', False)]"
                    '                     }"/>'
                )
                arch = arch.replace(city_placeholder, city_placeholder_mod)
        return arch

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if not rec.property_product_pricelist:
                usd = self.env.ref("base.USD")
                usd_pl = self.env["product.pricelist"].search([("currency_id", "=", usd.id)], limit=1)
                if usd_pl:
                    rec.property_product_pricelist = usd_pl.id
        return res
