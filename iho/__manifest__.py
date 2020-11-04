# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'IHO Instance Module',
    'summary': 'Module to install Instance',
    'version': '13.0.1.0.1',
    'category': 'Instance',
    'author': 'MtNet, Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'base_user_role',
        'base_address_city',
        'purchase',
        'stock_move_quantity_limit',
        'sale_crm',
        'mrp',
        'sif_interface',
        'sale_authorization',
        'sale_stock',
        'report_sale_order_iho',
        'sale_order_version',
        'crm_team_analytic',
        'sale_name_to_purchase',
        'sale_review',
        'stock_manual_route',
        'crm_team_definition',
        'supplier_product_discounts',
        'l10n_mx',
        'l10n_mx_edi',
        'l10n_mx_reports',
        'iho_simplification',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/ir_ui_menu_view.xml',
    ],
}
