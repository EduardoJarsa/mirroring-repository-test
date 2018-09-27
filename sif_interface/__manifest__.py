# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sif Interface',
    'summary': '''Create Bill of Materials by XML files
                 and export it as SIF files''',
    'version': '11.0.1.0.0',
    'category': 'Customs',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
        'sale_management',
    ],
    'data': [
        'wizards/import_2020_wizard_view.xml',
    ],
}
