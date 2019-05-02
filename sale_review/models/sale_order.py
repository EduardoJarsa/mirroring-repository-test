# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def call_wizard(self):
        return {
            'name': _("Select activity user"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'sale.order.review.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'sellers_sr_id': self._context.get('sellers_sr_id')}
        }

    @api.multi
    def send_quotation(self, name, email, rec_id):
        template = self.env.ref('sale_review.email_template_review_sale')
        return template.with_context(
            seller_sr_name=name,
            email=email).send_mail(rec_id)

    @api.multi
    def review_sale_order(self):
        for rec in self:
            users_senior_id = []
            for follower in rec.message_follower_ids.mapped('partner_id'):
                senior_group = self.env.ref(
                    'sales_team.group_sale_salesman_all_leads')
                if follower.user_ids in senior_group.users:
                    users_senior_id.append(follower.user_ids.id)
            if not users_senior_id:
                raise ValidationError(_(
                    'A seller sr has not been defined.'))
            if len(users_senior_id) > 1:
                return rec.with_context(
                    sellers_sr_id=users_senior_id).call_wizard()
            user_id = self.env['res.users'].search(
                [('id', '=', users_senior_id[0])])
            activity_data = {
                'res_id': rec.id,
                'activity_type_id':
                    self.env.ref(
                        'sale_review.activity_type_sale_review_quotations').id,
                'res_model_id': self.env.ref('sale.model_sale_order').id,
                'user_id': users_senior_id[0],
                'summary': _('Request to review quotation.'),
            }
            self.send_quotation(user_id.name, user_id.partner_id.email, rec.id)
            return self.env['mail.activity'].create(activity_data)
