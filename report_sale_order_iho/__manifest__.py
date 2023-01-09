# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# Copyright 2020, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale order report for IHO",
    "summary": "Custom module for sale order report",
    "version": "13.0.1.0.0",
    "category": "Report",
    "author": "Jarsa Sistemas",
    "website": "https://www.jarsa.com.mx",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "sale_order_version",
    ],
    "data": [
        "wizard/generate_sale_order_terms_wizard_view.xml",
        "views/sale_order_view.xml",
        "views/sale_term_view.xml",
        "views/sale_term_category_view.xml",
        "reports/report_papaerformat.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sale_term_category.xml",
        "data/sale_term.xml",
    ],
}
