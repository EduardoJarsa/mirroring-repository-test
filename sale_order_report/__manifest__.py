# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale order report for IHO',
    'summary': 'Custom module for sale order report',
    'version': '12.0.1.0.0',
    'category': 'Report',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'sale_management',
    ],
    'data': [
        'data/default_template.xml',
        'views/sale_order_view.xml',
        'views/sale_order_template.xml',
        'reports/report_papaerformat.xml',
    ],
}
