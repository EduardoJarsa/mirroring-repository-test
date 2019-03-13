# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import csv

from io import StringIO
from odoo import api, fields, models


class ImportSaleOrder(models.TransientModel):
    _name = 'import.sale.order.iho'
    _description = "import sale orders from CSV"

    upload_file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="File Name")

    @api.model
    def _prepare_sale_order_line(self, sale_order_line, sale_order):
        default_code = sale_order_line['CodigoProducto']
        if default_code == '':
            default_code = False
        if not default_code:
            product_id = self.env.ref('import_sale_order.product_product_dummy') 
        if not product_id:
            return False
        product_qty = float(sale_order_line['Cantidad'])
        if product_qty == '':
            product_qty = False
        price_unit = int(sale_order_line['PriceList'])
        if price_unit == '':
            price_unit = False
        factor = sale_order_line['Factor']
        if factor == '':
            factor = False
        discount = float(sale_order_line['CustomerDiscount'])
        if discount == '':
            discount = False
        iho_currency = sale_order_line['IHOCurrency']
        if iho_currency == '':
            iho_currency = False
        iho_discount = sale_order_line['IHODiscount']
        if iho_discount == '':
            iho_discount = False
        iho_currency_id = self.env['res.currency'].search(
            [('name', '=', iho_currency)])
        if iho_currency_id == '':
            iho_currency_id = False
        return {
            'name': product_id.name,
            'product_id': product_id.id,
            'product_uom_qty': product_qty,
            'price_unit': price_unit,
            'discount': discount,
            'factor': factor,
            'iho_currency_id': iho_currency_id.id,
            'iho_discount': iho_discount,
            'order_id': sale_order.id,
            'tax_id': [(6, 0, product_id.taxes_id.ids)],
        }

    @api.multi
    def import_sale_order_iho(self):
        self.ensure_one()
        data = base64.b64decode(self.upload_file).decode('utf-8')
        data = StringIO(data)
        reader = csv.DictReader(data)
        sale_order_id = self._context.get('active_id')
        sale_order = self.env['sale.order'].search(
            [('id', '=', sale_order_id)])
        sale_line_list = []
        for line in reader:
            order_line_element = self._prepare_sale_order_line(
                line, sale_order)
            if order_line_element:
                sale_line_list.append(order_line_element)
        self.env['sale.order.line'].create(
            sale_line_list)
