# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os

from codecs import BOM_UTF8
from lxml import objectify
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

BOM_UTF8U = BOM_UTF8.decode('UTF-8')


class Import2020Wizard(models.TransientModel):
    _name = "import.2020.wizard"

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', readonly=True,
        help='Company to which it belongs this attachment',)
    xml_name = fields.Char(help='Save the file name, to verify that is .xml',)
    file_xml = fields.Binary(
        string='XML File',
        help='The xml file exported by the system', required=True,)

    @api.model
    def validate_data(self, dict_value):
        if 'Vendor' in dict_value:
            return True
        else:
            return False

    @api.model
    def xml2dict(self, xml):
        """Receive 1 lxml etree object and return a dict string.
        This method allow us have a precise diff output

            :return: method to iterate the xml recursively
            :rtype: dict
        """
        def recursive_dict(xml_object):
            """ Local method that iterates recursively element
            by element the xml to convert it in a dictionary with
            format { 'xml_tag': children_tags or element value }

                :return: self-method to iterate the children tags
                :rtype: self-method
            """
            count = 1
            dict_object = {}
            if xml_object.getchildren():
                for children in xml_object.getchildren():
                    tag = children.tag.split('}')[1]
                    if tag in dict_object.keys():
                        dict_object[tag + str(count)] = children
                        count += 1
                    else:
                        dict_object[tag] = children
            else:
                dict_object = xml_object.__dict__
            if not dict_object:
                return xml_object
            for key, value in dict_object.items():
                dict_object[key] = recursive_dict(value)
            return dict_object
        return {xml.tag.split('}')[1]: recursive_dict(xml)}

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

    @api.model
    def get_data_info(self, xpath, data_node):
        return [data for node, data in data_node.items() if xpath in node]

    @api.model
    def search_data(self, value, model, attr=False):
        item = self.env[model].search([('name', '=', str(value))])
        if not item:
            if model == 'product.attribute.value':
                item = self.env[model].create({
                    'name': str(value),
                    'attribute_id': attr.id})
                return item
            item = self.env[model].create({'name': str(value)})
        return item

    @api.multi
    def run_product_creation(self):
        self.ensure_one()
        obj_prod_prod = self.env['product.product']
        file_extension = os.path.splitext(self.xml_name)[1].lower()
        if file_extension != '.xml':
            raise ValidationError(_('Verify that file is .xml, please!'))
        file_data = self.get_file_data()
        vendors = self.get_data_info('Vendor', file_data['Envelope']['Header'])
        order_lines = self.get_data_info(
            'OrderLineItem', file_data['Envelope']['PurchaseOrder'])
        for vendor in vendors:
            partner = self.search_data(vendor.get('Code'), 'res.partner')
        for line in order_lines:
            product_template = self.search_data(
                line['SpecItem']['Number'], 'product.template')
            attributes = self.get_attributes(
                self.get_data_info('Option', line['SpecItem']))
            product = obj_prod_prod.search([
                ('name', '=', str(line['SpecItem']['Alias']['Number'])),
                ('product_tmpl_id', '=', product_template.id)])
            if not product or product.attribute_value_ids.ids == attributes:
                obj_prod_prod.create({
                    'name': str(line['SpecItem']['Alias']['Number']),
                    'product_tmpl_id': product_template.id,
                    'attribute_value_ids': [(6, 0, attributes)],
                    'list_price': line['Price']['PublishedPrice'],
                })

        return file_data

    @api.model
    def get_attributes(self, line):
        attributes = []

        def option_recursive(option):
            data = str(option['Description']).split(":")
            attr = self.search_data(data[0], 'product.attribute')
            value = self.search_data(data[1], 'product.attribute.value', attr)
            attributes.append(value.id)
            if option.get('Option'):
                option_recursive(option.get('Option'))
            return True

        for item in line:
            option_recursive(item)

        return attributes
