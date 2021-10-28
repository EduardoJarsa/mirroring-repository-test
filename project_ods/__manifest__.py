# Copyright 2021, MtNet Services SA de CV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Project for IHO Service Orders',
    'summary': 'Modification to the Project module to be used '
    'for IHO Service orders',
    'version': '13.0.1.0.0',
    'category': 'project',
    'author': 'MtNet Services, Jarsa Sistemas',
    'website': 'https://www.mtnet.com.mx/',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'web_gantt',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project_project_view.xml',
        'views/project_task_view.xml',
        'views/project_task_class_view.xml',
    ],
}
