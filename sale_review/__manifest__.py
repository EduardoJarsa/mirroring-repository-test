# Copyright 2019, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Review IHO",
    "summary": "Module for the review versions",
    "version": "13.0.1.0.0",
    "category": "Sale",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "sale_order_version",
        "hr",
    ],
    "data": [
        "data/activity_type.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "wizard/sale_order_version_wizard_view.xml",
    ],
}
