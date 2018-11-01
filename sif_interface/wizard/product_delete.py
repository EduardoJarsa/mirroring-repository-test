import odoorpc
import progressbar
odoo = odoorpc.ODOO(timeout=1232131)
odoo.login('iho12', 'admin', 'admin')
product_template_obj = odoo.env['product.template']
mrp_obj = odoo.env['mrp.production']
product_template_boms = product_template_obj.search([
    ('attribute_line_ids', '=', False),
    ('bom_count', '!=', 0)])
obj_product_template_boms = product_template_obj.browse(product_template_boms)
count = 0
bar = progressbar.ProgressBar(max_value=len(obj_product_template_boms)).start()
for line in obj_product_template_boms:
    count += 1
    boms = line.bom_ids
    for bom in boms:
        odoo.execute(
            'mrp.production',
            'action_cancel',
            mrp_obj.search([('bom_id', '=', bom.id)]))
        odoo.execute(
            'mrp.production',
            'unlink',
            mrp_obj.search([('bom_id', '=', bom.id)]))
    boms.unlink()

product_templates = product_template_obj.search([
    ('attribute_line_ids', '=', False)])
obj_product_templates = product_template_obj.browse(product_templates)
obj_sale_order_line = odoo.env['sale.order.line']
obj_product_product = odoo.env['product.product']
count1 = 0
bar1 = progressbar.ProgressBar(max_value=len(obj_product_templates)).start()
for product in obj_product_templates:
    count1 += 1
    for prod_prod in product.product_variant_ids:
        order_line = obj_sale_order_line.browse(
            obj_sale_order_line.search([('product_id', '=', prod_prod.id)]))

        if order_line.order_id.state != 'cancel':
            order_line.order_id.action_cancel()
            order_line.order_id.unlink()
        prod_prod.unlink()
    product.unlink()
