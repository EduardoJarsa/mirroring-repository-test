# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from odoo import api, fields, models

MAPPING = {
    'default_code': 'PN',
    'description': 'OD',
    'product_id.seller_ids': 'L'
}


class ExportSifWizard(models.TransientModel):
    _name = "export.sif.wizard"

    name = fields.Char()
    sif_binary = fields.Binary(string="Download File")
    state = fields.Selection(
        [('choose', 'Get'), ('download', 'Download')], default='choose')

    @api.model
    def _prepare_lines_items(self, line, sif_data):
        sif_data += 'PN=' + line.product_id.product_tmpl_id.default_code + '\n'
        sif_data += 'PD=' + line.product_id.name + '\n'
        sif_data += 'TG=' + "Aun no se que lleva." + '\n'
        sif_data += 'MC=' + (line.product_id.attribute_value_ids.filtered(
            lambda r: r.attribute_id.name == 'Catalog').name or "sin code"
        ) + '\n'
        sif_data += 'QT=' + str(line.product_qty) + '\n'
        sif_data += 'ZO=' + str(line.sequence) + '\n'
        sif_data += 'PL=' + str(line.price_unit) + '\n'
        sif_data += 'WT=' + "Aun no se que lleva. 0" + '\n'
        sif_data += 'VO=' + "Aun no se que lleva. 0" + '\n'
        sif_data += 'V1=' + "Aun no se que lleva." + '\n'
        sif_data += 'V2=' + "Aun no se que lleva." + '\n'
        sif_data += 'V3=' + "Aun no se que lleva." + '\n'
        sif_data += 'S-=' + "ofda:EndCustomerDiscount" + '\n'
        sif_data += 'P%=' + "ofda:OrderDealerDiscount" + '\n'
        sif_data += 'GC=' + (line.product_id.attribute_value_ids.filtered(
            lambda r: r.attribute_id.name == 'Catalog').name or "sin code"
        ) + '\n'
        sif_data += 'PV=' + line.product_id.product_tmpl_id.default_code + '\n'
        sif_data += 'EV=' + "" + '\n'
        sif_data += '3D=' + "Aun no se que lleva. no viene xml" + '\n'
        sif_data += 'L1=' + (
            line.sale_line_id.product_id.name or "Alias") + '\n'
        sif_data += 'L2=' + "Vacios hasta el momento" + '\n'
        sif_data += 'L3=' + "Vacios hasta el momento" + '\n'
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
