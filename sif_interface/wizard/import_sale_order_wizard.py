# Copyright 2020,2021 MtNet Services, S.A. de C.V.
# Copyright 2018,Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import csv
import os
from codecs import BOM_UTF8

from io import StringIO
from lxml import objectify
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

BOM_UTF8U = BOM_UTF8.decode('LATIN-1')


class ImportSaleOrderWizard(models.TransientModel):
    _name = "import.sale.order.wizard"
    _description = "Import sale order from a file."

    upload_file = fields.Binary(required=True)
    file_name = fields.Char()

    def run_import(self):
        file_extension = os.path.splitext(self.file_name)[1].lower()
        if file_extension not in ['.xml', '.csv']:
            raise ValidationError(
                _('Only .xml or .csv files allowed'))
        if file_extension == '.xml':
            self._run_2020_import()
        if file_extension == '.csv':
            self._run_csv_import()

    @api.model
    def to_float(self, line, column):
        """format a text to try to find a float in it."""
        text = line.get(column, '')
        t_no_space = text.replace(' ', '').replace('$', '').replace('€', '')
        char = ""
        for letter in t_no_space:
            if letter in ['.', ',']:
                char = letter
        if char == ",":
            t_no_space = t_no_space.replace(".", "")
            t_no_space = t_no_space.replace(",", ".")
        elif char == ".":
            t_no_space = t_no_space.replace(",", "")
        try:
            return float(t_no_space)
        except (AttributeError, ValueError):
            product = line.get('ProductCodeQuotLine', 'NA')
            if not product:
                product = 'NA'
            raise ValidationError(_(
                'There is no number or the format is incorrect for column %s '
                'of  product\n\nProduct:\n%s\n\nDescription:\n%s\n\nPlease '
                'validate the format of the whole column.\n\nRead value '
                'is: [%s]') % (column, product, line.get('Descrip', ''), text))

    @api.model
    def _check_value_extra_expense(self, extra_expense, index):
        if extra_expense:
            try:
                float(extra_expense)
            except ValueError:
                raise ValidationError(
                    _(
                        'column extra_expense wrong format '
                        '[%s] in line %s')
                    % (extra_expense, index))

    @api.model
    def _add_default_values(self, line, sale_order):
        default_values_cols = {
            'PurchCurrencyQuotLine': 'USD',
            'CustomerDiscountQuotLine': '0',
            'FactorQuotLine': '1',
            'ServiceFactorQuotLine': '1',
            'DealerDiscountQuotLine': '0',
            'ExchRateQuotLine': '1',
            'MakerQuotLine': '',
            'CatalogQuotLine': '',
            'FamilyQuotLine': '',
        }
        for column_default, value_default in default_values_cols.items():
            if not line.get(column_default):
                line[column_default] = value_default

    @api.model
    def _validate_service_factor(self, service_factor, product_id, index):
        if not service_factor:
            service_factor = 1
        if product_id.type in ('product', 'consu') and \
                (service_factor < 1 or service_factor > 1.99):
            raise ValidationError(
                _('Error CSV line [%s]: Column "Service factor" has '
                  'value of [%s] and must be [1-1.99]') %
                (index, service_factor))
        if product_id.type == 'service' and service_factor != 1:
            raise ValidationError(
                _('Error CSV line [%s]: Column "Service factor" in a '
                  'service line has value of [%s] and must be [1]') %
                (index, service_factor))

    @api.model
    def _prepare_sale_order_line(self, line, sale_order, index):
        if line.get('ProductCodeQuotLine', False) == '<empty>':
            return False
        self._add_default_values(line, sale_order)
        self._check_col_name(line)
        customer_discount = self.to_float(line, 'CustomerDiscountQuotLine')
        pricelist = self.to_float(line, 'PriceListQuotLine')
        iho_purchase_cost = pricelist * (100 - customer_discount) / 100
        supplier_reference = line.get('MakerQuotLine', False)
        # catalog_id
        catalog = line.get('CatalogQuotLine', False)
        catalog_id = False
        if catalog:
            catalog_id = self.env['iho.catalog'].search(
                [('name', '=', catalog)])
            if not catalog_id:
                new_catalog = {
                    'name': catalog,
                }
                catalog_id = self.env['iho.catalog'].create(new_catalog)
        # family_id
        family_id = False
        family = line.get('FamilyQuotLine', False)
        if family:
            family_id = self.env['iho.family'].search(
                [('name', '=', family)])
            if not family_id:
                new_family = {
                    'name': family,
                }
                family_id = self.env['iho.family'].create(new_family)
        # partner_id
        if supplier_reference:
            partner = self.env['res.partner'].search(
                [('ref', '=', supplier_reference), (
                    'supplier', '=', True)], limit=1)
        else:
            partner = self.env.ref('sif_interface.nd_res_partner')
        if not partner and supplier_reference:
            raise ValidationError(
                _('Error CSV line [%s]: Column "MakerQuotLine" There is not '
                  'a supplier with internal reference [%s] for product %s')
                % (index, supplier_reference, line['ProductDescripQuotLine'])
            )
        # default_code
        default_code = line.get('ProductCodeQuotLine', False)
        dummy_product = False
        if default_code:
            product_id = self.env['product.product'].search([(
                'default_code', '=', default_code)])
            if product_id:
                partner = product_id.maker_id
                catalog_id = product_id.catalog_id
                family_id = product_id.family_id
            if not product_id:
                dummy_product = self.env.ref(
                    'sif_interface.product_product_dummy')
                product_id = dummy_product
        else:
            dummy_product = self.env.ref('sif_interface.product_product_dummy')
            product_id = dummy_product
        # iho_currency
        iho_currency = line.get('PurchCurrencyQuotLine', False)
        if not iho_currency:
            iho_currency = 'USD'
        iho_currency_id = self.env['res.currency'].search(
            [('name', '=', iho_currency)])
        # service_factor
        service_factor = self.to_float(line, 'ServiceFactorQuotLine')
        self._validate_service_factor(service_factor, product_id, index)

        res = False
        if dummy_product:
            res = {
                'name': '[' + default_code + '] ' +
                        line['ProductDescripQuotLine']
            }
        else:
            res = {
                'name': line['ProductDescripQuotLine']
            }
        res.update({
            'product_id': product_id.id,
            'product_uom_qty': self.to_float(line, 'QttyQuotLine'),
            'iho_price_list': pricelist,
            'iho_purchase_cost': iho_purchase_cost,
            # 'iho_tc': self.to_float(line, 'ExchRateQuotLine'),
            'iho_service_factor': service_factor,
            'customer_discount': customer_discount,
            'iho_factor': self.to_float(line, 'FactorQuotLine'),
            'vendor_id': partner.id,
            'iho_currency_id': iho_currency_id.id,
            'dealer_discount': self.to_float(line, 'DealerDiscountQuotLine'),
            'order_id': sale_order.id,
            'analytic_tag_ids': [(6, 0, sale_order.analytic_tag_ids.ids)],
            'tax_id': [(6, 0, product_id.taxes_id.ids)],
        })
        if family_id:
            res.update({
                'family_id': family_id.id,
            })
        if catalog_id:
            res.update({
                'catalog_id': catalog_id.id,
            })
        return res

    def _check_col_name(self, line):
        file_cols = list(line.keys())
        required_cols = [
            'ProductCodeQuotLine',
            'ProductDescripQuotLine',
            'PurchCurrencyQuotLine',
            'QttyQuotLine',
            'PriceListQuotLine',
        ]
        cols_error = ''
        for rec in required_cols:
            if rec not in file_cols:
                cols_error = cols_error + rec + ','
        if cols_error:
            cols_error = cols_error[:-1]
            self._return_error_message(cols_error)

    @api.model
    def _return_error_message(self, cols_error):
        message = (
            _('Columns [%s] are not found in CSV file, '
                'please check for misspelling or extra spaces.')
            % cols_error)
        raise ValidationError(message)

    def _run_csv_import(self):
        self.ensure_one()
        data = base64.b64decode(self.upload_file).decode('latin-1')
        data = StringIO(data)
        reader = csv.DictReader(data)
        sale_order_id = self._context.get('active_id')
        sale_order = self.env['sale.order'].browse(sale_order_id)
        # sale_order lines importation
        sale_line_list = []
        index = 1
        for line in reader:
            # sale order header importation.   Header data is at CSV first row
            if index == 1:
                header_tc = line.get('ExchRateQuot', False)
                if header_tc:
                    sale_order.write({'iho_tc': header_tc, })
            index = index + 1
            element = self._prepare_sale_order_line(line, sale_order, index)
            if element:
                sale_line_list.append(element)
        lines = self.env['sale.order.line'].create(sale_line_list)
        # this line execute method than add fleet product
        # I do this because of a bug with create method
        sale_order = lines[0].order_id
        # TODO: Verify if we need to add _amount_untaxed_fleet_service function
        sale_order_lines = self.env['sale.order.line'].search(
            [('order_id', '=', sale_order.id)])
        last_index = len(sale_order_lines)
        fleet = sale_order_lines[last_index - 1].product_id
        sale_order_lines[last_index - 1].update(
            {
                'analytic_tag_ids': sale_order.analytic_tag_ids.ids,
                'tax_id': [(6, 0, fleet.taxes_id.ids)],
            }
        )

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
        xml_string = base64.b64decode(self.upload_file).lstrip(BOM_UTF8)
        try:
            xml = objectify.fromstring(xml_string)
            file_data = self.xml2dict(xml)
            self.env["ir.attachment"].create({
                'res_model': self._context.get('active_model'),
                'name': self.file_name,
                'res_id': self._context.get('active_id'),
                'type': 'binary',
                'datas': self.upload_file,
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
                    'customer_rank': 0,
                    'supplier_rank': 1,
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
                product_variant_id = self.env['product.product'].search(
                    [('product_tmpl_id', '=', item.id)])
                product_variant_id.write({
                    'default_code': item.default_code,
                })
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
                    'display_type': 'select',
                    'create_variant': 'always',
                })
        return item

    def _run_2020_import(self):
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

            # Alias
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

            # Catalog attribute:
            # catalog = self.search_data('Catalog', 'product.attribute')
            # cat_value = self.search_data(
            #     line['SpecItem']['Catalog']['Code'],
            #     'product.attribute.value', attr=catalog)
            # attributes.append(cat_value.id)

            # Generic attribute:
            # generic = self.search_data('Generic', 'product.attribute')
            # tags_data = {
            #     tag: value for tag, value in line.items() if tag.startswith(
            #         'Tag')}
            # generic_node = [
            #     value.get('Value')
            #     for tag, value in tags_data.items() if
            #     value.get('Type') == 'Generic']
            # generic_value = self.search_data(
            #     generic_node[0],
            #     'product.attribute.value', attr=generic)
            # attributes.append(generic_value.id)

            product = obj_prod_prod.search([
                ('default_code', '=', str(
                    line['SpecItem']['Alias']['Number'])),
                ('product_tmpl_id', '=', product_template.id)])
            if not product:
                try:
                    product = obj_prod_prod.create({
                        'name': str(line['SpecItem']['Description']),
                        'product_tmpl_id': product_template.id,
                        'product_template_attribute_value_ids': [(6, 0, attributes)],
                        'list_price': line['Price']['PublishedPrice'],
                        'route_ids': [(6, 0, routes)],
                        'code': str(line['SpecItem']['Alias']['Number']),
                        'default_code': str(
                            line['SpecItem']['Alias']['Number']),
                    })
                    # Remove the original product created when the
                    # product.template is created
                    obj_prod_prod.search([
                        ('product_tmpl_id', '=', product_template.id),
                        ('id', '!=', product.id),
                        ('product_variant_ids', '=', False)]).unlink()
                except Exception as exc:
                    raise ValidationError(str(exc) + _(
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
            customer_discount = (
                1 - (dealer_price_total[tag] / pub_price_total[tag])) * 100
            sale_order_line = sale_order.order_line.create({
                'product_id': product_bom.id,
                'product_uom_qty': 1.0,
                'name': product_bom.display_name,
                'order_id': sale_order.id,
                'iho_price_list': pub_price_total[tag],
                'discount': customer_discount,
                'product_uom': product_bom.uom_id.id,
                'customer_discount': customer_discount,
                'iho_currency_id': iho_currency_id.id,
                'analytic_tag_ids': [(6, 0, sale_order.analytic_tag_ids.ids)],
            })
            sale_order_line._compute_sell_1()
            sale_order_line._compute_sell_2()
            sale_order_line._compute_sell_3()
            sale_order_line._compute_sell_4()
        message = _(
            "The file %s was correctly loaded. ") % (self.file_name)
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
