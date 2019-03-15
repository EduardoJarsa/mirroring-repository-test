# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import csv

from io import StringIO
from odoo import api, fields, models


class ImportSaleOrderLineIHO(models.TransientModel):
    _name = 'import.sale.order.line.iho'
    _description = "import sale orders from CSV"

    upload_file = fields.Binary()
    file_name = fields.Char()

    @api.model
    def _prepare_sale_order_line(self, sale_order_line, sale_order):
        default_code = sale_order_line.get('CodigoProducto', False)
        description = sale_order_line['Descrip']
        if default_code:
            product_id = self.env['product.product'].search([(
                'default_code', '=', default_code)])
            if not product_id:
                product_id = self.env.ref(
                    'import_sale_order_line.product_product_dummy')
        else:
            product_id = self.env.ref(
                    'import_sale_order_line.product_product_dummy')
        product_qty = sale_order_line.get('Cantidad', False)
        price_unit = sale_order_line.get('PriceList', False)
        factor = sale_order_line.get('Factor', False)
        discount = sale_order_line['CustomerDiscount']
        if discount:
            discount = float(discount)
        iho_currency = sale_order_line.get('IHOCurrency', False)
        iho_discount = sale_order_line['IHODiscount']
        iho_currency_id = self.env['res.currency'].search(
            [('name', '=', iho_currency)])
        return {
            'name': description,
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
    def import_sale_order_line_iho(self):
        self.ensure_one()
        data = base64.b64decode(self.upload_file).decode('utf-8')
        data = StringIO(data)
        reader = csv.DictReader(data)
        sale_order_id = self._context.get('active_id')
        sale_order = self.env['sale.order'].browse(
            [(sale_order_id)])
        sale_line_list = []
        for line in reader:
            order_line_element = self._prepare_sale_order_line(
                line, sale_order)
            if order_line_element:
                sale_line_list.append(order_line_element)
        self.env['sale.order.line'].create(
            sale_line_list)
