# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase

# pylint: disable=W8121


class TestStockPicking(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product = self.env.ref("product.product_product_6")
        routes = self.env["stock.location.route"]
        routes |= self.env.ref("purchase_stock.route_warehouse0_buy")
        routes |= self.env.ref("stock.route_warehouse0_mto")
        self.product.route_ids = [(6, 0, routes.ids)]
        self.partner = self.env.ref("base.res_partner_12")
        self.warehouse_1 = self.env.ref("stock.warehouse0")
        self.warehouse_2 = self.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2",
                "code": "TEST2",
            }
        )
        self.warehouse_3 = self.env["stock.warehouse"].create(
            {
                "name": "Warehouse 3",
                "code": "TEST3",
            }
        )
        self.order = self.create_sale_order()
        self.customer_picking = self.order.picking_ids
        self.purchase_picking = self.get_purchase_picking()

    def create_sale_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        return order

    def validate_picking(self, picking):
        for move in picking.move_line_ids:
            move.qty_done = move.product_uom_qty
        picking.button_validate()

    def get_purchase_picking(self):
        order = self.env["purchase.order"].search([("origin", "=", self.order.name)])
        order.picking_type_id = self.warehouse_2.in_type_id.id
        order.button_confirm()
        self.validate_picking(order.picking_ids)
        return order.picking_ids

    def test_10_create_route_internal(self):
        context = {
            "active_id": self.purchase_picking.id,
        }
        wizard = (
            self.env["stock.create.manual.route.wizard"]
            .with_context(**context)
            .create(
                {
                    "move_type": "internal",
                    "warehouse_id": self.warehouse_3.id,
                    "programed_date": fields.Date.today(),
                }
            )
        )
        res = wizard.run_routing()
        picking_ids = res["domain"][0][2]
        pickings = self.env["stock.picking"].browse(picking_ids)
        picking_wh2 = pickings.filtered(lambda p: p.picking_type_id.warehouse_id.id == self.warehouse_2.id)
        picking_wh3 = pickings.filtered(lambda p: p.picking_type_id.warehouse_id.id == self.warehouse_3.id)
        self.assertEqual(len(picking_wh2), 1)
        self.assertEqual(len(picking_wh3), 1)
