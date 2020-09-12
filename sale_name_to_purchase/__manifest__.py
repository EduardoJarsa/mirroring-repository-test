# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Transfer SO name to PO',
    'summary': """
    This module allow change name to purchase order
    on base a prefix of letter of alphabet and
    the name of Sale Order
    """,
    'version': '13.0.1.0.0',
    'category': 'Customs',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'purchase',
    ],
}
