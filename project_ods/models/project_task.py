# Copyright 2021, MtNet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_task_class_ids = fields.Many2many(
        'project.task.class',
    )
    ptc_was_modified = fields.Boolean(
        compute='_compute_ptc_was_modified',
        store=True,
    )
    ptc_number_of_ids = fields.Integer(
        compute='_compute_ptc_number_of_ids',
    )
    ptc_service_type = fields.Char(
        compute='_compute_ptc_service_type',
    )
    ptc_additionals = fields.Char(
        compute='_compute_ptc_additionals',
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        help='Approved sale order of the Customer',
    )
    sale_order_opportunity_id = fields.Many2one(
        'crm.lead',
        compute='_compute_sale_order_opportunity_id',
        help='Registered opportunity at the sale order',
    )
    planner_id = fields.Many2one(
        'hr.employee',
        help='Available Planners as "Proyectista"',
    )
    service_center_id = fields.Many2one(
        'res.partner',
        help='Company Service centers registered as company contacts "Suc "',
    )
    company_partner_id = fields.Many2one(
        'res.partner',
        compute='_compute_company_partner_id',
        store=True,
    )
    to_invoice = fields.Float(
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    requested_execution_date_time = fields.Datetime(
        help='Date this order has to be executed',
    )
    service_order_number = fields.Char(
        string='OdS'
    )
    service_order_contact_id = fields.Many2one(
        'res.partner',
    )
    service_order_address_id = fields.Many2one(
        'res.partner',
    )
    project_project_service_order_iho = fields.Boolean(
        related='project_id.service_order_iho'
    )
    project_project_warehouse_order_iho = fields.Boolean(
        related='project_id.warehouse_order_iho'
    )
    ods_oda_name = fields.Char(
        compute='_compute_ods_oda_name'
    )

    @api.depends(
        'project_project_warehouse_order_iho',
        'project_project_service_order_iho'
    )
    def _compute_ods_oda_name(self):
        for rec in self:
            ods_oda_text = ''
            if rec.project_project_service_order_iho:
                ods_oda_text = 'Service Order'
            if rec.project_project_warehouse_order_iho:
                ods_oda_text = 'Warehouse Order'
            rec.ods_oda_name = ods_oda_text

    @api.depends('project_task_class_ids')
    def _compute_ptc_was_modified(self):
        for rec in self:
            rec.ptc_was_modified = True

    @api.depends('project_task_class_ids')
    def _compute_ptc_number_of_ids(self):
        for rec in self:
            rec.ptc_number_of_ids = (len(
                rec.project_task_class_ids.filtered(
                    lambda l: l.warning_message
                ).ids
            ) if rec.project_task_class_ids else 0)

    @api.depends('name', 'service_order_number')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                (rec.service_order_number + ' '
                    if rec.service_order_number else '')
                + (rec.name
                    if rec.name else '')
            )

    @api.depends('company_id')
    def _compute_company_partner_id(self):
        for rec in self:
            rec.company_partner_id = (
                rec.company_id.partner_id if rec.company_id.partner_id
                else False
            )

    @api.depends('sale_order_id')
    def _compute_sale_order_opportunity_id(self):
        for rec in self:
            rec.sale_order_opportunity_id = (
                rec.sale_order_id.opportunity_id if rec.sale_order_id
                and rec.sale_order_id.opportunity_id else False
            )

    @api.depends('project_task_class_ids')
    def _compute_ptc_service_type(self):
        for rec in self:
            ptc_service_type = ''
            for ptc in rec.project_task_class_ids:
                ptc_service_type +=\
                    ptc.name+";   " if (
                        ptc.parent_id ==
                        self.env.ref('project_ods.project_task_class_service_type')
                    ) else ''
            rec.ptc_service_type = ptc_service_type

    @api.depends('project_task_class_ids')
    def _compute_ptc_additionals(self):
        for rec in self:
            ptc_additionals = ''
            for ptc in rec.project_task_class_ids:
                ptc_additionals +=\
                    ptc.name+";   " if (
                        ptc.parent_id ==
                        self.env.ref('project_ods.project_task_class_additionals')
                    ) else ''
            rec.ptc_additionals = ptc_additionals

    @api.constrains('requested_execution_date_time')
    def _validate_requested_execution_date(self):
        if (
            self.project_id.service_order_iho and
            self.requested_execution_date_time
        ):
            ts = fields.Datetime.now()
            dt = fields.Datetime.context_timestamp(self, ts)
            # if it is late, another day is added
            late_today = 1 if dt.hour >= 14 else 0
            best_date = date_utils.add(dt.date(), days=1+late_today)
            # list of non-working days based on project calendar
            non_working_days = []
            global_leave_ids =\
                self.project_id.resource_calendar_id.global_leave_ids
            if global_leave_ids:
                for leave in global_leave_ids:
                    for span in range(
                        0, (leave.date_to.date()-leave.date_from.date()).days
                    ):
                        non_working_days.append(
                            leave.date_from.date()+date_utils.get_timedelta(
                                span, 'day')
                        )
            # look for best possible execution day
            while (best_date.weekday() == 6) or (
                    best_date in non_working_days):
                best_date = date_utils.add(best_date, days=1)
            if self.requested_execution_date_time.date() < best_date:
                raise ValidationError(
                    _('Date not available, select on or after %s') %
                    best_date.strftime('%d-%m-%Y')
                )

    def show_task_warnings(self):
        return self.project_task_class_ids.show_class_warnings(
            self.project_task_class_ids.ids)

    def write(self, vals):
        for rec in self:
            if rec.project_id.service_order_iho:
                if not rec.service_order_number:
                    if not rec.service_center_id.service_order_sequence_id:
                        raise ValidationError(
                            _('Service center sequence not defined'))
                    vals['service_order_number'] = (
                        rec.service_center_id.service_order_sequence_id.
                        next_by_id())
                vals['ptc_was_modified'] = False
            if rec.project_id.warehouse_order_iho:
                if not rec.service_order_number:
                    if not rec.service_center_id.warehouse_order_sequence_id:
                        raise ValidationError(
                            _('Service center sequence not defined'))
                    vals['service_order_number'] = (
                        rec.service_center_id.warehouse_order_sequence_id.
                        next_by_id())
                vals['ptc_was_modified'] = False
            res = super().write(vals)
        return res
