# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os

from codecs import BOM_UTF8
from lxml import objectify
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

BOM_UTF8U = BOM_UTF8.decode('UTF-8')


class ImportBomWizard(models.TransientModel):
    _name = "import.bom.wizard"

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', readonly=True,
        help='Company to which it belongs this attachment',)
    xml_name = fields.Char(help='Save the file name, to verify that is .xml',)
    file_xml = fields.Binary(
        string='XML File',
        help='The xml file exported by the system', required=True,)

    @api.model
    def xml2dict(self, xml):
        """Receive 1 lxml etree object and return a dict string.
        This method allow us have a precise diff output

            :return: method to iterate the xml recursively
            :rtype: dict
        """
        def recursive_dict(element):
            """ Local method that iterates recursively element
            by element the xml to convert it in a dictionary with
            format { 'xml_tag': children_tags or element value }

                :return: self-method to iterate the children tags
                :rtype: self-method
            """
            return (element.tag.split('}')[1],
                    dict(map(recursive_dict, element.getchildren()),
                         **element.attrib))
        return dict([recursive_dict(xml)])

    @api.model
    def get_file_data(self):
        """Method used to translate the raw xml to a clean dictionary

           :return: A clean dictionary with the xml data
           :rtype: dict
        """
        xml_string = base64.b64decode(self.file_xml).lstrip(BOM_UTF8)
        try:
            xml = objectify.fromstring(xml_string)
            file_data = self.xml2dict(xml)
        except(SyntaxError, ValueError) as err:
            raise ValidationError(
                _('The XML file has an error, please check your data. \n '
                    'Error: %s') % (err))
        return file_data

    @api.multi
    def run_bom_creation(self):
        self.ensure_one()
        file_extension = os.path.splitext(self.xml_name)[1].lower()
        if file_extension != '.xml':
            raise ValidationError(_('Verify that file is .xml, please!'))
        file_data = self.get_file_data()
        return file_data
