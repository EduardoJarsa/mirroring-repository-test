# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, 2021 MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# pylint: disable=C0103

from odoo import _, models
from odoo.exceptions import ValidationError


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, company_id, origins, values):
        """ overriding currency_id based on purchase currency from partner """
        res = super()._prepare_purchase_order(company_id, origins, values)
        maker_currency = values[0].get('supplier').name.property_purchase_currency_id.id
        if maker_currency:
            res['currency_id'] = maker_currency
        else:
            partner_name = values[0].get('supplier').name.ref
            raise ValidationError(_(
                'Maker Partner [%s] has not Purchase Currency set') %
                (partner_name))
        return res

    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, company_id, values, po):
        """Set the proper product price unit on PO taking in consideration
        multi currency and the supplier info from so.
        Mar 7,2021: copying analytic fields as sale.order has them"""
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po)
        seller = values.get('supplier')
        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(
            taxes, product_id, seller.name) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(
                lambda x: x.company_id.id == values['company_id'].id)
        # search for the last unit price at the product.seller_ids
        sale_order = po.origin
        seller_price = False
        for record in product_id.seller_ids.sorted(
            key=lambda r: r.id, reverse=True
        ):
            if record.sale_order_id.name in sale_order:
                seller_price = record.price
        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            seller_price if seller_price else seller.price,
            product_id.supplier_taxes_id,
            taxes_id, values['company_id']) if seller else 0.0
        # if (price_unit and seller and po.currency_id and
        #         maker_currency != so_currency):
        #     price_unit = so_currency._convert(
        #         price_unit, maker_currency,
        #         po.company_id, po.date_order or fields.Date.today())
        res['price_unit'] = price_unit
        # copying analytic_tag_ids and analytic_account from so
        so_line = self.env['sale.order.line'].browse(
            values['sale_line_id'])
        res['analytic_tag_ids'] = so_line.analytic_tag_ids
        res['account_analytic_id'] = so_line.order_id.analytic_account_id.id
        return res
