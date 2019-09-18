# -*- coding: utf-8 -*-
{
    'name': "CRM Team Definition",

    'summary':  """
        Adds a team tab on notebook's opportunity for
        teams management    
    """,

    'description': """
        This module, adds a new tab to notebook's opportunity
        for managing teams, each member can have an specific
        percentage of the pretended revenue
    """,

    'author': "Jarsa Sistemas",
    'website': "https://www.jarsa.com.mx",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'crm',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'sale', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}