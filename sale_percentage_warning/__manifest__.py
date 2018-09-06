# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Percentage Warning',
    'summary': 'percentage',
    'version': '11.0.1.0.2',
    'category': 'Connector',
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
    'installable': True,
}
