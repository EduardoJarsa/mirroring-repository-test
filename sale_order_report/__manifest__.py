# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Sale order report for IHO',
    'summary': 'Custom module for sale order report',
    'version': '12.0.1.0.0',
    'category': 'Report',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'sale_order_version',
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/sale_order_template.xml',
        'reports/report_papaerformat.xml',
    ],
}
