# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _


class SaleOrderVersionWizard(models.TransientModel):
    _name = 'sale.order.version.wizard'

    sale_version_id = fields.Many2one(
        comodel_name='sale.order.version',
        string="Sale Order Version",
        required=True,
    )
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string="Sale Order",
    )

    @api.model
    def default_get(self, res_fields):
        res = super().default_get(res_fields)
        res['sale_id'] = self._context.get('active_id', False)
        return res

    @api.multi
    def back_previous_version(self):
        self.ensure_one()
        self.sale_id.order_line.unlink()
        lines = self.sale_version_id.line_ids.read(
            load='without_name_get'
        )
        order = self.sale_version_id.read(
            load='without_name_get'
        )
        # Delete useless fields of lines
        for line in lines:
            del line['create_date']
            del line['write_date']
            del line['create_uid']
            del line['write_uid']
            del line['sale_version_id']
            del line['id']
            # Apply format to analytic_tag_ids because is a M2M field
            # and need it to get the desire value from sale order version line
            line['analytic_tag_ids'] = [(6, 0, line['analytic_tag_ids'])]
        # Delete useless fields from sale order version
        del order[0]['order_version_ids']
        del order[0]['order_line']
        del order[0]['message_follower_ids']
        del order[0]['message_ids']
        del order[0]['name']
        del order[0]['line_ids']
        del order[0]['prefix']
        del order[0]['sale_id']
        del order[0]['id']
        # Apply format to analytic_tag_ids and tag_ids fields because they are
        # M2M fields and need it to get the desire value sale_order_version
        order[0]['analytic_tag_ids'] = [(6, 0, order[0]['analytic_tag_ids'])]
        order[0]['tag_ids'] = [(6, 0, order[0]['tag_ids'])]
        self.sale_id.write(order[0])
        self.sale_id.order_line.create(lines)
        message = _("The <a href=# data-oe-model=sale.order.version"
                    " data-oe-id=%d>%s</a> version was selected to reset"
                    " the Sale Order") % (
                        self.sale_version_id.id, self.sale_version_id.name)
        self.sale_id.message_post(body=message)
