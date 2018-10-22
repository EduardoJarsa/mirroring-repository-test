# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from odoo import _, api, fields, models

MAPPING = {
    'default_code': 'PN',
    'description': 'OD',
    'product_id.seller_ids': 'L'
}


class ExportSifWizard(models.TransientModel):
    _name = "export.sif.wizard"

    name = fields.Char()
    sif_binary = fields.Binary(string="Download File")
    state = fields.Selection(
        [('choose', 'Get'), ('download', 'Download')], default='choose')

    @api.multi
    def generate_file(self):
        self.ensure_one()
        lines = ['hola', 'como', 'estas']
        sif_data = ""
        if not lines:
            raise ValidationError(
                _("No results with requested information \n"
                  "Please check!"))
        for line in lines:
            sif_data += ('').join(line) + '\n\n'
        self.sif_binary = base64.b64encode(
            bytes(sif_data.encode('UTF-8')))
        self.write({
            'state': 'download',
            'name': 'test.sif',
            })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'export.sif.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
