# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    version_name = fields.Char()

    use_prefix = fields.Boolean()
    flag_first_time = fields.Integer()

    def call_wizard(self):
        return {
            "name": _("Select activity user"),
            "view_mode": "form",
            "res_model": "sale.order.review.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"sellers_sr_id": self._context.get("sellers_sr_id")},
        }

    def review_sale_order(self):
        for rec in self:
            if self.show_errors:
                raise ValidationError(_("Your quotation has errors, fix them first" " before asking for review"))
            senior_partner_ids = (
                self.env.ref("sales_team.group_sale_salesman_all_leads").users.mapped("partner_id").ids
            )
            users_senior_id = (
                rec.message_follower_ids.mapped("partner_id").filtered(lambda u: u.id in senior_partner_ids).ids
            )
            if not users_senior_id:
                users_senior_id = self.user_id.coach_id.user_id.partner_id.ids
                if users_senior_id:
                    self.message_subscribe(users_senior_id)
                    return rec.with_context(sellers_sr_id=users_senior_id).call_wizard()
                raise ValidationError(
                    _(
                        "A Sr Salesman has not been found.  "
                        " Be sure you have a Sr Salesman assigned at Employees"
                        " module and have him/her as your document follower"
                    )
                )
            if len(users_senior_id) > 0:
                return rec.with_context(sellers_sr_id=users_senior_id).call_wizard()
