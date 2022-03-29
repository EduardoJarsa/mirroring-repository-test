# Copyright 2021, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    service_order_iho = fields.Boolean(
        default=False,
        help='To implement: \n1-Set project visibility as followers,'
        '\n   2-Per Service center set consecutive and admins'
        '\n   3-Assign users to the proper iho-ods sec. groups'
    )
    warehouse_order_iho = fields.Boolean(
        default=False,
    )
