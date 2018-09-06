# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'IHO customs',
    'summary': 'Customs',
    'version': '11.0.1.0.0',
    'category': 'Customs',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'sale_percentage_warning',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
    ],
}
