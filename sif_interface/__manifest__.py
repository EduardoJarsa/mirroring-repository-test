# Copyright 2020, Mtnet Services, S.A. de C.V.
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sif Interface',
    'summary': '''Create Bill of Materials by XML files
                 and export it as SIF files''',
    'version': '13.0.1.0.0',
    'category': 'Customs',
    'author': 'MtNet Services, Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'mrp',
        'sale_management',
        'l10n_mx_edi',
        'supplier_product_discounts',
    ],
    'data': [
        'data/res_partner_data.xml',
        'data/sif_interface_data.xml',
        'data/product_product_data.xml',
        'data/decimal_precision_data.xml',
        'wizard/import_sale_order_wizard.xml',
        'views/res_config_view.xml',
        'views/mrp_bom_view.xml',
        'views/product_supplierinfo_view.xml',
        'views/product_product_view.xml',
        'wizard/export_sif_wizard_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
    ],
    "external_dependencies": {
        "python": [
            "xlrd",
        ],
    },
}
