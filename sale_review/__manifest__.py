# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Sale Review IHO',
    'summary': 'Module for the review versions',
    'version': '13.0.1.0.0',
    'category': 'Sale',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'sale_order_version',
        'iho_security',
        'hr',
    ],
    'data': [
        'data/activity_type.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'wizard/sale_order_version_wizard_view.xml',
    ],
}
