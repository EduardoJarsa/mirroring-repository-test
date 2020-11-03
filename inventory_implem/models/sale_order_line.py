# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        warning_mess = super(SaleOrderLine, self)._onchange_product_id_check_availability()
        # import ipdb;  ipdb.set_trace()
        is_not_dummy_product = self.product_id != \
            self.env.ref('sif_interface.product_product_dummy')
        if is_not_dummy_product and warning_mess:
            raise ValidationError(
                _(warning_mess['warning']['title']) + "\n\n" +
                _(warning_mess['warning']['message']))
        # return warning_mess
