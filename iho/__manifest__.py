# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'IHO Instance Module',
    'summary': 'Module to install Instance',
    'version': '12.0.1.0.0',
    'category': 'Instance',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'base_user_role',
        'res_currency_rate_custom_decimals',
        'stock_move_quantity_limit',
        'sale_authorization',
        'sale_stock',
        'iho_security',
        'report_sale_order_iho',
        'sale_order_version',
        'crm_team_analytic',
        'sale_name_to_purchase',
        'sale_review',
        'stock_manual_route',
        'crm_team_definition',
        'supplier_product_discounts',
        'translations',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
    ],
}
