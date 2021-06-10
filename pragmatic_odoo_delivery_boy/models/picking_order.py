from odoo import api, models, fields, tools
import json
import requests
import googlemaps
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError


class picking_order(models.Model):
    _name = "picking.order"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = "picking"
    _description = "Picking Order"

    active = fields.Boolean('Active',default=True)
    delivery_boy = fields.Many2one('res.partner','Delivery Boy',domain="[('is_driver', '=', True),('status','=','available')]")
    # assigned_date = fields.datetime('Assigned Date')
    sale_order = fields.Many2one('sale.order','Order')
    invoice = fields.Many2one('account.move','Invoice')
    picking = fields.Many2one('stock.picking', 'Picking')
    assigned_date = fields.Datetime("Assigned Date",default=fields.Datetime.now)
    partner_id = fields.Many2one(related='sale_order.partner_id', string="Partner name")
    state = fields.Selection([
        ('created', 'Created'),
        ('assigned', 'Assigned'),
        ('accept','Accepted By Driver'),
        ('in_progress', 'In Progress'),
        # ('reject','Rejected By Driver'),
        ('paid', 'Paid'),
        ('delivered', 'Delivered'),
        ('payment_collected', 'Payment Collected'),
        ('canceled', 'Canceled')
    ], string='Status', readonly=True, copy=False, index=True, default='created', tracking=True)
    payment = fields.Selection([
        ('unpaid', 'UnPaid'),
        ('paid', 'Paid'),
    ], string='Payment Status', readonly=True, copy=False, index=True, default='unpaid', tracking=True)

    distance_btn_2_loc = fields.Float("Distance in KM", copy=False)
    zip_code = fields.Char("Zip Code", copy=False)
    payment_collection = fields.Boolean("Payment Collected")
    order_source = fields.Selection([('sale', 'Sale'), ('pos', 'POS')], string="Order Source", default="sale", readonly=True)

    #Point of sale home delivery order fields
    pos_order_id = fields.Many2one('pos.order', 'Order')
    name = fields.Char(string='Order', required=False, readonly=True, copy=False)
    # partner_id = fields.Many2one('res.partner', string='Customer', change_default=True, index=True)
    pos_partner_id = fields.Many2one('res.partner', string='Customer', change_default=True, index=True)
    '''used only for display purpose, showing the inputed value of pos'''
    display_delivery_time = fields.Datetime(string='Delivery Time',default=fields.Datetime.now,tracking=True)

    '''
        this is the actual delivery time which is stored in utc format in db,use this field to access the delivery time
    '''
    delivery_time = fields.Datetime(string='Delivery Time',default=fields.Datetime.now,readonly=True)
    street = fields.Char()
    street2 = fields.Char()
    # zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char(string="Email")
    phone = fields.Char(string="Mobile/Phone")
    # delivery_person = fields.Many2one('res.partner', string="Delivery Person",domain="[('is_driver', '=', True)]")
    bank_statement_ids = fields.One2many('pos.payment', 'picking_order_id', string='Payments', readonly=True)
    lines = fields.One2many('picking.order.line', 'picking_order_id', string='Order Lines', readonly=True, copy=True)
    session_id = fields.Many2one('pos.session', string='Session',readonly=True)
    order_date = fields.Datetime(string='Order Date', readonly=True, default=fields.Datetime.now)
    order_ref = fields.Char(string="Order Ref.", readonly=True)
    cashier = fields.Many2one('res.users', string="Cashier")
    order_note = fields.Text()
    # order_source = fields.Selection([('pos','POS')], string="Source", default="pos")
    payment_status_with_driver = fields.Boolean("Payment Status with driver")
    payment_status = fields.Char('Payment Status', default='Pending')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', help="The warehouse in which user belongs to.")
    # distance_btn_2_loc = fields.Float("Distance in KM", copy=False)
    latitude = fields.Char('Latitude')
    longitude = fields.Char('Longitude')
    transaction_id = fields.Many2one('payment.transaction', string='Transaction')
    acquirer_type = fields.Char(default='cash')
    payment_collection = fields.Boolean("Payment Collected")
    delivery_type = fields.Selection(
        [('home_delivery', 'Home Delivery'), ('take_away', 'Take Away'), ('default', 'Default')])

    def onchange_state_id(self,res):
        if self['delivery_boy'] and self['state'] in ['accept']:
            partner = self.env['res.partner'].sudo().browse(self.delivery_boy.id)
            deliveries= int(partner.assigned_deliveries)+1
            partner.write ({'assigned_deliveries':deliveries})
        elif self['delivery_boy'] and self['state'] in ['delivered']:
            partner = self.env['res.partner'].sudo().browse(self.delivery_boy.id)
            deliveries = int(partner.assigned_deliveries)-1
            partner.write ({'assigned_deliveries':deliveries})
            if deliveries<0:
                partner.assigned_deliveries = 0

    def action_picking_order_delivered(self):
        vals = {
            'state': 'delivered'
        }
        order_stage_id = self.env['order.stage'].search([('action_type', '=', 'delivered')])
        if order_stage_id:
            vals["stage_id"] = order_stage_id.id
        self.write(vals)

    def action_picking_order_paid(self):
        self.write({
            'state': 'paid'
        })

    def action_picking_order_canceled(self):
        self.write({'state': 'canceled'})

    def assignDriver(self):
        active_ids = self.env.context.get('active_ids',[])
        pickings = self.browse(active_ids)
        vals={}
        sale_orders = pickings.mapped('sale_order')
        vals['sale_order'] = sale_orders.ids
        picking_order_wizard= self.env['picking.order.wizard'].create(vals)

        return{
            'type': 'ir.actions.act_window',
            'name': 'Assign Delivery Boy by Zip Code',
            'res_model': 'picking.order.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': picking_order_wizard.id,
            'view_id': self.env.ref('pragmatic_odoo_delivery_boy.assign_driver_wizard', False).id,
            'target': 'new',
        }

    def write(self, vals):
        payment_transaction_obj = self.env['payment.transaction'].search([('id', 'in', self.sale_order.transaction_ids.ids)])
        vals['acquirer_type'] = payment_transaction_obj.acquirer_id.journal_id.type
        so_delivery_state = None
        if payment_transaction_obj:
            vals['acquirer_type'] = payment_transaction_obj.acquirer_id.journal_id.type
        if vals.get('payment_collection') == True:
            vals["state"] = 'payment_collected'
            order_stage_id = self.env['order.stage'].search([('action_type', '=', 'payment')])
            vals['active'] = False
            if order_stage_id:
                vals['stage_id'] = order_stage_id.id
                so_delivery_state = "paid"

        if vals.get('delivery_boy') != False:
            if self.state == 'created':
                vals['state'] = 'assigned'
                order_stage_id = self.env['order.stage'].search([('action_type', '=', vals.get('state'))])
                if order_stage_id:
                    vals['stage_id'] = order_stage_id.id
                    so_delivery_state = "assigned"

                Param = self.env['res.config.settings'].sudo().get_values()
                if Param.get('whatsapp_instance_id') and Param.get('whatsapp_token'):
                    if self.sale_order.partner_id.country_id.phone_code and self.sale_order.partner_id.mobile:
                        url = 'https://api.chat-api.com/instance' + Param.get('whatsapp_instance_id') + '/sendMessage?token=' + Param.get('whatsapp_token')
                        headers = {
                            "Content-Type": "application/json",
                        }
                        whatsapp_msg_number = self.sale_order.partner_id.mobile
                        whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "");
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(self.sale_order.partner_id.country_id.phone_code), "")
                        delivery_boy_id = self.env['res.partner'].search([('id', '=', vals.get('delivery_boy'))])
                        msg = "Your order " + delivery_boy_id.name + " driver has assigned."

                        tmp_dict = {
                            "phone": "+" + str(self.sale_order.partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                            "body": msg

                        }
                        response = requests.post(url, json.dumps(tmp_dict), headers=headers)

                        if response.status_code == 201 or response.status_code == 200:
                            _logger.info("\nSend Message successfully")

        elif vals.get('delivery_boy') == False:
            if self.state in ['assigned', 'accept']:
                vals['state'] = 'created'
                order_stage_id = self.env['order.stage'].search([('action_type', '=', 'ready')])
                if order_stage_id:
                    vals['stage_id'] = order_stage_id.id
                    so_delivery_state = "ready"

        if vals.get('delivery_person'):
            partner = self.env['res.partner'].browse(int(vals.get('delivery_person'))).ids
            driver_warehouse = self.env['stock.warehouse.driver'].search([('driver_id', 'in', partner)], limit=1)
            if driver_warehouse and driver_warehouse.warehouse_id:
                vals['warehouse_id'] = driver_warehouse.warehouse_id.id
            vals["delivery_boy"] = vals.get("delivery_person")
            del vals["delivery_person"]

        if vals.get("state") == "paid":
            order_stage_id = self.env['order.stage'].search([('action_type', '=', 'payment')])
            if order_stage_id:
                vals['stage_id'] = order_stage_id.id
                so_delivery_state = "paid"
        # some of the stages not updating fix
        if vals.get('invoice'):
            so_delivery_state = "paid"
            vals['payment'] = 'paid'
            vals['state'] = 'paid'
        if vals.get("stage_id") and self.sale_order:
            self.sale_order.write({'stage_id': vals['stage_id'], 'delivery_state': so_delivery_state})
        self.update_payment_status(vals)
        res = super(picking_order, self).write(vals)
        self.onchange_state_id(res)
        return res

    @api.model
    def create(self, vals):
        # pos delivery order patches to create picking order for pos delivery
        if vals.get("zip"):
            vals["zip_code"] = vals["zip"]
            del vals["zip"]
        if vals.get("partner_id"):
            vals["pos_partner_id"] = vals["partner_id"]
            del vals["partner_id"]
        if vals.get("delivery_person"):
            vals["delivery_boy"] = vals["delivery_person"]
            del vals["delivery_person"]
        if vals.get("delivery_state"):
            vals["state"] = vals["delivery_state"]

        res = super(picking_order, self.with_context(mail_create_nosubscribe=True)).create(vals)

        if vals.get('name'):
            pos_order = self.env['pos.order'].search([('pos_reference', '=', vals.get('name'))])
            if pos_order:
                res.pos_delivery_order_ref = pos_order.id
        res.update_payment_status(vals)
        return res

    @api.onchange('display_delivery_time')
    def onchange_deliverytime(self):
        self.delivery_time = self.display_delivery_time

    def update_payment_status(self, vals):
        if self.payment != 'paid' and self.sale_order:
            last_tx = self.sale_order.transaction_ids.get_last_transaction()
            if last_tx and last_tx.state == 'done' and last_tx.acquirer_id.journal_id.type != 'cash':
                vals['payment'] = 'paid'
                self.sale_order.delivery_state = 'paid'

    def in_progress_action(self):
        pos_order = self.env['pos.order'].search([('pos_reference', '=', self.name)])
        vals = {'state': 'in_progress'}
        if pos_order:
            vals["picking"] = pos_order.picking_id.id
            vals["pos_order_id"] = pos_order.id
        self.write(vals)

    def delivered_action(self):
        self.write({'state': 'delivered'})

    def make_payment_action(self):
        if self.name:
            pos_order = self.env['pos.order'].search([('pos_reference', '=', self.name)])
            if not pos_order:
                raise UserError("POS order not found.\n\n Before making payment, you need to validate POS from frontend.")
            elif pos_order:
                if pos_order.payment_ids:
                    if not self.bank_statement_ids:
                        for i in pos_order.payment_ids:
                            if i.name and 'return' not in i.name:
                                i.write({'name': pos_order.name + ': Home Delivery'})
                            elif not i.name:
                                i.write({'name': pos_order.name + ': Home Delivery'})

                        self.write({'bank_statement_ids': [(6, 0, pos_order.payment_ids.ids)],
                                    'state': 'paid',
                                    'pos_order_id': pos_order.id,
                                    'order_ref': pos_order.name})


class PickingOrderLine(models.Model):
    _name = "picking.order.line"
    _description = "Picking Delivery Order Line"

    picking_order_id = fields.Many2one('picking.order', string='Order Ref', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True)
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1)


class PosPayment(models.Model):
    _inherit = "pos.payment"

    picking_order_id = fields.Many2one('picking.order', string="POS Delivery Order statement", ondelete='cascade')
