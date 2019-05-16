# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _


class SaleOrderReviewWizard(models.TransientModel):
    _name = 'sale.order.review.wizard'

    seller_ids = fields.Many2one(
        'res.partner', string='Seller senior')

    @api.onchange('seller_ids')
    def _onchange_seller_id(self):
        res_partner_obj = self.env['res.partner'].browse(
            tuple(self._context['sellers_sr_id']))
        res = {'domain': {'seller_ids': []}}
        res['domain']['seller_ids'] = [
            ('user_ids.id', 'in', res_partner_obj.ids)]
        return res

    @api.multi
    def request_review_so(self):
        so_obj = self.env['sale.order']
        so = so_obj.browse(self._context.get('active_id'))
        activity_data = {
            'res_id': so.id,
            'activity_type_id': self.env.ref(
                'sale_review.activity_type_sale_review_quotations').id,
            'res_model_id': self.env.ref('sale.model_sale_order').id,
            'user_id': self.seller_ids.user_ids.id,
            'summary': _('Request to review quotation.'),
            'note': _(
                'Dear %s Please enter to the quote %s, for review '
                'in it case create the new quotation, it will send '
                'to the customer %s. If you have questions,'
                ' can include in the same document.') % (
                self.seller_ids.user_ids.name, so.name, so.partner_id.name)
        }
        return self.env['mail.activity'].create(activity_data)
