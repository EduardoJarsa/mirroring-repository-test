# Copyright 2021, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class ProjectTaskClass(models.Model):
    _name = 'project.task.class'
    _description = 'Task classifications for IHO Project tasks'
    _order = 'display_name asc'

    name = fields.Char()
    display_name = fields.Char(
        compute='_compute_display_name',
        store=True,
    )
    warning_message = fields.Char(
    )
    parent_id = fields.Many2one(
        'project.task.class',
    )

    @api.depends('name', 'parent_id')
    def _compute_display_name(self):
        for rec in self:
            res = rec.parent_id.name + "/ " if rec.parent_id else ""
            rec.display_name = res + rec.name if rec.name else ""

    @api.model
    def show_class_warnings(self, origin):
        return {
            'name': _('Project class task warnings'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': self.env.ref(
                'project_ods.view_project_task_class_tree_warning_iho').id,
            'target': 'new',
            'res_model': 'project.task.class',
            'domain': [('id', 'in', origin), ('warning_message', '!=', False)],
            'type': 'ir.actions.act_window',
            'context': {
                'search_default_product_group_by': False,
                'search_default_usage_group_by': False,
                'create': False,
                'edit': False,
                'delete': False,
            }
        }
