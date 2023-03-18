# Copyright 2019, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Vendor discounts",
    "version": "13.0.1.0.0",
    "category": "products",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "AGPL-3",
    "depends": [
        "sale_review",
        "sale_order_version",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/vendor_discount_view.xml",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
    ],
}
