# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Fleet Service',
    'summary': 'Add a fleet service line on sale orders',
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'sale_timesheet',
        'sif_interface',
    ],
    'data': [
        'data/project_project.xml',
        'data/product_product.xml',
        'views/res_config_settings_view.xml',
        'views/sale_order_view.xml',
    ],
}
