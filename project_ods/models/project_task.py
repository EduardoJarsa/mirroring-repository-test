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
        domain="[('job_id.name', '=', 'Proyectista')]",
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
            while best_date.weekday in [0, 6] or best_date in non_working_days:
                best_date = date_utils.add(best_date, days=1)
            if self.requested_execution_date_time.date() < best_date:
                raise ValidationError(
                    _('Date not available, select on or after %s') %
                    best_date.strftime('%d-%m-%Y')
                )

    def write(self, vals):
        for rec in self:
            res = super().write(vals)
            if (
                rec.project_id.service_order_iho
                and not rec.service_order_number
            ):
                if not rec.service_center_id.service_order_sequence_id:
                    raise ValidationError(
                        _('Service center sequence not defined'))
                next_folio = (
                    rec.service_center_id.service_order_sequence_id.
                    next_by_id())
                rec.write(
                    {'service_order_number': next_folio})
        return res
