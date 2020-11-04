# Copyright 2020, MtNet Services, S.A. de C.V.
# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'UI Simplification for IHO',
    'summary': 'Changes in UI such as fields, books, forms to simplify its use',
    'version': '13.0.1.0.0',
    'category': 'Sales',
    'author': 'MtNet, Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'utm',
        'crm',
        'sale_management',
        'sale_crm',
        'l10n_mx_edi',
    ],
    'data': [
        'data/utm.xml',
        'security/security.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
        'views/product_views.xml',
    ],
}
