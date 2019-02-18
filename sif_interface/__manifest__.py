# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sif Interface',
    'summary': '''Create Bill of Materials by XML files
                 and export it as SIF files''',
    'version': '12.0.1.0.0',
    'category': 'Customs',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'purchase_supplierinfo_currency',
        'mrp',
        'sale_management',
        'document',
        'l10n_mx_edi',
    ],
    'data': [
        'data/ir_default_data.xml',
        'wizard/import_2020_wizard_view.xml',
        'views/mrp_bom_view.xml',
        'views/product_supplierinfo_view.xml',
        'wizard/export_sif_wizard_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
    ],
}
