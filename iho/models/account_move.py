# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        if self._l10n_mx_edi_is_advance():
            self.update({
                'invoice_payment_term_id': self.env.ref(
                    'account.account_payment_term_immediate'),
                'l10n_mx_edi_origin': False,
            })
