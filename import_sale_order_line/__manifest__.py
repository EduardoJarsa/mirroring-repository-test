# Copyright 2019, Jarsa Sistemas S.A de C.V
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'IHO Import Sale Order Line',
    'summary': 'Import Sale Order from csv file',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'website': 'https://www.jarsa.com.mx',
    'author': 'Jarsa Sistemas',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'l10n_mx',
        'account',
        'sale_management',
        'stock',
        'sif_interface',
    ],
    'data': [
        'security/security.xml',
        'data/product_product.xml',
        'wizards/import_sale_order_line_wizard_view.xml',
        'views/import_sale_order_line_view.xml',
    ],
}
