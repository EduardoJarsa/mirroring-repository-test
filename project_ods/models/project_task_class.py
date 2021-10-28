# Copyright 2021, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ProjectTaskClass(models.Model):
    _name = 'project.task.class'
    _description = 'Task classifications for IHO Project tasks'
    _order = 'display_name asc'

    name = fields.Char()
    display_name = fields.Char(
        compute='_compute_display_name',
        store=True,
    )
    parent_id = fields.Many2one(
        'project.task.class',
    )

    @api.depends('name', 'parent_id')
    def _compute_display_name(self):
        for rec in self:
            res = rec.parent_id.name + "/ " if rec.parent_id else ""
            rec.display_name = res + rec.name if rec.name else ""
            # res = ""
            # if rec.parent_id:
            #     res = rec.parent_id.name + "/ "
            # rec.display_name = res + rec.name
