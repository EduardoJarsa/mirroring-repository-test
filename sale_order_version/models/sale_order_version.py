# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class SaleOrderVersion(models.Model):
    _name = 'sale.order.version'

    name = fields.Char(
        string='Version',
    )
    prefix = fields.Integer()
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string="Sale Order Version",
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name='sale.order.version.line',
        inverse_name='sale_version_id',
        string='Sale Version Lines',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True,
    )
    validity_date = fields.Date(
        string='Validity', readonly=True, copy=False,
        help="Validity date of the quotation, after this date, the customer"
        " won't be able to validate the quotation online.")
    reference = fields.Char(
        string='Payment Ref.',
        help='The payment communication of this sale order.')
    company_id = fields.Many2one(
        'res.company', 'Company')
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')],)
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Payment Terms',
    )
    picking_policy = fields.Selection([
        ('direct', 'Deliver each product when available'),
        ('one', 'Deliver all products at once')],
        string='Shipping Policy', required=True, readonly=True,
        default='direct',
        help="If you deliver all products at once,"
        " the delivery order will be scheduled based on the greatest "
        "product lead time. Otherwise, it will be based on the shortest.")
    incoterm = fields.Many2one(
        'account.incoterms', 'Incoterms',
        help="International Commercial Terms are a series of predefined"
        " commercial terms used in international transactions.")
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True,)
    date_order = fields.Datetime(
        string='Order Date', required=True,
        readonly=True, index=True,
        copy=False, default=fields.Datetime.now)
    user_id = fields.Many2one(
        'res.users', string='Salesperson',
        default=lambda self: self.env.user)
    team_id = fields.Many2one(
        'crm.team', 'Sales Team',)
    expected_date = fields.Datetime(
        help="Delivery date you can promise to the customer,"
        " computed from product lead times and from the shipping "
        " policy of the order.")
    commitment_date = fields.Datetime(
        readonly=True, help="This is the delivery date promised to the"
        " customer. If set, the delivery order will be scheduled based"
        " on this date rather than product lead times.")
    origin = fields.Char(
        string='Source Document', help="Reference of the document that "
        " generated this sales order request.")
    client_order_ref = fields.Char(string='Customer Reference',)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        readonly=True,
        help="The analytic account related to a sales order.",)
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags')
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position',
        string='Fiscal Position')
    currency_agreed_rate = fields.Float(default=1.0,)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', required=True, readonly=True,
        help="Pricelist for current sales order.")
    tag_ids = fields.Many2many('crm.lead.tag', string='Tags')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')],
        string='Order Status',
        default='draft',
    )
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address',)


class SaleOrderVersionLine(models.Model):
    _name = 'sale.order.version.line'

    sale_version_id = fields.Many2one(
        comodel_name="sale.order.version",
        string="Sale Version",
    )
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain=[('sale_ok', '=', True)],
        ondelete='restrict')
    name = fields.Text(string='Description',)
    iho_price_list = fields.Float(string='Price List',)
    iho_discount = fields.Float(string='IHO Discount (%)',)
    iho_sell_1 = fields.Float(
        string='Sell 1')
    iho_factor = fields.Float(
        string='Factor',
        default=1.0,)
    iho_sell_2 = fields.Float(
        string="Sell 2")
    iho_sell_3 = fields.Float(
        string="Sell 3")
    product_uom_qty = fields.Float(
        string='Ordered Quantity',
        required=True, default=1.0)
    qty_delivered = fields.Float('Delivered Quantity')
    qty_invoiced = fields.Float(string='Invoiced Quantity')
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag', string='Analytic Tags')
    route_id = fields.Many2one(
        'stock.location.route',
        string='Route', domain=[('sale_selectable', '=', True)],)
    price_unit = fields.Float(
        'Unit Price', required=True, default=0.0)
    tax_id = fields.Many2many(
        'account.tax', string='Taxes')
    price_subtotal = fields.Float(string='Subtotal',)
    order_id = fields.Many2one(
        'sale.order', string='Order Reference',)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], help="Technical field for UX purpose.")
    image_sol = fields.Binary('Add image', attachment=True)
    vendor_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    iho_currency_id = fields.Many2one(
        'res.currency',
        string='IHO Currency',
    )
    iho_purchase_cost = fields.Float()
    discount = fields.Float(string='Discount (%)',)
