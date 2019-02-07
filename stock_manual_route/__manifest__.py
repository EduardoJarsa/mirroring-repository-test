# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Stock Manual Route',
    'summary': 'Create the Stock Routing Manually',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'sale_stock',
        'purchase_stock',
    ],
    'data': [
        'wizards/stock_create_manual_route_wizard_view.xml',
        'views/stock_picking_view.xml',
    ]
}
