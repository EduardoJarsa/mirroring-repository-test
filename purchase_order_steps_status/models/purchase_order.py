# Copyright 2021, MtNet Services Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    current_step = fields.Selection([
        ('poaccepted',  _('Purchase order Accepted')),
        ('production',  _('Production')),
        ('intltransit', _("Int'l Transit")),
        ('customs', _('Customs')),
        ('bonded', _('Bonded warehouse')),
        ('transit', _('Transit')),
        ('warehouse', _('Warehouse')),
        ])
    current_step_text = fields.Char()
    date_po_accepted = fields.Date()
    date_po_accepted_text = fields.Char()
    date_production_starts = fields.Date()
    date_production_starts_text = fields.Char()
    date_production_ends = fields.Date()
    date_production_ends_text = fields.Char()
    date_pick_origin_intltransit = fields.Date()
    date_pick_origin_intltransit_text = fields.Char()
    date_arrives_customs = fields.Date()
    date_arrives_customs_text = fields.Char()
    date_bonded_warehouse = fields.Date()
    date_bonded_warehouse_text = fields.Char()
    date_pick_customs_transit = fields.Date()
    date_pick_customs_transit_text = fields.Char()
    date_warehouse = fields.Date()
    date_warehouse_text = fields.Char()
    current_step_health = fields.Char(
        compute='_compute_current_step_health',
        default='N/A')
    current_step_percentage = fields.Float(
        compute='_compute_current_step_percentage',
        default=0.0)

    def _compute_current_step_health(self):
        for record in self:
            record.current_step_health = 'Ok'

    @api.depends('current_step')
    def _compute_current_step_percentage(self):
        for record in self:
            record.current_step_percentage = 0.0
            if record.current_step == 'poaccepted':
                record.current_step_percentage = 100/7
                break
            if record.current_step == 'production':
                record.current_step_percentage = 200/7
                break
            if record.current_step == 'intltransit':
                record.current_step_percentage = 300/7
                break
            if record.current_step == 'customs':
                record.current_step_percentage = 400/7
                break
            if record.current_step == 'bonded':
                record.current_step_percentage = 500/7
                break
            if record.current_step == 'transit':
                record.current_step_percentage = 600/7
                break
            if record.current_step == 'warehouse':
                record.current_step_percentage = 700/7
                break
