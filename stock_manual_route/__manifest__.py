# Copyright 2019, Jarsa
# Copyright 2021, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Manual Route",
    "summary": "Create the Stock Routing Manually, Adds sale order as origin at the picking IN",
    "version": "13.0.1.0.0",
    "category": "Stock",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "sale_stock",
        "purchase_stock",
    ],
    "data": [
        "wizards/stock_create_manual_route_wizard_view.xml",
        "views/stock_picking_view.xml",
    ],
}
