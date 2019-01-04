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

    @api.model
    def default_get(self, res_fields):
        res = super().default_get(res_fields)
        res['sale_id'] = self._context.get('active_id', False)
        return res

    @api.model
    def _prepare_sov_lines(self, lines):
        res = []
        line_fields = ["product_id", "name", "iho_price_list", "iho_discount",
                       "iho_sell_1", "iho_factor", "iho_sell_2", "iho_sell_3",
                       "product_uom_qty", "qty_delivered", "qty_invoiced",
                       "analytic_tag_ids", "route_id", "price_unit", "tax_id",
                       "price_subtotal", "order_id"]
        for line in lines:
            data = line.read(line_fields, 'without_name_get')[0]
            data['sale_line_id'] = line.id
            res.append((0, 0, data))
        return res

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
        name = alphabet[prefix]
        if self.name:
            name = alphabet[prefix] + ' ' + self.name
        version = sov_obj.create({
            'name': name,
            'partner_id': self.sale_id.partner_id.id,
            'validity_date': self.sale_id.validity_date,
            'payment_term_id': self.sale_id.payment_term_id.id,
            'picking_policy': self.sale_id.picking_policy,
            'user_id': self.sale_id.user_id.id,
            'team_id': self.sale_id.team_id.id,
            'currency_agreed_rate': self.sale_id.currency_agreed_rate,
            'warehouse_id': self.sale_id.warehouse_id.id,
            'pricelist_id': self.sale_id.pricelist_id.id,
            'incoterm': self.sale_id.incoterm,
            'expected_date': self.sale_id.expected_date,
            'commitment_date': self.sale_id.commitment_date,
            'date_order': self.sale_id.date_order,
            'origin': self.sale_id.origin,
            'client_order_ref': self.sale_id.client_order_ref,
            'analytic_account_id': self.sale_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.sale_id.analytic_tag_ids.ids)],
            'tag_ids': [(6, 0, self.sale_id.tag_ids.ids)],
            'route_id': self.sale_id.route_id.id,
            'fiscal_position_id': self.sale_id.fiscal_position_id.id,
            'prefix': prefix,
            'line_ids': self._prepare_sov_lines(self.sale_id.order_line),
            'sale_id': self.sale_id.id,
        })
        message = _("The <a href=# data-oe-model=sale.order.version"
                    " data-oe-id=%d>%s</a> version was created.") % (
                        version.id, version.name)
        self.sale_id.message_post(body=message)
