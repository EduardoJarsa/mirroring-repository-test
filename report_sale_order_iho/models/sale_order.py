# Copyright 2018, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

# pylint: disable=context-overridden


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image_sol = fields.Binary("Add image", attachment=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id.image_medium:
            self.image_sol = self.product_id.image_medium


class SaleOrderTerm(models.Model):
    _name = "sale.order.term"
    _description = "Terms and Conditions for Sales Order"
    _order = "sequence asc"
    _rec_name = "term_id"

    name = fields.Html(required=True)
    order_id = fields.Many2one("sale.order", required=True)
    term_id = fields.Many2one("sale.term", required=True)
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.term_id.code
            result.append((rec.id, name))
        return result

    @api.model
    def create(self, values):
        order = self.env["sale.order"].browse(values["order_id"])
        new_term = self.env["sale.term"].browse(values["term_id"])
        sale_order_terms = order.mapped("sale_order_term_ids.term_id")
        if new_term in sale_order_terms:
            raise ValidationError(_("This term is already in Sale Order"))
        # Compare with invalid combination of sale order
        invalid_terms = sale_order_terms.filtered(lambda term: new_term in term.invalid_term_ids)
        invalid_terms |= new_term.invalid_term_ids.filtered(lambda term: term in sale_order_terms)
        if invalid_terms:
            invalid_terms = ["[%s] %s" % (x.category_id.name, x.code) for x in invalid_terms]
            raise ValidationError(
                _("Unable to add this term, it is not compatible with the terms.\n %s") % "\n".join(invalid_terms)
            )
        return super().create(values)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery = fields.Text("Delivery time")
    sale_order_term_ids = fields.One2many("sale.order.term", "order_id", string="Terms and Conditions")
    incoterm_spec = fields.Text()

    @api.model
    def create(self, values):
        res = super().create(values)
        res._generate_terms(add_defaults=True)
        return res

    def write(self, values):
        res = super().write(values)
        self._generate_terms()
        return res

    def _generate_terms(self, add_defaults=False):
        for rec in self:
            context = {"lang": rec.partner_id.lang}
            updated_terms = False
            if rec.sale_order_term_ids:
                updated_terms = rec.sale_order_term_ids.mapped("term_id").ids
                for term in rec.sale_order_term_ids:
                    term.name = safe_eval(
                        term.term_id.with_context(**context).name, {"order": rec.with_context(**context)}
                    )
            terms = self.env["sale.term"].search(
                [("default", "=", True), ("id", "not in", updated_terms)], order="sequence asc"
            )
            if not add_defaults:
                continue
            new_terms = []
            # Use context to allow to get translation from terms.
            for term in terms:
                new_terms.append(
                    {
                        "name": safe_eval(term.with_context(**context).name, {"order": rec.with_context(**context)}),
                        "order_id": rec.id,
                        "term_id": term.id,
                        "sequence": term.sequence,
                    }
                )
            rec.sale_order_term_ids.create(new_terms)

    def get_product_freight(self):
        for rec in self.mapped("order_line"):
            fleet_product = self.env.ref("sale_fleet_service.product_product_fleet_service")
            if rec.product_id.id == fleet_product.id:
                return {"unit_price": rec.price_unit, "product_id": rec.product_id.id}

    def find_images(self):
        images = []
        for rec in self.mapped("order_line"):
            if rec.image_sol:
                images.append(rec.product_id)
        if not images:
            return False

    amount_services = fields.Float(compute="_compute_amount_services")

    @api.depends("order_line")
    def _compute_amount_services(self):
        for rec in self:
            order_lines = rec.order_line
            services = 0
            for line in order_lines:
                percentage_service = line.iho_service_factor - 1
                services += line.iho_sell_3 * percentage_service * line.product_uom_qty
            rec.amount_services = services

    def _return_code(self, code):
        str_descr = ""
        for char in code:
            if char != "]":
                str_descr = str_descr + char
            else:
                break
        return str_descr[1:]

    def _return_description(self, descr):
        count_char = 0
        for char in descr:
            if char != "]":
                count_char += 1
            else:
                break
        count_char += 1
        return descr[count_char:]
