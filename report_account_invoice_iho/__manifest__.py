# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Report: Invoice for IHO",
    "summary": "Custom report for invoice",
    "version": "13.0.1.0.0",
    "category": "report",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "l10n_mx_edi_supplier_defaults",
    ],
    "data": [
        "reports/account_invoice_report.xml",
        "views/account_journal_view.xml",
    ],
}
