# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Vendor discounts',
    'version': '12.0.1.0.0',
    'category': 'products',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'sif_interface'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/vendor_discount_view.xml',
        'views/product_template_view.xml',
    ],
}
