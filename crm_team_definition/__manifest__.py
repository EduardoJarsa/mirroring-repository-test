# Copyright 2019, MTNET Services, S.A. de C.V.
# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': "CRM Team Definition",

    'summary':  """
        Adds a team tab on notebook's opportunity for
        teams management
    """,

    'author': "Jarsa Sistemas",
    'website': "https://www.jarsa.com.mx",
    'license': 'LGPL-3',

    'category': 'crm',
    'version': '13.0.1.0.0',

    'depends': [
        'crm',
        'sale',
        'hr'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
