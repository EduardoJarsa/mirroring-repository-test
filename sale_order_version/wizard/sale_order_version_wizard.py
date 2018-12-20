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

    @api.multi
    def back_previous_version(self):
        self.ensure_one()
        self.sale_id.order_line.unlink()
        lines = self.sale_version_id.line_ids.read(
            load='without_name_get'
        )
        for line in lines:
            del line['create_date']
            del line['write_date']
            del line['create_uid']
            del line['write_uid']
            del line['sale_version_id']
        self.sale_id.order_line.create(lines)
        message = _("The <a href=# data-oe-model=sale.order.version"
                    " data-oe-id=%d>%s</a> version was selected to reset"
                    " the Sale Order") % (
                        self.sale_version_id.id, self.sale_version_id.name)
        self.sale_id.message_post(body=message)
