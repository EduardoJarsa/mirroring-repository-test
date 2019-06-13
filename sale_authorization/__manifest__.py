# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Sale Authorization',
    'summary': 'Module for the authorization of third parties in quotes',
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'sale_review',
        'sale_order_version',
        'sale_order_sequence',
    ],
    'data': [
        'security/security.xml',
        'views/sale_order_view.xml',
        'views/crm_lead_view.xml',
    ],
}
