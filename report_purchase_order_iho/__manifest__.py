# Copyright 2021, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Report Purchase Order IHO",
    "summary": "Custom report for Purchase Order IHO",
    "version": "13.0.1.0.0",
    "category": "Report",
    "author": "Jarsa, MtNet Services SA de CV",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_order_view.xml",
        "reports/report_purchase_order.xml",
    ],
}
