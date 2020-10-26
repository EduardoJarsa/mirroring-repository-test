# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# pylint: disable=C0103

from odoo import fields, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_select_supplier(self, values, suppliers):
        """Method overridden from odoo to return the propper supplier info
        searching it taking in consideration the origin sale order"""
        res = super()._make_po_select_supplier(
            values, suppliers)
        supplier = suppliers.with_context(values=values).filtered(
            lambda r: r.sale_order_id == r._context.get(
                'values').get('group_id').sale_id and r.sale_order_id) or res
        return supplier

    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po):
        """Method overridden from odoo to set the proper product price
        unit on PO taking in consideration multi currency and the supplier info
        from so"""
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po)
        seller = values.get('supplier')
        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(
            taxes, product_id, seller.name) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(
                lambda x: x.company_id.id == values['company_id'].id)
        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            seller.price, product_id.supplier_taxes_id,
            taxes_id, values['company_id']) if seller else 0.0
        if (price_unit and seller and po.currency_id and
                seller.currency_id != po.currency_id):
            price_unit = seller.currency_id._convert(
                price_unit, po.currency_id,
                po.company_id, po.date_order or fields.Date.today())
        res['price_unit'] = price_unit
        return res
