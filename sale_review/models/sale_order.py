# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    review_so = fields.Boolean(string='Review SO')

    @api.multi
    def review_sale_order(self):
        self.ensure_one()
        current_uid = self._context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        if self.review_so:
            self.sudo().review_so = False
            message = _('<strong>%s</strong> canceled review'
                        ' <strong>%s %s</strong>.') % (
                user.name, self.name, self.active_version_id.name,)
        else:
            self.sudo().review_so = True
            message = _('The <strong>%s</strong>'
                        ' was reviewed by <strong>%s</strong>.') % (
                self.name, user.name, )
            if self.active_version_id:
                message = _('The <strong>%s %s</strong> '
                            'was reviewed by <strong>%s</strong>.') % (
                    self.name, self.active_version_id.name, user.name,)
        return self.message_post(body=message)
