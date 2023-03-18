# Copyright 2019, Jarsa
# Copyright 2020, MtNet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Authorization",
    "summary": "Module for the authorization of third parties in quotes",
    "version": "13.0.1.0.0",
    "category": "Sale",
    "author": "MtNet Services, Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "sale_crm",
        "sale_review",
        "sale_order_version",
        "sale_order_sequence",
        "sif_interface",
    ],
    "data": [
        "security/security.xml",
        "views/sale_order_view.xml",
        "views/crm_lead_view.xml",
    ],
}
