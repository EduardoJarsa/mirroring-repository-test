# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Order Version',
    'summary': 'Allows to have a different versions of sale order',
    'version': '12.0.1.0.0',
    'category': 'sale',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'sale_stock',
        'sale_crm',
        'sif_interface'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/sale_order_version_wizard_view.xml',
        'wizard/sale_order_version_create_wizard.xml',
        'views/sale_order_view.xml',
        'views/sale_order_version_view.xml',
    ],
}
