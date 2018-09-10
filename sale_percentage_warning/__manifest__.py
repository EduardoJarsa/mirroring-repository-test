# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Percentage Warning',
    'summary': 'Module to limit the discount on each line of the sale order',
    'version': '11.0.1.0.0',
    'category': 'Sale',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'sale_management',
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/res_config_settings_view.xml',
    ],
}
