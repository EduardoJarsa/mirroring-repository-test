# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from odoo import api, fields, models


class ExportSifWizard(models.TransientModel):
    _name = "export.sif.wizard"
    _description = "Export SIF Files from Purchase Order(s)"

    name = fields.Char()
    sif_binary = fields.Binary(string="Download File")
    state = fields.Selection(
        [('choose', 'Get'), ('download', 'Download')], default='choose')

    @api.model
    def _prepare_lines_items(self, line, sif_data):
        bom_product_tmpl_id = line.sale_line_id.product_id.product_tmpl_id
        bom_line = self.env['mrp.bom.line'].search(
            [('product_id', '=', line.product_id.id),
             ('parent_product_tmpl_id', '=', bom_product_tmpl_id.id)],
            limit=1)
        customer_price = bom_line.iho_customer_cost
        product_price = line.product_id.list_price or 1
        dealer_price = line.product_id.seller_ids.with_context(
            order=line.sale_line_id.order_id).filtered(
            lambda r: r.sale_order_id == r._context.get('order')).price
        sif_data += 'PN=' + (
            line.product_id.
            product_tmpl_id.default_code) + '\n'  # Product Code
        sif_data += 'PD=' + line.product_id.name + '\n'  # Product Name
        sif_data += 'TG=\n'  # unknown
        sif_data += 'MC=' + (line.product_id.attribute_value_ids.filtered(
            lambda r: r.attribute_id.name == 'Catalog').name or " "  # Catalog
        ) + '\n'
        sif_data += 'QT=' + str(line.product_qty) + '\n'  # Product Quantity
        sif_data += 'ZO=' + str(line.sequence) + '\n'  # Sequence
        sif_data += 'PL=' + str(product_price) + '\n'  # Product List Price
        sif_data += 'WT=' + str(line.product_id.weight) + '\n'  # Weight
        sif_data += 'VO=' + str(line.product_id.volume) + '\n'  # Volume
        sif_data += 'V1= \n'  # unknown
        sif_data += 'V2= \n'  # unknown
        sif_data += 'V3= \n'  # unknown
        sif_data += 'S-=' + str(round(
            (product_price - customer_price) * 100 /
            product_price, 2)) + '\n'  # Sale Discount
        sif_data += 'P%=' + str(round(
            product_price - dealer_price * 100 /
            product_price, 2)) + '\n'  # Purchase Discount
        sif_data += 'GC=' + (line.product_id.attribute_value_ids.filtered(
            lambda r: r.attribute_id.name == 'Generic').name or " "
        ) + '\n'  # Generic Tag
        sif_data += 'PV=' + line.product_id.product_tmpl_id.default_code + '\n'
        sif_data += 'EV=' + "" + '\n'
        sif_data += '3D=\n'  # unknown
        sif_data += 'L1=' + (
            line.sale_line_id.product_id.name.split(
                ' - ')[0] or "Alias") + '\n'
        sif_data += 'L2= \n'
        sif_data += 'L3= \n'
        for attribute in line.product_id.attribute_value_ids.filtered(
                lambda r: r.attribute_id.name != 'Catalog'):
            on_code = attribute.attribute_id.name.split("-")
            sif_data += 'ON=' + on_code[0] + '\n'
            sif_data += 'OD=' + (
                on_code[1] + ":" + attribute.name
                if len(on_code) == 2 else attribute.name) + '\n'
        return sif_data

    @api.multi
    def generate_file(self):
        self.ensure_one()
        purchase_order = self.env[
            self._context.get('active_model')].browse(
                self._context.get('active_id'))
        sif_data = 'SF=\nST=\n'
        for line in purchase_order.order_line:
            sif_data = self._prepare_lines_items(line, sif_data)
        self.sif_binary = base64.b64encode(
            bytes(sif_data.encode('UTF-8')))
        self.write({
            'state': 'download',
            'name': purchase_order.name + '.sif',
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
