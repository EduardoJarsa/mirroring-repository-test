# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import string

from odoo import api, fields, models
from odoo.tools.translate import _


class SaleOrderVersionCreateWizard(models.TransientModel):
    _name = 'sale.order.version.create.wizard'

    name = fields.Char()
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string="Sale Order",
    )
    json = fields.Char()
    boolean_switch = fields.Boolean(
        compute='_compute_same_prefix_boolean',
        help='This field helps to control the invisible'
        ' property of the field below "use_same_prefix".'
        ' If there is any line, the field will appear,'
        ' in other way, the field will remain hidden.',
    )
    use_same_prefix = fields.Boolean(
        string='Use same prefix?',
        help='If this field is checked, it allows you'
        ' to use the same prefix in different versions'
        ', in other way, the prefix will be increased to the'
        ' next letter of the alphabet.',
    )

    @api.multi
    @api.depends('use_same_prefix')
    def _compute_same_prefix_boolean(self):
        for rec in self:
            rec.boolean_switch = bool(rec.sale_id.order_version_ids)

    @api.multi
    def create_version(self):
        self.ensure_one()
        sov_obj = self.env['sale.order.version']
        alphabet = list(string.ascii_uppercase)
        alphabet.extend([i + b for i in alphabet for b in alphabet])
        index = sov_obj.search(
            [('sale_id', '=', self.sale_id.id)], order='id desc', limit=1)
        if not index:
            prefix = 0
        elif self.use_same_prefix and index:
            prefix = index.prefix
        else:
            prefix = (index.prefix) + 1
        version = sov_obj.create({
            'name': alphabet[prefix] + ' ' + self.name,
            'prefix': prefix,
            'line_ids': (
                [(0, 0, line) for line in self.sale_id.order_line.read(
                    load='without_name_get')]),
        })
        message = _("The <a href=# data-oe-model=sale.order.version"
                    " data-oe-id=%d>%s</a> version was created.") % (
                        version.id, version.name)
        self.sale_id.message_post(body=message)
