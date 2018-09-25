# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ImportBomWizard(models.TransientModel):
    _name = "import.bom.wizard"

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', readonly=True,
        help='Company to which it belongs this attachment',)
    xml_name = fields.Char(help='Save the file name, to verify that is .xml',)
    file_xml = fields.Binary(
        string='XML File',
        help='The xml file exported by the system', required=True,)

    @api.multi
    def run_bom_creation(self):
        file_extension = os.path.splitext(self.xml_name)[1].lower()
        if file_extension != '.xml':
            raise ValidationError(_('Verify that file is .xml, please!'))
        return True
