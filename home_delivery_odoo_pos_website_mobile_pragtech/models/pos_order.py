from odoo import models,fields,api


class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    pos_delivery_order_ref = fields.Many2one('picking.order',string='Delivery Order Ref',readonly=True)
    delivery_type = fields.Selection([('home_delivery', 'Home Delivery'),
                                      ('default', 'Default')], string='Delivery Type', default='default')

    @api.model
    def create(self, vals):
        if vals.get('pos_reference'):
            pos_delivery_order = self.env['picking.order'].search([('name', '=', vals.get('pos_reference'))])
            if pos_delivery_order:
                vals['pos_delivery_order_ref'] = pos_delivery_order.id
                pos_delivery_order.write({'payment_status': 'Paid'})
        res = super(PosOrderInherit, self).create(vals)
        return res

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrderInherit, self)._order_fields(ui_order)
        if not ui_order.get('table_id'):
            res['delivery_type'] = ui_order.get('delivery_type')
        return res
