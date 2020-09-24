# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta
from odoo import _, api, fields, models


class StockCreateManualRouteWizard(models.TransientModel):
    _name = "stock.create.manual.route.wizard"
    _description = "Create Manual Route"

    move_type = fields.Selection(
        [('internal', 'Internal'),
         ('customer', 'Customer')],
        required=True,
        default='internal',
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        default=lambda self: self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.user.company_id.id)], limit=1),
        required=True,
    )
    programed_date = fields.Datetime(
        required=True,
        help='field to indicate when it leaves the warehouse to transit '
             'and when it will be received from the other side.')

    def _prepare_stock_move(self, move, picking):
        """ Prepare the stock moves data for one order line.
            This function returns a list of
            dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        return {
            'name': move.name or '',
            'product_id': move.product_id.id,
            'product_uom_qty': move.product_uom_qty,
            'product_uom': move.product_uom.id,
            'date': picking.date,
            'date_expected': picking.scheduled_date,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': picking.partner_id.id,
            'state': 'draft',
            'purchase_line_id': move.purchase_line_id.id,
            'company_id': move.company_id.id,
            'price_unit': move.price_unit,
            'picking_type_id': move.picking_type_id.id,
            'group_id': move.group_id.id,
            'origin': move.origin,
            'route_ids': move.route_ids.ids,
            'warehouse_id': move.warehouse_id.id,
        }

    @api.model
    def _prepare_picking(self, picking, picking_type,
                         src_location, dest_location, scheduled_date):
        self.ensure_one()
        return {
            'picking_type_id': picking_type.id,
            'partner_id': picking.partner_id.id,
            'date': scheduled_date,
            'scheduled_date': scheduled_date,
            'origin': picking.origin,
            'location_dest_id': dest_location.id,
            'location_id': src_location.id,
            'company_id': picking.company_id.id,
        }

    @api.model
    def create_pickings(self):
        picking_obj = self.env['stock.picking']
        active_id = self._context.get('active_id')
        src_picking = picking_obj.browse(active_id)
        picking_type_out = src_picking.picking_type_id.warehouse_id.int_type_id
        picking_type_in = self.warehouse_id.int_type_id
        transit_location = (
            self.env.user.company_id.internal_transit_location_id)
        dest_location = self.warehouse_id.lot_stock_id
        scheduled_date = self.programed_date + timedelta(days=1)
        # Create the out picking
        out_picking = picking_obj.create(
            self._prepare_picking(
                picking=src_picking,
                picking_type=picking_type_out,
                src_location=src_picking.location_dest_id,
                dest_location=transit_location,
                scheduled_date=scheduled_date,
            )
        )
        # Create the In picking
        in_picking = picking_obj.create(
            self._prepare_picking(
                picking=src_picking,
                picking_type=picking_type_in,
                src_location=transit_location,
                dest_location=dest_location,
                scheduled_date=scheduled_date,
            )
        )
        return src_picking, out_picking, in_picking

    @api.model
    def create_moves(self, src_picking, out_picking, in_picking):
        sm_obj = self.env['stock.move']
        link_move = False
        for move in src_picking.move_lines:
            dest_location = self.warehouse_id.lot_stock_id
            move_dest_ids = move.purchase_line_id.move_dest_ids
            orig_dest_location = move_dest_ids.mapped('location_id')
            # Create the output move
            out_move = sm_obj.create(
                self._prepare_stock_move(move, out_picking))
            # Create the input move
            in_move = sm_obj.create(
                self._prepare_stock_move(move, in_picking))
            # Link Moves
            out_move.write({'move_dest_ids': [(4, in_move.id)]})
            in_move.write({'move_orig_ids': [(4, out_move.id)]})
            # If the destination location is the same location than
            # the origin location of the delivery order we only
            # link the moves to complete the delivery
            if orig_dest_location == dest_location:
                move_dest_ids.write({
                    'move_orig_ids': [(6, 0, in_move.ids)],
                })
                in_move.write({
                    'move_dest_ids': [(6, 0, move_dest_ids.ids)],
                })
                link_move = True
        return link_move

    @api.model
    def prepare_action(self):
        return {
            'name': _('Stock Picking'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
            }
        }

    @api.model
    def run_customer_route(self):
        picking_obj = self.env['stock.picking']
        active_id = self._context.get('active_id')
        src_picking = picking_obj.browse(active_id)
        scheduled_date = self.programed_date + timedelta(days=1)
        # Create the out picking
        for move in src_picking.move_lines:
            # Create the output move
            move_dest_ids = move.purchase_line_id.move_dest_ids
            move_dest_ids.write({
                'move_orig_ids': [(6, 0, move.ids)],
                'location_id': src_picking.location_dest_id.id,
            })
        picking = move_dest_ids.picking_id
        picking.write({
            'location_id': src_picking.location_dest_id.id,
            'scheduled_date': scheduled_date,
        })
        picking.action_assign()
        res = self.prepare_action()
        res['res_id'] = picking.id
        return res

    @api.model
    def run_internal_route(self):
        # Process the pickings
        src_picking, out_picking, in_picking = self.create_pickings()
        # Create or Link the moves
        self.create_moves(src_picking, out_picking, in_picking)
        # Confirm the new pickings
        out_picking.action_confirm()
        out_picking.action_assign()
        in_picking.action_confirm()
        in_picking.action_assign()
        picking_ids = [out_picking.id, in_picking.id]
        # Return the action to see the pickings created
        res = self.prepare_action()
        res.update({
            'domain': [('id', 'in', picking_ids)],
            'view_mode': 'tree,form',
        })
        return res

    def run_routing(self):
        self.ensure_one()
        # If the move type is not internal we create a direct delivery
        if self.move_type == 'customer':
            return self.run_customer_route()
        return self.run_internal_route()
