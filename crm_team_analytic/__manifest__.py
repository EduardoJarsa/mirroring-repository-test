# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CRM Team Analytic',
    'summary': """
    This module add a funtion that auto select
    analytic tags on the selected sales team
    """,
    'version': '13.0.1.0.0',
    'category': 'Sale',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'sale',
        'account_accountant',
    ],
    'data': [
        'views/crm_team_view.xml',
    ],
}
