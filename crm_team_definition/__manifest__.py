{
    'name': "CRM Team Definition",

    'summary':  """
        Adds a team tab on notebook's opportunity for
        teams management
    """,

    'author': "Jarsa Sistemas",
    'website': "https://www.jarsa.com.mx",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base
    # /data/ir_module_category_data.xml
    # for the full list
    'category': 'crm',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'crm',
        'sale',
        'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
