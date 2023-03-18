# Copyright 2020,2021 MtNet Services, S.A. de C.V.
# Copyright 2018,Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import csv
import logging
import os
from codecs import BOM_UTF8
from io import StringIO

from lxml import objectify
from xlrd import open_workbook

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# pylint: disable=too-many-nested-blocks
# pylint: disable=W7938
# pylint: disable=old-deprecated-method
# pylint: disable=too-complex
# pylint: disable=consider-iterating-dictionary


BOM_UTF8U = BOM_UTF8.decode("LATIN-1")
_logger = logging.getLogger(__name__)


class ImportSaleOrderWizard(models.TransientModel):
    _name = "import.sale.order.wizard"
    _description = "Import sale order from a file."

    @api.model
    def _default_tax_sale(self):
        tax = False
        tax = self.env.company.account_sale_tax_id
        return tax

    upload_file = fields.Binary(required=True)
    file_name = fields.Char()
    product_category_id = fields.Many2one(
        "product.category",
    )
    taxes_id = fields.Many2many(
        "account.tax",
        default=lambda self: self._default_tax_sale(),
    )

    def run_import(self):
        file_extension = os.path.splitext(self.file_name)[1].lower()
        if file_extension not in [".xml", ".csv", ".xls", ".xlsx"]:
            raise ValidationError(_("Only .xml or .csv files allowed"))
        if file_extension == ".xml":
            self._run_2020_import()
        if file_extension == ".csv":
            self._run_csv_import()
        if file_extension in (".xlsx", ".xls"):
            self._run_2020_import_xls()

    @api.model
    def to_float(self, line, column):
        """format a text to try to find a float in it."""
        text = line.get(column, "")
        t_no_space = text.replace(" ", "").replace("$", "").replace("€", "")
        char = ""
        for letter in t_no_space:
            if letter in [".", ","]:
                char = letter
        if char == ",":
            t_no_space = t_no_space.replace(".", "")
            t_no_space = t_no_space.replace(",", ".")
        elif char == ".":
            t_no_space = t_no_space.replace(",", "")
        try:
            return float(t_no_space)
        except (AttributeError, ValueError):
            product = line.get("ProductCodeQuotLine", "NA")
            if not product:
                product = "NA"
            raise ValidationError(
                _(
                    "There is no number or the format is incorrect for column %s "
                    "of  product\n\nProduct:\n%s\n\nDescription:\n%s\n\nPlease "
                    "validate the format of the whole column.\n\nRead value "
                    "is: [%s]"
                )
                % (column, product, line.get("Descrip", ""), text)
            )

    @api.model
    def _check_value_extra_expense(self, extra_expense, index):
        if extra_expense:
            try:
                float(extra_expense)
            except ValueError:
                raise ValidationError(_("column extra_expense wrong format [%s] in line %s") % (extra_expense, index))

    @api.model
    def _add_default_values(self, line, sale_order):
        default_values_cols = {
            "PurchCurrencyQuotLine": "USD",
            "CustomerDiscountQuotLine": "0",
            "FactorQuotLine": "1",
            "ServiceFactorQuotLine": "1",
            "DealerDiscountQuotLine": "0",
            "ExchRateQuotLine": "1",
            "MakerQuotLine": "",
            "CatalogQuotLine": "",
            "FamilyQuotLine": "",
        }
        for column_default, value_default in default_values_cols.items():
            if not line.get(column_default):
                line[column_default] = value_default

    @api.model
    def _validate_service_factor(self, service_factor, product_id, index):
        if not service_factor:
            service_factor = 1
        if product_id.type in ("product", "consu") and (service_factor < 1 or service_factor > 1.99):
            raise ValidationError(
                _("Error CSV line [%s]: Column 'Service factor' has value of [%s] and must be [1-1.99]")
                % (index, service_factor)
            )
        if product_id.type == "service" and service_factor != 1:
            raise ValidationError(
                _(
                    'Error CSV line [%s]: Column "Service factor" in a '
                    "service line has value of [%s] and must be [1]"
                )
                % (index, service_factor)
            )

    @api.model
    def _get_line_tax(self, line):
        line_tax_str = line.get("TaxQuotLine", False)
        line_tax_id = False
        if line_tax_str:
            # tax_line_str from CSV has to be '16', '8', 0, ...
            # account.tax name has to be 'IVA(16', 'IVA(8'
            line_tax_id = (
                self.env["account.tax"]
                .search([("type_tax_use", "=", "sale"), ("name", "=ilike", "IVA(%s" % line_tax_str + "%")], limit=1)
                .id
            )
        return line_tax_id

    @api.model
    def _prepare_sale_order_line(self, line, sale_order, index):
        if line.get("ProductCodeQuotLine", False) == "<empty>":
            return False
        self._add_default_values(line, sale_order)
        self._check_col_name(line)
        customer_discount = self.to_float(line, "CustomerDiscountQuotLine")
        pricelist = self.to_float(line, "PriceListQuotLine")
        iho_purchase_cost = pricelist * (100 - customer_discount) / 100
        supplier_reference = line.get("MakerQuotLine", False)
        line_tax_id = self._get_line_tax(line)
        # catalog_id
        catalog = line.get("CatalogQuotLine", False)
        catalog_id = False
        if catalog:
            catalog_id = self.env["iho.catalog"].search([("name", "=", catalog)])
            if not catalog_id:
                new_catalog = {
                    "name": catalog,
                }
                catalog_id = self.env["iho.catalog"].create(new_catalog)
        # family_id
        family_id = False
        family = line.get("FamilyQuotLine", False)
        if family:
            family_id = self.env["iho.family"].search([("name", "=", family)])
            if not family_id:
                new_family = {
                    "name": family,
                }
                family_id = self.env["iho.family"].create(new_family)
        # partner_id
        if supplier_reference:
            partner = self.env["res.partner"].search(
                [("ref", "=", supplier_reference), ("supplier", "=", True)], limit=1
            )
        else:
            partner = self.env.ref("sif_interface.nd_res_partner")
        if not partner and supplier_reference:
            raise ValidationError(
                _(
                    'Error CSV line [%s]: Column "MakerQuotLine" There is not '
                    "a supplier with internal reference [%s] for product %s"
                )
                % (index, supplier_reference, line["ProductDescripQuotLine"])
            )
        # default_code
        default_code = line.get("ProductCodeQuotLine", False)
        dummy_product = False
        if default_code:
            product_id = self.env["product.product"].search([("default_code", "=", default_code)])
            if product_id:
                partner = product_id.maker_id
                catalog_id = product_id.catalog_id
                family_id = product_id.family_id
            if not product_id:
                dummy_product = self.env.ref("sif_interface.product_product_dummy")
                product_id = dummy_product
        else:
            dummy_product = self.env.ref("sif_interface.product_product_dummy")
            product_id = dummy_product
        # iho_currency
        iho_currency = line.get("PurchCurrencyQuotLine", False)
        if not iho_currency:
            iho_currency = "USD"
        iho_currency_id = self.env["res.currency"].search([("name", "=", iho_currency)])
        # service_factor
        service_factor = self.to_float(line, "ServiceFactorQuotLine")
        self._validate_service_factor(service_factor, product_id, index)

        res = False
        if dummy_product:
            res = {"name": "[" + default_code + "] " + line["ProductDescripQuotLine"]}
        else:
            res = {"name": line["ProductDescripQuotLine"]}
        res.update(
            {
                "product_id": product_id.id,
                "product_uom_qty": self.to_float(line, "QttyQuotLine"),
                "iho_price_list": pricelist,
                "iho_purchase_cost": iho_purchase_cost,
                # 'iho_tc': self.to_float(line, 'ExchRateQuotLine'),
                "iho_service_factor": service_factor,
                "customer_discount": customer_discount,
                "iho_factor": self.to_float(line, "FactorQuotLine"),
                "vendor_id": partner.id,
                "iho_currency_id": iho_currency_id.id,
                "dealer_discount": self.to_float(line, "DealerDiscountQuotLine"),
                "order_id": sale_order.id,
                "analytic_tag_ids": [(6, 0, sale_order.analytic_tag_ids.ids)],
                "tax_id": [(6, 0, [line_tax_id] if line_tax_id else product_id.taxes_id.ids)],
            }
        )
        if family_id:
            res.update(
                {
                    "family_id": family_id.id,
                }
            )
        if catalog_id:
            res.update(
                {
                    "catalog_id": catalog_id.id,
                }
            )
        return res

    def _check_col_name(self, line):
        file_cols = list(line.keys())
        required_cols = [
            "ProductCodeQuotLine",
            "ProductDescripQuotLine",
            "PurchCurrencyQuotLine",
            "QttyQuotLine",
            "PriceListQuotLine",
        ]
        cols_error = ""
        for rec in required_cols:
            if rec not in file_cols:
                cols_error = cols_error + rec + ","
        if cols_error:
            cols_error = cols_error[:-1]
            self._return_error_message(cols_error)

    @api.model
    def _return_error_message(self, cols_error):
        message = (
            _("Columns [%s] are not found in CSV file, please check for misspelling or extra spaces.") % cols_error
        )
        raise ValidationError(message)

    def _run_csv_import(self):
        self.ensure_one()
        data = base64.b64decode(self.upload_file).decode("latin-1")
        data = StringIO(data)
        reader = csv.DictReader(data)
        sale_order_id = self._context.get("active_id")
        sale_order = self.env["sale.order"].browse(sale_order_id)
        # sale_order lines importation
        sale_line_list = []
        index = 1
        for line in reader:
            # sale order header importation.   Header data is at CSV first row
            if index == 1:
                header_tc = line.get("ExchRateQuot", False)
                if header_tc:
                    sale_order.write(
                        {
                            "iho_tc": header_tc,
                        }
                    )
            index = index + 1
            element = self._prepare_sale_order_line(line, sale_order, index)
            if element:
                sale_line_list.append(element)
        lines = self.env["sale.order.line"].create(sale_line_list)
        sale_order = lines[0].order_id

    @api.model
    def xml2dict(self, xml):
        """Receive 1 lxml etree object and return a dict string.
        This method allow us have a precise diff output

            :return: method to iterate the xml recursively
            :rtype: dict
        """

        def recursive_dict(xml_object):
            """Local method that iterates recursively element
            by element the xml to convert it in a dictionary with
            format { 'xml_tag': children_tags or element value }

                :return: self-method to iterate the children tags
                :rtype: self-method
            """
            count = 1
            dict_object = {}
            if xml_object.getchildren():
                for children in xml_object.getchildren():
                    tag = children.tag.split("}")[1]
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

        return {xml.tag.split("}")[1]: recursive_dict(xml)}

    def _get_currency_row_value(self, row_values):
        currency = False
        for rec in row_values:
            if not currency and rec != "":
                currency = self.env["res.currency"].search([("name", "=", rec)])
        if not currency:
            raise ValidationError(_("Currency not found"))
        return currency

    @api.model
    def get_file_data_xlsx(self):
        """Method used to translate the raw xml to a clean dictionary

        :return: A clean dictionary with the xml data
        :rtype: dict
        """
        try:
            book = open_workbook(file_contents=base64.decodestring(self.upload_file))
        except FileNotFoundError:
            raise ValidationError(_("No such file or directory found. \n%s.") % self.file_name)
        save = False
        for sheet in book.sheets():
            try:
                line_vals = []
                header_index = {}
                index = 0
                currency = False
                currency_row = False
                for row in range(sheet.nrows):
                    index += 1
                    current_header = str(sheet.row_values(row)[0]).lower()
                    if current_header == "sold to":
                        currency_row = index + 4
                    if currency_row and currency_row == index:
                        currency = self._get_currency_row_value(sheet.row_values(row))
                    if current_header == "item":
                        save = True
                        header_index["item"] = 0
                        header_index["qty"] = 1
                        header_index["part_number"] = 2
                        header_index["part_description"] = 3
                        header_index["clave_desc"] = 4
                        header_index["vendor"] = 5
                        header_index["price_list"] = 6
                        header_index["price_list_ext"] = 7
                        header_index["product_name"] = 9
                        header_index["row"] = 10
                        continue
                    if save:
                        qty = sheet.row_values(row)[1]
                        if qty != "":
                            current_line = sheet.row_values(row)
                            current_line.append(row + 1)
                            line_vals.append(current_line)
            except IndexError:
                _logger.warning("IndexError: %s", sheet.name)
        return line_vals, header_index, currency

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
            self.env["ir.attachment"].create(
                {
                    "res_model": self._context.get("active_model"),
                    "name": self.file_name,
                    "res_id": self._context.get("active_id"),
                    "type": "binary",
                    "datas": self.upload_file,
                }
            )
        except (SyntaxError, ValueError) as err:
            raise ValidationError(_("The XML file has an error, please check your data. \n Error: %s") % (err))
        return file_data

    @api.model
    def get_data_info(self, xpath, data_node):
        return [data for node, data in data_node.items() if xpath in node]

    @api.model
    def search_data(
        self,
        value,
        model,
        attr=False,
        name=False,
        buy=True,
        vendor=False,
        dealer_price=False,
        currency=False,
        published_price=False,
        product_template=False,
        product_brand=False,
    ):
        routes = [
            self.env.ref("stock.route_warehouse0_mto").id,
            self.env.ref("purchase_stock.route_warehouse0_buy").id,
        ]
        if model == "res.partner":
            item = self.env[model].search([("ref", "=ilike", str(value))])
            if not item:
                item = self.env[model].create(
                    {
                        "name": str(value),
                        "company_type": "company",
                        "customer_rank": 0,
                        "supplier_rank": 1,
                        "ref": str(value),
                        "property_purchase_currency_id": currency.id,
                    }
                )
        elif model == "product.template":
            psi_obj = self.env["product.supplierinfo"]
            item = self.env[model].search([("default_code", "=", str(value))])
            if not item:
                sat_code = self.env["ir.default"].get(model, "l10n_mx_edi_code_sat_id")
                product_dict = {
                    "name": str(name),
                    "default_code": str(value),
                    "list_price": published_price,
                    "type": "product",
                    "purchase_ok": buy,
                    "l10n_mx_edi_code_sat_id": sat_code or False,
                    "categ_id": self.product_category_id.id,
                    "taxes_id": self.taxes_id.ids,
                }
                if product_brand:
                    product_dict.update(
                        {
                            "product_brand_id": product_brand.id,
                        }
                    )
                if not dealer_price:
                    category_no_cost = self.env.ref("sif_interface.product_category_no_cost_materials")
                    product_dict["categ_id"] = category_no_cost.id
                item = self.env[model].create(product_dict)
                item.write(
                    {
                        "route_ids": [(6, 0, routes)],
                    }
                )
                product_variant_id = self.env["product.product"].search([("product_tmpl_id", "=", item.id)])
                product_variant_id.write(
                    {
                        "default_code": item.default_code,
                    }
                )
            if vendor:
                sale_order_id = self._context.get("active_id")
                if not psi_obj.search([("product_tmpl_id", "=", item.id), ("sale_order_id", "=", sale_order_id)]):
                    psi_obj.create(
                        {
                            "name": vendor.id,
                            "delay": 1,
                            "min_qty": 0,
                            "price": dealer_price,
                            "product_tmpl_id": item.id,
                            "sale_order_id": sale_order_id,
                            "currency_id": currency.id,
                        }
                    )
        elif model == "product.attribute.value":
            item = self.env[model].search([("name", "=", str(value)), ("attribute_id", "=", attr.id)])
            if not item:
                item = self.env[model].create(
                    {
                        "name": str(value),
                        "attribute_id": attr.id,
                    }
                )
        elif model == "product.attribute":
            item = self.env[model].search([("name", "=", str(value))])
            if not item:
                item = self.env[model].create(
                    {
                        "name": str(value),
                        "display_type": "select",
                        "create_variant": "always",
                    }
                )
        return item

    def _prepare_item(self, attr, value):
        def process_item(element, value):
            return (
                0,
                0,
                {
                    "attribute_id": attr.id,
                    "value_ids": [(6, 0, [value.id])],
                },
            )

        items = []
        items_ids = []
        item = process_item(attr, value)
        items_ids.append(attr.id)
        if item:
            items.append(item)
        return items, items_ids

    def _generate_default_code_variant(self, default_code, variant):
        code = ""
        attribute_values = variant.product_template_attribute_value_ids
        attr_list = []
        for rec in attribute_values.mapped("name"):
            attr_list.append(rec)
        full_code = code.join(attr_list)
        full_code = default_code + " " + full_code
        return full_code

    def _run_2020_import_xls(self):
        self.ensure_one()
        sale_order = self.env[self._context.get("active_model")].browse(self._context.get("active_id"))
        routes = [
            self.env.ref("stock.route_warehouse0_mto").id,
            self.env.ref("purchase_stock.route_warehouse0_buy").id,
        ]
        order_lines, header_index, currency = self.get_file_data_xlsx()
        product_template = False
        is_other_prod = False
        error = False
        list_error = []
        for line in order_lines:
            line_quantity = line[header_index["qty"]]
            iho_currency_id = currency.id
            vendor_code = line[header_index["vendor"]]
            clave_desc = line[header_index["clave_desc"]]
            row = line[header_index["row"]]
            if " " in clave_desc:
                error = True
                list_error.append(row)
            if error:
                continue
            vendor = self.env["res.partner"].search([("ref", "=ilike", str(vendor_code))])
            if not vendor:
                raise ValidationError(_("Vendor code %s not found") % vendor_code)
            product_brand = False
            brand_model = self.env["product.brand"]
            product_brands = brand_model.search([("partner_id", "=", vendor.id)])
            if product_brands:
                product_brand = product_brands[0]
            else:
                product_brand = brand_model.create(
                    {
                        "name": vendor.name,
                        "partner_id": vendor.id,
                    }
                )
            # Detect if is other product to separate the attributes value.
            if product_template and product_template.default_code != line[header_index["part_number"]]:
                is_other_prod = True
            _logger.info("%s", is_other_prod)
            product_template = self.search_data(
                line[header_index["part_number"]],
                "product.template",
                name=line[header_index["product_name"]],
                vendor=vendor,
                currency=currency,
                product_brand=product_brand,
            )
            attributes_value = False
            attr, attributes_value = self.get_attributes_xlsx(line, header_index)
            # order alphabetically
            order_attributes = sorted(attributes_value)
            code_value = self._generate_attribute_value(order_attributes)
            # Remove last char
            code_value = code_value[:-1]
            full_description = line[header_index["part_description"]]
            attr_value = False
            attr_value = self.search_data(
                code_value, "product.attribute.value", attr=attr[0], product_template=product_template
            )
            try:
                attribute_lines, attributes_ids = self._prepare_item(attr[0], attr_value)
                _logger.info("%s", attributes_ids)
                routes = product_template.route_ids
                default_code = product_template.default_code
                if not product_template.attribute_line_ids:
                    product_template.write(
                        {
                            "attribute_line_ids": attribute_lines,
                        }
                    )
                else:
                    # Filter to create new variants
                    lines_attributes = product_template.attribute_line_ids
                    product_attribute_values = lines_attributes.product_template_value_ids
                    names = product_attribute_values.filtered(lambda l: l.name == attr_value.name)
                    if not names:
                        product_template.attribute_line_ids[0].write(
                            {
                                "value_ids": [(4, attr_value.id)],
                            }
                        )

                for variant in product_template.product_variant_ids:
                    full_code = self._generate_default_code_variant(default_code, variant)
                    if variant.default_code != full_code:
                        product_name = line[header_index["product_name"]]
                        part_description = line[header_index["part_description"]]
                        variant.write(
                            {
                                "name": product_name + ", " + part_description,
                                "default_code": full_code,
                                "route_ids": [(6, 0, routes.ids)],
                                "full_description": default_code + " " + full_description,
                                "categ_id": self.product_category_id.id,
                                "taxes_id": self.taxes_id.ids,
                                "maker_id": vendor,
                                "product_brand_id": product_template.product_brand_id.id,
                            }
                        )
                        if len(product_template.product_variant_ids) == 1:
                            variant.variant_seller_ids.write(
                                {
                                    "product_id": variant,
                                }
                            )
                        else:
                            seller = variant.variant_seller_ids.filtered(
                                lambda l: l.sale_order_id == sale_order and l.product_id == variant
                            )
                            if not seller:
                                psi_obj = self.env["product.supplierinfo"]
                                psi_obj.create(
                                    {
                                        "name": vendor.id,
                                        "delay": 1,
                                        "min_qty": 0,
                                        "price": 1.0,
                                        "product_tmpl_id": product_template.id,
                                        "sale_order_id": sale_order.id,
                                        "currency_id": iho_currency_id,
                                        "product_id": variant.id,
                                    }
                                )
                if not product_template.default_code:
                    product_template.write(
                        {
                            "default_code": default_code,
                        }
                    )
            except Exception as exc:
                error_def_code = str(line["SpecItem"]["Alias"]["Number"])
                error_prod_descp = str(line["SpecItem"]["Description"])
                raise ValidationError(str(exc) + _("\n\n Product: [%s] - %s") % (error_def_code, error_prod_descp))

            current_code_variant = default_code + " " + code_value
            product_variant = product_template.product_variant_ids.filtered(
                lambda l: l.default_code == current_code_variant
            )
            iho_price_list = float(line[header_index["price_list"]])
            if product_variant.display_name:
                sale_order_line = sale_order.order_line.create(
                    {
                        "product_id": product_variant.id,
                        "product_uom_qty": line_quantity,
                        "order_id": sale_order.id,
                        "iho_price_list": iho_price_list,
                        "discount": 0,
                        "product_uom": product_variant.uom_id.id,
                        "customer_discount": 0,
                        "iho_currency_id": iho_currency_id,
                        "analytic_tag_ids": [(6, 0, sale_order.analytic_tag_ids.ids)],
                        "iho_tc": 1.0,
                    }
                )
                sale_order_line.write(
                    {
                        "iho_service_factor": 1.0,
                    }
                )
                sale_order_line._compute_sell_1()
                sale_order_line._compute_sell_2()
                sale_order_line._compute_sell_3()
                sale_order_line._compute_sell_4()
                self._change_varriant_seller(product_variant, vendor, sale_order_line.price_unit)
        if error:
            raise ValidationError(_("There is white space in attribute values in the next lines %s") % list_error)
        message = _("The file %s was correctly loaded. ") % (self.file_name)
        sale_order.message_post(body=message)
        pricelist = self.env["product.pricelist"].search([("currency_id", "=", iho_currency_id)], limit=1)
        if pricelist and pricelist != sale_order.pricelist_id:
            sale_order.write(
                {
                    "pricelist_id": pricelist.id,
                    "currency_id": pricelist.currency_id.id,
                }
            )

    def _run_2020_import(self):
        self.ensure_one()
        cust_price_total = {}
        dealer_price_total = {}
        pub_price_total = {}
        sale_order = self.env[self._context.get("active_model")].browse(self._context.get("active_id"))
        routes = [
            self.env.ref("stock.route_warehouse0_mto").id,
            self.env.ref("purchase_stock.route_warehouse0_buy").id,
        ]
        file_data = self.get_file_data()
        order_lines = self.get_data_info("OrderLineItem", file_data["Envelope"]["PurchaseOrder"])
        currency = file_data["Envelope"]["Header"]["Currency"]
        iho_currency_id = self.env["res.currency"].search([("name", "=", currency)])
        product_template = False
        is_other_prod = False
        for line in order_lines:
            vendor = self.search_data(line.get("VendorRef"), "res.partner", currency=sale_order.currency_id)
            product_brands = self.env["product.brand"].search([("partner_id", "=", vendor.id)])
            product_brand = False
            if product_brands:
                product_brand = product_brands[0]
            # Detect if is other product to separate the attributes value.
            if product_template and product_template.default_code != line["SpecItem"]["Number"]:
                is_other_prod = True
            _logger.info("%s", is_other_prod)
            product_template = self.search_data(
                line["SpecItem"]["Number"],
                "product.template",
                name=line["SpecItem"]["Description"],
                vendor=vendor,
                dealer_price=line["Price"]["OrderDealerPrice"],
                currency=iho_currency_id,
                published_price=line["Price"]["PublishedPrice"],
                product_brand=product_brand,
            )
            # Alias
            tags = self.get_data_info("Tag", line)
            tag_alias = [
                str(tag.get("Value")) + " - " + sale_order.name for tag in tags if "Alias" in str(tag.get("Type"))
            ]
            if not tag_alias:
                tag_alias = [" "]

            attributes_value = False
            attr, attributes_value, attributes_description = self.get_attributes(
                self.get_data_info(
                    "Option",
                    line["SpecItem"],
                ),
                product_template=product_template,
            )

            if not attr:
                pub_price_total[tag_alias[0]] = pub_price_total.setdefault(tag_alias[0], 0.0) + (
                    line["Price"]["PublishedPrice"] * line["Quantity"]
                )
                cust_price_total[tag_alias[0]] = cust_price_total.setdefault(tag_alias[0], 0.0) + (
                    line["Price"]["EndCustomerPrice"] * line["Quantity"]
                )
                dealer_price_total[tag_alias[0]] = dealer_price_total.setdefault(tag_alias[0], 0.0) + (
                    line["Price"]["OrderDealerPrice"] * line["Quantity"]
                )
                customer_discount = (1 - (dealer_price_total[tag_alias[0]] / pub_price_total[tag_alias[0]])) * 100
                iho_price_list = line["Price"]["PublishedPrice"]

                sale_order_line = sale_order.order_line.create(
                    {
                        "product_id": int(product_template.product_variant_ids),
                        "product_uom_qty": int(line["Quantity"]),
                        "name": "[" + str(line["SpecItem"]["Number"]) + "]" + str(line["SpecItem"]["Description"]),
                        "order_id": int(sale_order.id),
                        "iho_price_list": float(iho_price_list),
                        "discount": float(0.0),
                        "product_uom": int(product_template.product_variant_ids.uom_id.id),
                        "customer_discount": float(customer_discount),
                        "iho_currency_id": int(iho_currency_id.id),
                        "analytic_tag_ids": [(6, 0, sale_order.analytic_tag_ids.ids)],
                        "product_packaging": 0,
                        "display_type": 0,
                    }
                )
                sale_order_line.write(
                    {
                        "iho_service_factor": 1.0,
                    }
                )
                sale_order_line._compute_sell_1()
                sale_order_line._compute_sell_2()
                sale_order_line._compute_sell_3()
                sale_order_line._compute_sell_4()
                if product_template.maker_id.name == "N/D":
                    product_template.write(
                        {
                            "maker_id": vendor,
                        }
                    )

            if attr:
                code_value = self._generate_attribute_value(attributes_value)
                full_description = self._generate_full_description(attributes_description)
                # Remove last char
                code_value = code_value[:-1]
                full_description = full_description[:-2]
                attr_value = False
                attr_value = self.search_data(
                    code_value, "product.attribute.value", attr=attr[0], product_template=product_template
                )
                try:
                    attribute_lines, attributes_ids = self._prepare_item(attr[0], attr_value)
                    _logger.info("%s", attributes_ids)
                    routes = product_template.route_ids
                    default_code = product_template.default_code
                    if not product_template.attribute_line_ids:
                        product_template.write(
                            {
                                "attribute_line_ids": attribute_lines,
                            }
                        )
                    else:
                        # Filter to create new variants
                        lines_attributes = product_template.attribute_line_ids
                        product_attribute_values = lines_attributes.product_template_value_ids
                        names = product_attribute_values.filtered(lambda l: l.name == attr_value.name)
                        if not names:
                            product_template.attribute_line_ids[0].write(
                                {
                                    "value_ids": [(4, attr_value.id)],
                                }
                            )

                    for variant in product_template.product_variant_ids:
                        full_code = self._generate_default_code_variant(default_code, variant)
                        if variant.default_code != full_code:
                            variant.write(
                                {
                                    "default_code": full_code,
                                    "route_ids": [(6, 0, routes.ids)],
                                    "full_description": default_code + " " + full_description,
                                    "categ_id": self.product_category_id.id,
                                    "taxes_id": self.taxes_id.ids,
                                    "maker_id": vendor,
                                    "product_brand_id": product_template.product_brand_id.id,
                                }
                            )
                            if len(product_template.product_variant_ids) == 1:
                                variant.variant_seller_ids.write(
                                    {
                                        "product_id": variant,
                                    }
                                )
                            else:
                                seller = variant.variant_seller_ids.filtered(
                                    lambda l: l.sale_order_id == sale_order and l.product_id == variant
                                )
                                if not seller:
                                    psi_obj = self.env["product.supplierinfo"]
                                    currency_id = self.env.ref("base." + currency).id
                                    psi_obj.create(
                                        {
                                            "name": vendor.id,
                                            "delay": 1,
                                            "min_qty": 0,
                                            "price": 1.0,
                                            "product_tmpl_id": product_template.id,
                                            "sale_order_id": sale_order.id,
                                            "currency_id": currency_id,
                                            "product_id": variant.id,
                                        }
                                    )
                    if not product_template.default_code:
                        product_template.write(
                            {
                                "default_code": default_code,
                            }
                        )
                except Exception as exc:
                    error_def_code = str(line["SpecItem"]["Alias"]["Number"])
                    error_prod_descp = str(line["SpecItem"]["Description"])
                    raise ValidationError(str(exc) + _("\n\n Product: [%s] - %s") % (error_def_code, error_prod_descp))
                current_code_variant = default_code + " " + code_value
                product_variant = product_template.product_variant_ids.filtered(
                    lambda l: l.default_code == current_code_variant
                )
                pub_price_total[tag_alias[0]] = pub_price_total.setdefault(tag_alias[0], 0.0) + (
                    line["Price"]["PublishedPrice"] * line["Quantity"]
                )
                cust_price_total[tag_alias[0]] = cust_price_total.setdefault(tag_alias[0], 0.0) + (
                    line["Price"]["EndCustomerPrice"] * line["Quantity"]
                )
                dealer_price_total[tag_alias[0]] = dealer_price_total.setdefault(tag_alias[0], 0.0) + (
                    line["Price"]["OrderDealerPrice"] * line["Quantity"]
                )
                customer_discount = (1 - (dealer_price_total[tag_alias[0]] / pub_price_total[tag_alias[0]])) * 100
                iho_price_list = line["Price"]["PublishedPrice"]

                sale_order_line = sale_order.order_line.create(
                    {
                        "product_id": product_variant.id,
                        "product_uom_qty": line["Quantity"],
                        "name": product_variant.display_name,
                        "order_id": sale_order.id,
                        "iho_price_list": iho_price_list,
                        "discount": 0.0,
                        "product_uom": product_variant.uom_id.id,
                        "customer_discount": customer_discount,
                        "iho_currency_id": iho_currency_id.id,
                        "analytic_tag_ids": [(6, 0, sale_order.analytic_tag_ids.ids)],
                    }
                )
                sale_order_line.write(
                    {
                        "iho_service_factor": 1.0,
                    }
                )
                sale_order_line._compute_sell_1()
                sale_order_line._compute_sell_2()
                sale_order_line._compute_sell_3()
                sale_order_line._compute_sell_4()

                self._change_varriant_seller(product_variant, vendor, sale_order_line.price_unit)

        message = _("The file %s was correctly loaded. ") % (self.file_name)
        sale_order.message_post(body=message)
        pricelist = self.env["product.pricelist"].search([("currency_id", "=", iho_currency_id.id)], limit=1)
        if pricelist and pricelist != sale_order.pricelist_id:
            sale_order.write(
                {
                    "pricelist_id": pricelist.id,
                    "currency_id": pricelist.currency_id.id,
                }
            )
        return file_data

    def _generate_full_description(self, attributes_description):
        code_value = ""
        for rec in attributes_description:
            code_value += rec + "/ "
        return code_value

    def _generate_attribute_value(self, attributes_value):
        code_value = ""
        for rec in attributes_value:
            code_value += rec + "-"
        return code_value

    def _change_varriant_seller(self, product_variant, vendor, price_unit):
        if vendor:
            sale_order_id = self._context.get("active_id")
            variant_seller = product_variant.variant_seller_ids.filtered(lambda l: l.sale_order_id.id == sale_order_id)
            if variant_seller:
                variant_seller.write(
                    {
                        "price": price_unit,
                    }
                )

    @api.model
    def get_attributes(self, line, product_template=False):
        attributes = []
        attributes_value = []
        attributes_description = []

        def option_recursive(option):
            data = str(option["Description"]).split(":")
            code = str(option.get("Code"))
            attribute = code + "-" + data[0] if len(data) == 2 else code
            value = data[1] if len(data) == 2 else data[0]
            _logger.info("%s", value)
            _logger.info("%s", attribute)
            generic_attribute = "Specs"
            attr = self.search_data(generic_attribute, "product.attribute")
            if attr not in attributes:
                attributes.append(attr)
            attributes_value.append(code)
            attributes_description.append(data[0])
            if option.get("Option"):
                option_recursive(option.get("Option"))
            return True

        for item in line:
            option_recursive(item)
        return attributes, attributes_value, attributes_description

    @api.model
    def get_attributes_xlsx(self, line, header_index, product_template=False):
        attributes = []
        attributes_value = []
        generic_attribute = "Specs"
        base_code = line[header_index["clave_desc"]].replace("\n", " ")
        # Remove last char
        last_char = base_code[-1]
        if last_char == ",":
            base_code = base_code[:-1]
        code = base_code.split(" ")
        attr = self.search_data(generic_attribute, "product.attribute")
        if attr not in attributes:
            attributes.append(attr)
        for rec in code:
            if rec != "":
                attributes_value.append(rec)
        return attributes, attributes_value
