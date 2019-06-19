# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import csv

from io import StringIO
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ImportSaleOrderLineIHO(models.TransientModel):
    _name = 'import.sale.order.line.iho'
    _description = "import sale orders from CSV"

    upload_file = fields.Binary()
    file_name = fields.Char()

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
            product = line.get('CodigoProducto', 'NA')
            if not product:
                product = 'NA'
            raise ValidationError(_(
                'There is no number or the format is incorrect for column %s '
                'of  product\n\nProduct:\n%s\n\nDescription:\n%s\n\nPlease '
                'validate the format of the whole column.\n\nThe readed value '
                'is: %s') % (column, product, line.get('Descrip', ''), text))

    @api.model
    def _prepare_sale_order_line(self, line, sale_order):
        supplier_reference = line.get('Fabricante', False)
        partner = self.env['res.partner'].search(
            [('ref', '=', supplier_reference), (
                'supplier', '=', True)], limit=1)
        if not partner:
            raise ValidationError(
                _(
                    'There is not a supplier with internal reference %s')
                % supplier_reference
            )
        default_code = line.get('CodigoProducto', False)
        if default_code:
            product_id = self.env['product.product'].search([(
                'default_code', '=', default_code)])
            if not product_id:
                product_id = self.env.ref(
                    'import_sale_order_line.product_product_dummy')
        else:
            product_id = self.env.ref(
                'import_sale_order_line.product_product_dummy')
        tc_agreed = self.to_float(line, 'TCAcordado')
        if not tc_agreed:
            tc_agreed = sale_order.currency_agreed_rate
        iho_currency = line.get('IHOCurrency', False)
        iho_currency_id = self.env['res.currency'].search(
            [('name', '=', iho_currency)])
        return {
            'name': line['Descrip'],
            'product_id': product_id.id,
            'product_uom_qty': self.to_float(line, 'Cantidad'),
            'iho_price_list': self.to_float(line, 'PriceList'),
            'iho_tc': tc_agreed,
            'iho_service_factor': self.to_float(line, 'FactorServicio'),
            'discount': self.to_float(line, 'CustomerDiscount'),
            'iho_factor': self.to_float(line, 'Factor'),
            'vendor_id': partner.id,
            'iho_currency_id': iho_currency_id.id,
            'iho_discount': self.to_float(line, 'IHODiscount'),
            'order_id': sale_order.id,
            'analytic_tag_ids': [(6, 0, sale_order.analytic_tag_ids.ids)],
            'tax_id': [(6, 0, product_id.taxes_id.ids)],
        }

    @api.multi
    def import_sale_order_line_iho(self):
        self.ensure_one()
        data = base64.b64decode(self.upload_file).decode('utf-8')
        data = StringIO(data)
        reader = csv.DictReader(data)
        sale_order_id = self._context.get('active_id')
        sale_order = self.env['sale.order'].browse(sale_order_id)
        sale_line_list = []
        for line in reader:
            element = self._prepare_sale_order_line(line, sale_order)
            if element:
                sale_line_list.append(element)
        lines = self.env['sale.order.line'].create(sale_line_list)
        # this line execute method than add fleet product
        # I do this because of a bug with create method
        sale_order = lines[0].order_id
        sale_order._amount_untaxed_fleet_service()
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
