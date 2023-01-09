# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    sale_authorized = fields.Integer(compute="_compute_sale_autorized", string="Number of Quotations")

    @api.depends("order_ids")
    def _compute_sale_autorized(self):
        for lead in self:
            nbr = 0
            for order in lead.order_ids:
                if order.state != "sale":
                    if order.authorized:
                        nbr += 1
            lead.sale_authorized = nbr

    @api.depends("order_ids")
    def _compute_sale_amount_total(self):
        for lead in self:
            total = 0.0
            nbr = 0
            company_currency = lead.company_currency or self.env.user.company_id.currency_id
            for order in lead.order_ids:
                if order.state not in ("reviewed", "approved", "sale"):
                    if not order.authorized:
                        nbr += 1
                if order.state not in ("draft", "sent", "cancel"):
                    total += order.currency_id._convert(
                        order.amount_untaxed,
                        company_currency,
                        order.company_id,
                        order.date_order or fields.Date.today(),
                    )
            lead.sale_amount_total = total
            lead.sale_number = nbr
