# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# Copyright 2019, MtNet SA de CV, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Translations',
    'summary': 'Translations required for Spanish for IHO',
    'version': '12.0.1.0.0',
    'category': 'Translation',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'crm',
    ],
    'data': [
        'security/security.xml',
        'data/utm.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
    ],
}
