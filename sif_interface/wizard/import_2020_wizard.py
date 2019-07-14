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
    _description = "Export XML Files from 2020 to Sale Orders"

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
            self.env["ir.attachment"].create({
                'res_model': self._context.get('active_model'),
                'name': self.xml_name,
                'res_id': self._context.get('active_id'),
                'type': 'binary',
                'datas': self.file_xml,
                'datas_fname': self.xml_name,
            })
        except(SyntaxError, ValueError) as err:
            raise ValidationError(
                _('The XML file has an error, please check your data. \n '
                    'Error: %s') % (err))
        return file_data

    @api.model
    def get_data_info(self, xpath, data_node):
        return [data for node, data in data_node.items() if xpath in node]

    @api.model
    def search_data(self, value, model,
                    attr=False, name=False, buy=True, vendor=False,
                    dealer_price=False, currency=False, published_price=False):
        routes = [
            self.env.ref('stock.route_warehouse0_mto').id,
            self.env.ref('purchase_stock.route_warehouse0_buy').id]
        if model == 'res.partner':
            item = self.env[model].search([('ref', '=ilike', str(value))])
            if not item:
                item = self.env[model].create({
                    'name': str(value),
                    'company_type': 'company',
                    'customer': False,
                    'supplier': True,
                    'ref': str(value),
                })
        elif model == 'product.template':
            psi_obj = self.env['product.supplierinfo']
            item = self.env[model].search([
                ('default_code', '=', str(value))])
            if not item:
                sat_code = self.env['ir.default'].get(
                    model, 'l10n_mx_edi_code_sat_id')
                product_dict = {
                    'name': str(name),
                    'default_code': str(value),
                    'list_price': published_price,
                    'type': 'product',
                    'purchase_ok': buy,
                    'route_ids': [(6, 0, routes)],
                    'l10n_mx_edi_code_sat_id': sat_code or False,
                }
                if not dealer_price:
                    category_no_cost = self.env.ref(
                        'sif_interface.product_category_no_cost_materials'
                        )
                    product_dict['categ_id'] = category_no_cost.id
                item = self.env[model].create(product_dict)
            if vendor:
                sale_order_id = self._context.get('active_id')
                if not psi_obj.search(
                        [('product_tmpl_id', '=', item.id),
                         ('sale_order_id', '=', sale_order_id)]):
                    psi_obj.create({
                        'name': vendor.id,
                        'delay': 1,
                        'min_qty': 0,
                        'price': dealer_price,
                        'product_tmpl_id': item.id,
                        'sale_order_id': sale_order_id,
                        'currency_id': currency.id,
                    })
        elif model == 'product.attribute.value':
            item = self.env[model].search([
                ('name', '=', str(value)),
                ('attribute_id', '=', attr.id)])
            if not item:
                item = self.env[model].create({
                    'name': str(value),
                    'attribute_id': attr.id, })
        elif model == 'product.attribute':
            item = self.env[model].search([('name', '=', str(value))])
            if not item:
                item = self.env[model].create({
                    'name': str(value),
                    'type': 'select',
                    'create_variant': 'dynamic',
                })
        return item

    @api.multi
    def run_product_creation(self):
        self.ensure_one()
        obj_bom = self.env['mrp.bom']
        obj_prod_prod = self.env['product.product']
        bom_elements = {}
        cust_price_total = {}
        dealer_price_total = {}
        pub_price_total = {}
        sale_order = self.env[
            self._context.get('active_model')].browse(
                self._context.get('active_id'))
        routes = [
            self.env.ref('stock.route_warehouse0_mto').id,
            self.env.ref('purchase_stock.route_warehouse0_buy').id]
        file_extension = os.path.splitext(self.xml_name)[1].lower()
        if file_extension != '.xml':
            raise ValidationError(_('Verify that file is .xml, please!'))
        file_data = self.get_file_data()
        order_lines = self.get_data_info(
            'OrderLineItem', file_data['Envelope']['PurchaseOrder'])
        currency = file_data['Envelope']['Header']['Currency']
        iho_currency_id = self.env['res.currency'].search(
            [('name', '=', currency)])
        for line in order_lines:
            generic_value = ''
            vendor = self.search_data(
                line.get('VendorRef'), 'res.partner')
            product_template = self.search_data(
                line['SpecItem']['Number'], 'product.template',
                name=line['SpecItem']['Description'], vendor=vendor,
                dealer_price=line['Price']['OrderDealerPrice'],
                currency=iho_currency_id,
                published_price=line['Price']['PublishedPrice'])
            tags = self.get_data_info('Tag', line)
            tag_alias = [
                str(tag.get('Value')) + ' - ' + sale_order.name
                for tag in tags
                if 'Alias' in str(tag.get('Type'))
            ]
            if not tag_alias:
                name_product = (line['SpecItem']['Number'])
                raise ValidationError(
                    _('The %s product does '
                      'not have a configured Alias.'
                      '\nPlease verify the data of the xml.') % (name_product))
            attributes = self.get_attributes(
                self.get_data_info('Option', line['SpecItem']))
            catalog = self.search_data('Catalog', 'product.attribute')
            cat_value = self.search_data(
                line['SpecItem']['Catalog']['Code'],
                'product.attribute.value', attr=catalog)
            attributes.append(cat_value.id)
            generic = self.search_data('Generic', 'product.attribute')
            tags_data = {
                tag: value for tag, value in line.items() if tag.startswith(
                    'Tag')}
            generic_node = [
                value.get('Value')
                for tag, value in tags_data.items() if
                value.get('Type') == 'Generic']
            generic_value = self.search_data(
                generic_node[0],
                'product.attribute.value', attr=generic)
            attributes.append(generic_value.id)
            product = obj_prod_prod.search([
                ('default_code', '=', str(
                    line['SpecItem']['Alias']['Number'])),
                ('product_tmpl_id', '=', product_template.id)])
            if not product:
                try:
                    product = obj_prod_prod.create({
                        'name': str(line['SpecItem']['Description']),
                        'product_tmpl_id': product_template.id,
                        'attribute_value_ids': [(6, 0, attributes)],
                        'list_price': line['Price']['PublishedPrice'],
                        'route_ids': [(6, 0, routes)],
                        'code': str(line['SpecItem']['Alias']['Number']),
                        'default_code': str(
                            line['SpecItem']['Alias']['Number']),
                    })
                    # Remove the original product created when the
                    # product.template is created.
                    obj_prod_prod.search([
                        ('product_tmpl_id', '=', product_template.id),
                        ('id', '!=', product.id),
                        ('attribute_value_ids', '=', False)]).unlink()
                except Exception as exc:
                    raise ValidationError(exc.name + _(
                        '\n\n Product: [%s] - %s') % (
                        str(line['SpecItem']['Alias']['Number']),
                        str(line['SpecItem']['Description'])))
            bom_elements.setdefault(tag_alias[0], []).append((0, 0, {
                'product_id': product.id,
                'product_qty': line.get('Quantity'),
                'iho_purchase_cost': line['Price']['OrderDealerPrice'],
                'vendor_id': vendor.id,
                'iho_currency_id': iho_currency_id.id,
                'iho_customer_cost': line['Price']['EndCustomerPrice'],
            }))
            pub_price_total[tag_alias[0]] = pub_price_total.setdefault(
                tag_alias[0], 0.0) + (
                    line['Price']['PublishedPrice'] * line['Quantity'])
            cust_price_total[tag_alias[0]] = cust_price_total.setdefault(
                tag_alias[0], 0.0) + (
                    line['Price']['EndCustomerPrice'] * line['Quantity'])
            dealer_price_total[tag_alias[0]] = dealer_price_total.setdefault(
                tag_alias[0], 0.0) + (
                line['Price']['OrderDealerPrice'] * line['Quantity'])
        for tag, boms in bom_elements.items():
            product_template_bom = self.search_data(
                tag, 'product.template', name=tag, buy=False)
            if not obj_bom.search(
                    [('product_tmpl_id', '=', product_template_bom.id)]):
                obj_bom.create({
                    'type': 'phantom',
                    'bom_line_ids': boms,
                    'product_tmpl_id': product_template_bom.id,
                })
            product_bom = product_template_bom.product_variant_id
            customer_discount = (
                1 - (cust_price_total[tag] / pub_price_total[tag])) * 100
            iho_discount = (
                1 - (dealer_price_total[tag] / pub_price_total[tag])) * 100
            sale_order_line = sale_order.order_line.create({
                'product_id': product_bom.id,
                'product_uom_qty': 1.0,
                'name': product_bom.display_name,
                'order_id': sale_order.id,
                'iho_price_list': pub_price_total[tag],
                'discount': customer_discount,
                'product_uom': product_bom.uom_id.id,
                'iho_discount': iho_discount,
            })
            sale_order_line._compute_sell_1()
            sale_order_line._compute_sell_2()
            sale_order_line._compute_sell_3()
            sale_order_line._compute_sell_4()
        message = _(
            "The file %s was correctly loaded. ") % (self.xml_name)
        sale_order.message_post(body=message)
        pricelist = self.env['product.pricelist'].search(
            [('currency_id', '=', iho_currency_id.id)], limit=1)
        if pricelist and pricelist != sale_order.pricelist_id:
            sale_order.write({
                'pricelist_id': pricelist.id,
                'currency_id': pricelist.currency_id.id,
            })
        return file_data

    @api.model
    def get_attributes(self, line):
        attributes = []

        def option_recursive(option):
            data = str(option['Description']).split(":")
            code = str(option.get('Code'))
            attribute = code + "-" + data[0] if len(data) == 2 else code
            value = data[1] if len(data) == 2 else data[0]
            attr = self.search_data(attribute, 'product.attribute')
            attr_value = self.search_data(
                value, 'product.attribute.value', attr=attr)
            attributes.append(attr_value.id)
            if option.get('Option'):
                option_recursive(option.get('Option'))
            return True

        for item in line:
            option_recursive(item)

        return attributes
