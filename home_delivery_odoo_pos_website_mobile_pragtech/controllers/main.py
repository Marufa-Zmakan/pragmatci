import requests
from odoo import http, tools
from odoo.http import request
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError

from ...pragmatic_delivery_control_app.controllers.main import WebsiteCustomer
from ...pragmatic_odoo_delivery_boy.controllers.main_driver import WebsiteCustomerDriver

import pytz, ast
import json
import logging

OPG = 5  # Order Per Page

_logger = logging.getLogger(__name__)


class PosHomeDeliveryControl(http.Controller):

    @http.route(['/create/homedelivery'], type='json', auth="none")
    def create_order_home_delivery(self, **post):
        if 'partner_id' in post and 'name' in post and 'product_lst' in post:
            delivery_lst = post.copy()
            delivery_lst["order_source"] = "pos"
            delivery_lst["state"] = "assigned"
            del delivery_lst['product_lst']
            pos_delivery_order_srch = request.env['picking.order'].sudo().search([('name', '=', post['name']),
                                                                                  ('state', '!=', 'canceled')])
            if not pos_delivery_order_srch:
                if delivery_lst['ship_to_diff_addr'] == True:

                    del delivery_lst['ship_to_diff_addr']

                    partner = request.env['res.partner'].sudo().search([('id', '=', int(delivery_lst['partner_id']))])
                    current_uid = request.env.context.get('uid')
                    user = request.env['res.users'].sudo().browse(current_uid)

                    if partner and user.company_id:
                        partner_dict={}
                        if 'street' in delivery_lst:
                            partner_dict['street'] = delivery_lst['street'] or ''
                        if 'street2' in delivery_lst:
                            partner_dict['street2'] = delivery_lst['street2'] or ''

                        if 'city' in delivery_lst:
                            partner_dict['city'] = delivery_lst['city'] if delivery_lst['city'] else ''

                        if 'zip' in delivery_lst:
                            partner_dict['zip'] = delivery_lst['zip'] if delivery_lst['zip'] else ''

                        partner_dict['parent_id'] = partner.id
                        partner_dict['type'] = 'delivery'
                        partner_dict['name'] = delivery_lst['customer_name']
                        partner_dict['email'] = delivery_lst['email']
                        res = request.env['res.partner'].sudo().with_context(mail_create_nosubscribe=True,
                                                                             force_company=user.company_id.id).create(partner_dict)
                        delivery_lst['partner_id'] = res.id

                        if 'delivery_time' in post and 'display_delivery_time' in post:
                            delivery_lst['display_delivery_time'] = delivery_lst['display_delivery_time'].replace('T', " ")
                            delivery_lst['delivery_time'] = delivery_lst['delivery_time'].replace('T', " ")

                        if 'delivery_type' in post:
                            delivery_lst['delivery_type'] = delivery_lst['delivery_type']

                        del delivery_lst['customer_name']
                        if post.get('session_id'):
                            session_id = request.env['pos.session'].sudo().search(
                            [('id', '=', post.get('session_id'))])

                            if session_id.config_id and session_id.config_id.picking_type_id and session_id.config_id.picking_type_id.warehouse_id:
                                delivery_lst['warehouse_id'] = session_id.config_id.picking_type_id.warehouse_id.id
                        pos_delivery_order = request.env['picking.order'].sudo().create(delivery_lst)

                        # code for converting delivery time from utc to user timezone
                        if 'delivery_time' in post:
                            delv_time_format = pos_delivery_order.display_delivery_time.strftime(DATETIME_FORMAT)
                            delv_time = datetime.strptime(delv_time_format, DATETIME_FORMAT)
                            tz_name = request.env.context.get('tz') or request.env.user.tz
                            if tz_name:
                                user_dt_tz = pytz.timezone(tz_name).localize(delv_time, is_dst=False).astimezone(
                                    pytz.timezone('UTC')).replace(tzinfo=None)  # UTC = no DST
                                pos_delivery_order.write({'display_delivery_time': user_dt_tz})

                            ########################################################

                        prod_lst = post['product_lst']
                        for i in prod_lst:
                            for j in i:
                                pos_delivery_order.write({
                                    'lines': [(0, 0, {
                                        'product_id': i['id'],
                                        'qty': i['qty'],
                                        'price_unit': i['price_unit'], })]
                                })
                                break
                        return True

                elif not delivery_lst['ship_to_diff_addr'] == True:
                    del delivery_lst['ship_to_diff_addr']
                    partner = request.env['res.partner'].sudo().search([('id', '=', int(delivery_lst['partner_id']))])
                    delivery_lst['street'] = partner.street or ''
                    delivery_lst['street2'] = partner.street2 or ''
                    delivery_lst['city'] = partner.city or ''
                    delivery_lst['zip'] = partner.zip or ''
                    if partner.state_id:
                        delivery_lst['state_id'] = partner.state_id.id
                    if partner.country_id:
                        delivery_lst['country_id'] = partner.country_id.id
                    if partner.email:
                        delivery_lst['email'] = partner.email
                    if partner.phone:
                        delivery_lst['phone'] = partner.phone

                    if 'delivery_time' in post and 'display_delivery_time' in post:
                        delivery_lst['display_delivery_time'] = delivery_lst['display_delivery_time'].replace('T', " ")
                        delivery_lst['delivery_time'] = delivery_lst['delivery_time'].replace('T', " ")

                    if post.get('session_id'):
                        session_id = request.env['pos.session'].sudo().search(
                        [('id', '=', post.get('session_id'))])

                        if session_id.config_id and session_id.config_id.picking_type_id and session_id.config_id.picking_type_id.warehouse_id:
                            delivery_lst['warehouse_id'] = session_id.config_id.picking_type_id.warehouse_id.id

                    pos_delivery_order = request.env['picking.order'].sudo().create(delivery_lst)

                    # code for converting delivery time from utc to user timezone
                    if 'delivery_time' in post:
                        delv_time_format = pos_delivery_order.display_delivery_time.strftime(DATETIME_FORMAT)
                        delv_time = datetime.strptime(delv_time_format, DATETIME_FORMAT)
                        tz_name = request.env.context.get('tz') or request.env.user.tz
                        if tz_name:
                            user_dt_tz = pytz.timezone(tz_name).localize(delv_time,is_dst=False).astimezone(pytz.timezone('UTC')).replace(tzinfo=None)  # UTC = no DST
                            pos_delivery_order.write({'display_delivery_time':user_dt_tz})
                        ########################################################

                    prod_lst = post['product_lst']
                    for i in prod_lst:
                        for j in i:
                            pos_delivery_order.write({
                                'lines': [(0, 0, {
                                    'product_id': i['id'],
                                    'qty':i['qty'],
                                    'price_unit': i['price_unit'], })]
                                })
                            break
                    return True

            else:
                return "already created"
        else:
            return False


class HomeDeliveryControl(http.Controller):

    @http.route('/page/pos-order-view/<order>', type='http', auth='public', website=True, csrf=False)
    def get_pos_order_details(self, order=None, mobilepreview=None):
        do = http.request.env['picking.order'].sudo()  # pos delivery orders
        pos_delivery_order = do.sudo().search([('name', '=', order)])
        pos = http.request.env['pos.order'].sudo()  # pos delivery orders
        pos_order = pos.sudo().search([('pos_reference', '=', order)], limit=1)
        # order_driver_msg = http.request.env['order.driver.message'].sudo().search(
        #     [('order_id', '=', sale_order.id)])
        api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])
        if len(api_key) == 1:
            maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"
        else:
            maps_url = "//maps.google.com/maps/api/js?key=&amp;libraries=places&amp;language=en-AU"
        values = {
            # 'maps_script_url': maps_url,
            'order': pos_order,
            'longitude': pos_delivery_order.pos_partner_id.partner_longitude,
            'latitude': pos_delivery_order.pos_partner_id.partner_latitude,
            'driver_longitude': pos_delivery_order.warehouse_id.partner_id.partner_longitude,
            'driver_latitude': pos_delivery_order.warehouse_id.partner_id.partner_latitude
        }
        return request.render('home_delivery_odoo_pos_website_mobile_pragtech.pos-order-view', values)

    @http.route('/page/job_list/pos-order-view/<order>', type='http', auth='public', website=True, csrf=False)
    def get_job_list_pos_order_details(self, order=None, mobilepreview=None):
        pos = http.request.env['pos.order'].sudo()
        pos_order = pos.search([('pos_reference', '=', order)], limit=1)
        # order_driver_msg = http.request.env['order.driver.message'].sudo().search(
        #     [('order_id', '=', sale_order.id)])
        # pos_delivery_order = http.request.env['picking.order'].sudo().search([('name', '=', order)], limit=1)
        pos_delivery_order = pos_order.pos_delivery_order_ref
        api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])
        if len(api_key) == 1:
            maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"
        else:
            maps_url = "//maps.google.com/maps/api/js?key=&amp;libraries=places&amp;language=en-AU"

        values = {
            # 'maps_script_url': maps_url,
            'pos_order': pos_order,
            'pos_delivery_order': pos_delivery_order,
            'delivery_order_payment_status': pos_delivery_order.payment_status,
            'longitude': pos_delivery_order.pos_partner_id.partner_longitude,
            'latitude': pos_delivery_order.pos_partner_id.partner_latitude,
            'driver_longitude': pos_delivery_order.warehouse_id.partner_id.partner_longitude,
            'driver_latitude': pos_delivery_order.warehouse_id.partner_id.partner_latitude,
            'driver_mobile': pos_delivery_order.delivery_boy.mobile,
            'driver_note': pos_delivery_order.order_note
        }
        return request.render('home_delivery_odoo_pos_website_mobile_pragtech.pos-order-view-driver', values)

    @http.route('/delivered/pos_order', type='http', auth='public', website=True, csrf=False)
    def delivered_pos_order_driver(self, **post):
        order_id = post.get('order_id')
        pos_delivery_order = http.request.env['picking.order'].sudo().search([('name', '=', order_id)])
        if pos_delivery_order:
            pos_delivery_order.write({'state': 'delivered'})
            return json.dumps({'status': 'true'})

    @http.route('/cancel/posorder', type='http', auth='public', website=True, csrf=False)
    def cancel_pos_order(self, **post):
        order_id = post.get('order_id')
        pos_order = http.request.env['pos.order'].sudo().search([('pos_reference', '=', order_id)], limit=1)
        pos_delivery_order = http.request.env['picking.order'].sudo().search([('name', '=', order_id)], limit=1)
        if pos_order and pos_delivery_order:
            pos_order.action_pos_order_cancel()
            pos_delivery_order.write({'state': 'canceled'})
            _logger.info(("Sale order %s has been cancelled from delivery control panel." % (pos_order.name)))
            return json.dumps({'status': 'true'})

    @http.route('/collect-payment-pos', type='http', auth='public', website=True, csrf=False)
    def collect_payment_pos(self, **post):
        if post.get('order_id') and post.get('order_source') == "POS":
            pos_delivery_order = http.request.env['picking.order'].sudo().search(
                [('name', '=', post.get('order_id'))], limit=1)
            if pos_delivery_order:
                pos_delivery_order.write(
                    {'payment_status_with_driver': True})
        return json.dumps({})

    @http.route('/driver/cancel/pos_order', type='http', auth='public', website=True, csrf=False)
    def driver_cancel_pos_order(self, **post):
        order_id = post.get('order_id')
        pos_delivery_order = request.env['picking.order'].sudo().search([('name', '=', order_id)],limit=1)
        pos_order = request.env['pos.order'].sudo().search([('pos_reference', '=', order_id)], limit=1)
        if pos_order and pos_delivery_order:
            pos_order.action_pos_order_cancel()
            pos_delivery_order.write({'state': 'canceled'})
            _logger.info(("Sale order %s has been cancelled from delivery control panel." % (pos_order.name)))
            return json.dumps({'status': 'true'})

    @http.route('/select/payment/pos/status', type='http', auth='public', website=True, csrf=False)
    def customer_payment_status_pos(self, **post):
        order_no = post.get('order_number')
        # pos_order = request.env['pos.order'].sudo().search([('pos_reference','=',order_no)])
        pos_delivery_order = request.env['picking.order'].sudo().search([('name', '=', order_no)])
        if post.get('selectedValue') == 'cash_on_delivery':
            pos_delivery_order.write({'payment_status': 'Cash On Delivery'})
        elif post.get('selectedValue') == 'prepaid':
            pos_delivery_order.write({'payment_status': 'Prepaid'})
        return json.dumps({})

    @http.route('/paid/pos_order/status', type='http', auth='public', website=True, csrf=False)
    def pos_order_paid_status(self, **post):
        try:
            if post.get('payment_status') == 'PAID':
                order_no = post.get('order_number')
                pos_delivery_order = request.env['picking.order'].search([('name', '=', order_no)],limit=1)
                pos_order = request.env['pos.order'].search([('pos_reference', '=', order_no)])
                if pos_order and pos_delivery_order:
                    if pos_order.payment_ids:
                        if not pos_delivery_order.bank_statement_ids:
                            for i in pos_order.payment_ids:
                                if i.name and 'return' not in i.name:
                                    i.write({'name': pos_order.name + ': Home Delivery'})
                                elif not i.name:
                                    i.write({'name': pos_order.name + ': Home Delivery'})

                            pos_delivery_order.write({'bank_statement_ids': [(6, 0, pos_order.payment_ids.ids)],
                                                      'state': 'paid',
                                                      'pos_order_id': pos_order.id,
                                                      'order_ref': pos_order.name})
            return json.dumps({})
        except:
            return False


class WebsiteDeliveryControlAppInherit(WebsiteCustomer):

    @http.route([
        '/page/manage/delivery',
        '/page/manage/delivery/page/<int:page>',
    ], type='http', auth="public", website=True)
    def manage_sale_order_delivery(self, page=0, search='', opg=False, domain=None, **post):
        # res_super = super(WebsiteDeliveryControlAppInherit, self).manage_sale_order_delivery(page,search, opg, domain, **post)
        if domain is None:
            domain = []
        if opg:
            try:
                opg = int(opg)
            except ValueError:
                opg = OPG
            post["ppg"] = opg
        else:
            opg = OPG

        so = request.env['sale.order'].sudo()
        do = request.env['picking.order'].sudo()  # pos delivery order
        pos = request.env['pos.order'].sudo() # pos order
        usr = request.env['res.users'].sudo().browse(request.uid)

        domain.append(('state', '=', 'sale'))
        so_count = so.search_count(domain)

        url = "/page/manage/delivery"
        # do_count = do.search_count([('state', '=', 'draft')])
        pos_count = pos.search_count([('state', '=', 'paid')])
        total_count = pos_count + so_count
        pager = request.website.pager(url=url, total=total_count, page=page, step=opg, scope=7, url_args=post)
        sale_orders = so.search(domain, limit=opg, offset=pager['offset'], order="id desc")
        pos_orders = pos.search([('state', '=', 'paid'),('pos_delivery_order_ref','!=',False)], limit=opg, offset=pager['offset'], order="id desc")
        # pos_delivery_orders = do.search([('state', '=', 'draft')], limit=opg, offset=pager['offset'], order="id desc")

        warehouses = http.request.env['stock.warehouse'].sudo().search_read(domain=[], fields=['name'])

        values = {
            'pager': pager,
            'search_count': total_count,  # common for all searchbox
            # 'pos_delivery_orders': pos_delivery_orders,
            'pos_orders': pos_orders,
            'sale_orders': sale_orders,
            'warehouses': warehouses,
            'wh_id': usr.warehouse_id.id
        }

        return request.render("pragmatic_delivery_control_app.manage_sale_order_delivery", values)



class WebsiteDeliveryControlAppInherit(WebsiteCustomerDriver):

    @http.route('/update_pickings', type='http', auth='public', website=True, csrf=False)
    def update_pickings(self, **post):
        res_users = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)])
        res_partner = request.env['res.partner'].sudo().search([('id', '=', res_users.partner_id.id)])

        if post.get('pickings') or post.get('pos_orders'):
            pickings = ast.literal_eval(post.get('pickings'))
            pos_orders_ids = ast.literal_eval(post.get('pos_orders'))

            picking_id = http.request.env['picking.order'].sudo().search([('id', 'in', pickings)])
            # picking_id = http.request.env['pos.order'].sudo().search([('id', 'in', pos_orders_ids)])

            purchase_order_obj = request.env['purchase.order']
            purchase_order_line_obj = request.env['purchase.order.line']

            po_id = purchase_order_obj.sudo().create({
                'partner_id': res_partner.id,
            })

            uom_id = request.env['uom.uom'].sudo().search([('name', '=', 'Units')])

            purchase_order_line_obj.sudo().create({
                'product_id': request.env.user.company_id.company_delivery_product.id,
                'name': "Total Distance Travelled {} KM".format(int(post.get('total_distance')) / 1000),
                'product_qty': 1,
                'product_uom': uom_id.id,
                'price_unit': int(post.get('total_distance')) * res_partner.drive_rate / 1000,
                'date_planned': datetime.now(),
                'order_id': po_id.id,
            })


        # for rec in picking_id:
        #     rec.action_picking_order_delivered()
        return json.dumps({})

    @http.route('/update-current-driver-location', type='http', auth='public', website=True)
    def update_current_drivers_live_location(self, **post):
        lat=''
        lng=''
        if request.env.user._is_public():
            return request.render("pragmatic_odoo_delivery_boy.logged_in_template")

        else:
            # api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])
            # url = "https://www.googleapis.com/geolocation/v1/geolocate?key="+api_key.value
            #
            # payload = {}
            # headers = {
            #     'Content-Type': 'application/json'
            # }
            #
            # response = requests.request("POST", url, headers=headers, data=payload)
            # print('Google API   ',response.json())
            #
            # if response.status_code==200:
            #     post = response.json()
            #     post=post.get('location')
            res_users = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)])
            res_partner = request.env['res.partner'].sudo().search([('id', '=', res_users.partner_id.id)])
            _logger.info('\n $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$User Object   ' + str(res_partner))
            if post.get('lat') and post.get('lng') and res_partner:
                _logger.info('\n User Name   ' + res_partner.name)
                _logger.info('\n partner_latitude   ' + post.get('lat'))
                _logger.info('\n partner_longitude  ' + post.get('lng'))
                lat =post.get('lat')
                lng = post.get('lng')
                res_partner.write({'partner_latitude':post.get('lat') ,'partner_longitude': post.get('lng')})
                request.env.cr.commit()
            # if response.status_code == 429:
            #     post = response.json()
            #     post = post.get('error')
            #     _logger.info('429 Google API   ' + response.text)
            #     return json.dumps({'message': post.get('message')})

            else:
                _logger.info('Google API   '+ post)

        return json.dumps({'lat': lat,'lng':lng})

    @http.route('/update-driver-location', type='http', auth='public', website=True)
    def update_drivers_live_location(self, **post):

        if request.env.user._is_public():
            return request.render("pragmatic_odoo_delivery_boy.logged_in_template")

        else:
            res_users = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)])
            res_partner = request.env['res.partner'].sudo().search([('id', '=', res_users.partner_id.id)])

            picking_orders = request.env['picking.order'].sudo().search([('state', 'in', ['assigned', 'accept']),
                                                                         ('delivery_boy', '=', res_partner.id),
                                                                         ('state', '!=', 'delivered'),
                                                                         ('state', '!=', 'canceled')])
            sale_orders = picking_orders.mapped('sale_order')
            orders = request.env['sale.order'].sudo().search([('id', 'in', sale_orders.ids)],
                                                             order='distance_btn_2_loc asc')

            # warehouse_driver = request.env['stock.warehouse.driver'].sudo().search([('driver_id', '=', res_partner.id)])
            routes = [[res_partner.partner_latitude,
                       res_partner.partner_longitude]]
            api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])

            if len(api_key) == 1:
                maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"

            if post.get('lat') and post.get('lng'):
                routes = [[float(post.get('lat')), float(post.get('lng'))]]
            arr_warehouse=[]
            for rec in orders:
                if rec.warehouse_id:
                    arr_warehouse.append(rec.warehouse_id.id)
                routes.append([rec.partner_shipping_id.partner_latitude, rec.partner_shipping_id.partner_longitude, rec.name])
            pos_delivery_orders = request.env['picking.order'].search([('state', 'in', ['assigned', 'accept', 'in_progress', ]),
                                                                       ('delivery_boy', '=', res_partner.id),
                                                                       ('state', 'not in', ['delivered', 'paid', 'canceled']),
                                                                       ]).ids
            if pos_delivery_orders or picking_orders:
                pos_orders = request.env['pos.order'].search(
                    [('state', '=', 'paid'), ('pos_delivery_order_ref', 'in', pos_delivery_orders)])
                for pos_orders_id in pos_orders:
                    routes.append([pos_orders_id.pos_delivery_order_ref.pos_partner_id.partner_latitude,
                                   pos_orders_id.pos_delivery_order_ref.pos_partner_id.partner_longitude, pos_orders_id.pos_delivery_order_ref.name])

            arr_warehouse = list(set(arr_warehouse))
            warehouse_loc = request.env['stock.warehouse'].sudo().search([('id', 'in', arr_warehouse)])
            if warehouse_loc:
                for warehouse in warehouse_loc:
                    routes.append([warehouse.partner_id.partner_latitude,
                                   warehouse.partner_id.partner_longitude, str('Warehouse : ' + warehouse.name)])

        return json.dumps({'routes': routes})
        return json.dumps({})

    @http.route('/page/route/map', type='http', auth='public', website=True)
    def route_map(self, page=0, search='', opg=False, domain=None, **kwargs):
        if request.env.user._is_public():
            return request.render("pragmatic_odoo_delivery_boy.logged_in_template")

        else:
            res_users = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)])
            res_partner = request.env['res.partner'].sudo().search([('id', '=', res_users.partner_id.id)])
            picking_orders = request.env['picking.order'].sudo().search([('state', 'in', ['assigned', 'accept']),
                                                                         ('delivery_boy', '=', res_partner.id),
                                                                         ('state', '!=', 'delivered'),
                                                                         ('state', '!=', 'canceled')])
            sale_orders = picking_orders.mapped('sale_order')
            orders = request.env['sale.order'].sudo().search([('id', 'in', sale_orders.ids)],
                                                             order='distance_btn_2_loc asc')
            # warehouse_driver = request.env['stock.warehouse.driver'].sudo().search([('driver_id', '=', res_partner.id)])

            routes = [[res_partner.partner_latitude, res_partner.partner_longitude]]

            api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])

            if len(api_key) == 1:
                maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"
            arr_warehouse=[]
            for rec in orders:
                if rec.warehouse_id:
                    arr_warehouse.append(rec.warehouse_id.id)
                routes.append([rec.partner_shipping_id.partner_latitude, rec.partner_shipping_id.partner_longitude, rec.name])

            pos_delivery_orders = request.env['picking.order'].search([('state', 'in', ['assigned', 'accept', 'in_progress']),
                                                                       ('delivery_boy', '=', res_partner.id),
                                                                       ]).ids

            arr_warehouse = list(set(arr_warehouse))
            warehouse_loc = request.env['stock.warehouse'].sudo().search([('id', 'in', arr_warehouse)])
            if warehouse_loc:
                for warehouse in warehouse_loc:
                    routes.append([warehouse.partner_id.partner_latitude,
                                   warehouse.partner_id.partner_longitude, str('Warehouse : ' + warehouse.name)])

            if pos_delivery_orders or picking_orders:
                pos_orders = request.env['pos.order'].search(
                    [('state', '=', 'paid'), ('pos_delivery_order_ref', 'in', pos_delivery_orders)])
                for pos_orders_id in pos_orders:
                    routes.append([pos_orders_id.pos_delivery_order_ref.pos_partner_id.partner_latitude,
                                   pos_orders_id.pos_delivery_order_ref.pos_partner_id.partner_longitude, pos_orders_id.pos_delivery_order_ref.name])


                if picking_orders.ids or pos_orders:
                    return request.render("pragmatic_delivery_control_app.route-map-view-driver", {
                        # 'maps_script_url': maps_url,
                        'picking_ids': picking_orders.ids,
                        'pos_orders': pos_orders.ids,

                        'routes': json.dumps(routes),

                    })

                else:
                    return request.render("pragmatic_delivery_control_app.route-map-view-driver", {
                        # 'maps_script_url': maps_url,
                    })
        return request.render("pragmatic_delivery_control_app.route-map-view", {
            # 'maps_script_url': maps_url,
        })

    @http.route('/admin/delivery/routes/details/<driver_id>', type='http', auth='public', website=True, csrf=False)
    def admin_delivery_routes_details(self, order=None, **kwargs):
        res_partner = request.env['res.partner'].sudo().search([('id', '=', kwargs.get('driver_id'))])
        picking_orders = request.env['picking.order'].sudo().search([('state', 'in', ['assigned', 'accept','paid']),
                                                                     ('delivery_boy', '=', res_partner.id),
                                                                     ])
        pos_delivery_orders = request.env['picking.order'].search([('state', 'in', ['assigned', 'accept', 'in_progress']),
                                                                   ('delivery_boy', '=', res_partner.id)
                                                                   ]).ids
        sale_orders = picking_orders.mapped('sale_order')
        orders = request.env['sale.order'].sudo().search([('id', 'in', sale_orders.ids)],
                                                         order='distance_btn_2_loc asc')

        api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])

        if len(api_key) == 1:
            maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"
            # maps_url = "//maps.googleapis.com/maps/api/js?key=" + api_key.value + "&callback=initMap"

        routes = []
        # warehouse_driver = request.env['stock.warehouse.driver'].sudo().search([('driver_id', '=', res_partner.id)])
        routes = [[res_partner.partner_latitude, res_partner.partner_longitude]]
        arr_warehouse = []
        for rec in orders:
            if rec.warehouse_id:
                arr_warehouse.append(rec.warehouse_id.id)
            routes.append([rec.partner_id.partner_latitude, rec.partner_id.partner_longitude, rec.name, rec.partner_id.zip])
        arr_warehouse = list(set(arr_warehouse))
        warehouse_loc = request.env['stock.warehouse'].sudo().search([('id','in',arr_warehouse)])

        if warehouse_loc:
            for warehouse in warehouse_loc:
                routes.append([warehouse.partner_id.partner_latitude,
                               warehouse.partner_id.partner_longitude, str('Warehouse : ' + warehouse.name)])

        if picking_orders.ids or pos_delivery_orders:
            pos_orders = request.env['pos.order'].search(
                [('state', '=', 'paid'), ('pos_delivery_order_ref', 'in', pos_delivery_orders)])
            for pos_orders_id in pos_orders:
                routes.append([pos_orders_id.pos_delivery_order_ref.pos_partner_id.partner_latitude,
                               pos_orders_id.pos_delivery_order_ref.pos_partner_id.partner_longitude, pos_orders_id.pos_delivery_order_ref.name])


            return request.render("pragmatic_delivery_control_app.route-map-view", {
                # 'maps_script_url': maps_url,
                'picking_ids': picking_orders.ids,
                'pos_orders': pos_orders.ids,
                'routes': json.dumps(routes)
            })

        else:
            return request.render("pragmatic_delivery_control_app.route-map-view", {
                # 'maps_script_url': maps_url,
            })

    @http.route('/page/job/list/driver', type='http', auth='public', website=True)
    def job_list_website(self, page=0, search='', opg=False, domain=None, **kwargs):
        values = {}
        if request.env.user._is_public():
            return request.render("pragmatic_odoo_delivery_boy.logged_in_template")
        else:
            res_users = request.env['res.users'].search([('id', '=', request.env.user.id)])
            res_partner = request.env['res.partner'].search([('id', '=', res_users.partner_id.id)])
            picking_orders = request.env['picking.order'].search(
                [('state', 'in', ['assigned', 'accept', 'in_progress', 'paid']), ('delivery_boy', '=', res_partner.id)],
                order='distance_btn_2_loc asc'
            )
            pos_orders = request.env['pos.order'].search([('state', '=', 'paid'), ('pos_delivery_order_ref', 'in', picking_orders.ids)])
            # warehouse_driver = request.env['stock.warehouse.driver'].sudo().search([('driver_id', '=', res_partner.id)])
            routes = []
            if res_partner:
                routes.append([res_partner.partner_latitude,
                               res_partner.partner_longitude])

            api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])

            if len(api_key) == 1:
                maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"
            for picking in picking_orders:
                if all([picking.sale_order, picking.sale_order.invoice_ids, not picking.invoice]):
                    picking.update({'invoice': picking.sale_order.invoice_ids[0], 'payment': 'paid'})
                if picking.sale_order.partner_shipping_id:
                    routes.append([picking.sale_order.partner_shipping_id.partner_latitude, picking.sale_order.partner_shipping_id.partner_longitude])
            for pos_order in pos_orders:
                routes.append([pos_order.pos_delivery_order_ref.pos_partner_id.partner_latitude,
                               pos_order.pos_delivery_order_ref.pos_partner_id.partner_longitude])
            # warehouse_loc = request.env['stock.warehouse'].sudo().search([])
            #
            # if warehouse_loc:
            #     for warehouse in warehouse_loc:
            #         routes.append([warehouse.partner_id.partner_latitude,
            #                        warehouse.partner_id.partner_longitude, str('Warehouse : ' + warehouse.name)])

            if picking_orders:
                    return request.render("pragmatic_odoo_delivery_boy.manage_job_list", {
                        # 'maps_script_url': maps_url,
                        'picking_ids': picking_orders.ids,
                        'routes': routes,
                        'picking_orders': picking_orders,
                        'delivery_boy': res_partner,
                        'pos_orders': pos_orders,
                        'pos_ids': pos_orders.ids
                    })
            else:
                return request.render("pragmatic_odoo_delivery_boy.manage_job_list", {
                    # 'maps_script_url': maps_url,
                    'delivery_boy': res_partner,
                })

    @http.route('/page/job/list/customer', type='http', auth='public', website=True)
    def job_list_website_customer(self, page=0, search='', opg=False, domain=None, **kwargs):
        if request.env.user._is_public():
            return request.render("pragmatic_odoo_delivery_boy.logged_in_template")
        else:
            res_users = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)])
            res_partner = request.env['res.partner'].sudo().search([('id', '=', res_users.partner_id.id)])

            picking_orders = request.env['picking.order'].sudo().search(
                [('partner_id', '=', res_partner.id)],
                order='distance_btn_2_loc asc')

            pos_orders = request.env['pos.order'].sudo().search([('partner_id', '=', res_partner.id)])

            # sale_orders = picking_orders.mapped('sale_order')
            # orders = request.env['sale.order'].sudo().search([('id', 'in', sale_orders.ids)],
            #                                                  order='distance_btn_2_loc asc')

            # warehouse_driver = request.env['stock.warehouse.driver'].sudo().search([('driver_id', '=', res_partner.id)])
            # routes = [[warehouse_driver[0].warehouse_id.partner_id.partner_latitude, warehouse_driver[0].warehouse_id.partner_id.partner_longitude]]

            # api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])

            # if len(api_key) == 1:
            #     maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"

            # for rec in orders:
            #     if rec.invoice_ids:
            #         picking_order = request.env['picking.order'].search([('sale_order', '=', rec.id)])
            #         for pic in picking_order:
            #             pic.invoice = rec.invoice_ids[0]
            #             pic.payment = 'paid'
            #     routes.append([rec.partner_shipping_id.partner_latitude, rec.partner_shipping_id.partner_longitude])
            #
            # routes.append([warehouse_driver[0].warehouse_id.partner_id.partner_latitude,
            #                warehouse_driver[0].warehouse_id.partner_id.partner_longitude])

            if picking_orders.ids or pos_orders:
                return request.render("pragmatic_odoo_delivery_boy.manage_job_list_customer", {
                    # 'maps_script_url': maps_url,
                    'picking_ids': picking_orders.ids,
                    'pos_order_ids': pos_orders.ids,
                    # 'routes': routes,
                    'picking_orders': picking_orders,
                    'pos_orders': pos_orders,
                    'delivery_boy': res_partner,
                })

            else:
                return request.render("pragmatic_odoo_delivery_boy.manage_job_list_customer", {
                    # 'maps_script_url': maps_url,
                    'delivery_boy': res_partner,
                })

    @http.route('/pos/delivery/route/order-view/<order_id>', type='http', auth='public', website=True, csrf=False)
    def pos_customer_delivery_routes(self, order=None, **kwargs):
        # orders = request.env['sale.order'].sudo().search([('id', '=', kwargs.get('order_id'))],
        #                                                  order='distance_btn_2_loc asc')
        # picking_orders = request.env['picking.order'].sudo().search([('sale_order', '=', orders.id),
        #                                                              ])
        pos_orders = request.env['picking.order'].sudo().search([('name', '=', kwargs.get('order_id'))])

        api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])

        if len(api_key) == 1:
            maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"
        routes = []

        # if picking_orders:
        #     routes = [[picking_orders.delivery_boy.partner_latitude, picking_orders.delivery_boy.partner_longitude]]

        if pos_orders:
            routes = [[pos_orders.delivery_boy.partner_latitude, pos_orders.delivery_boy.partner_longitude]]
        # for rec in orders:
        routes.append([pos_orders.pos_partner_id.partner_latitude, pos_orders.pos_partner_id.partner_longitude, pos_orders.name, pos_orders.partner_id.zip])

        if pos_orders.ids:
            return request.render("pragmatic_odoo_delivery_boy.route-map-customer-view", {
                # 'maps_script_url': maps_url,
                'pos_order_ids': pos_orders.ids,
                # 'picking_ids': orders.ids,
                'routes': json.dumps(routes)
            })

        else:
            return request.render("pragmatic_odoo_delivery_boy.route-map-customer-view", {
                'maps_script_url': maps_url,
            })

    @http.route('/pos/order/driver_accept_reject_status', type='http', auth='public', website=True, csrf=False)
    def pos_order_accept_reject_status_by_driver(self, **post):
        order_no = post.get('order_number')
        pos_delivery_order = http.request.env['picking.order'].sudo().search([('name', '=', order_no)])
        # picking_order = request.env['picking.order'].sudo().search([('sale_order', '=', sale_order.id)])
        if post.get('delivery_order_status') == 'accept':
            pos_delivery_order.write({'state': 'accept'})
            pos_delivery_order.message_post(body="Delivery Order Accepted By {}".format(pos_delivery_order.delivery_boy.name), type='comment')
            return json.dumps({'status': True})
        elif post.get('delivery_order_status') == 'reject':
            pos_delivery_order.message_post(body="Delivery Order Rejected By {}".format(pos_delivery_order.delivery_boy.name), type='comment')
            # picking_order.write({'state': 'created', 'delivery_boy': False})
            # sale_order.write({'delivery_state': 'ready'})
            return json.dumps({'status': False})

    @http.route('/pos/delivered/order', type='http', auth='public', website=True, csrf=False)
    def pos_delivered_order_driver(self, **post):
        order_id = post.get('order_id')
        pos_delivery_order = http.request.env['picking.order'].sudo().search([('id', '=', (int(order_id)))])
        # picking = http.request.env['picking.order']
        # pos_delivery_order.write({'state': 'paid'})
        pos_delivery_order.write({'state': 'delivered'})
        Param = http.request.env['res.config.settings'].sudo().get_values()

        if Param.get('whatsapp_instance_id') and Param.get('whatsapp_token'):
            if pos_delivery_order.pos_partner_id.country_id.phone_code and pos_delivery_order.pos_partner_id.mobile:
                url = 'https://api.chat-api.com/instance' + Param.get('whatsapp_instance_id') + '/sendMessage?token=' + Param.get('whatsapp_token')
                headers = {
                    "Content-Type": "application/json",
                }
                whatsapp_msg_number = pos_delivery_order.pos_partner_id.mobile
                whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "");
                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(pos_delivery_order.pos_partner_id.country_id.phone_code), "")
                msg = 'Your order has delivered.'
                tmp_dict = {
                    "phone": "+" + str(pos_delivery_order.pos_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                    "body": msg

                }
                response = requests.post(url, json.dumps(tmp_dict), headers=headers)

                if response.status_code == 201 or response.status_code == 200:
                    _logger.info("\nSend Message successfully")
                    mail_message_obj = http.request.env['mail.message']
                    # if self.env['ir.config_parameter'].sudo().get_param('pragmatic_odoo_whatsapp_integration.group_crm_display_chatter_message'):
                    comment = "fa fa-whatsapp"
                    body_html = tools.append_content_to_html('<div class = "%s"></div>' % tools.ustr(comment), msg)
                    # body_msg = self.convert_to_html(body_html)
                    mail_message_id = mail_message_obj.sudo().create({
                        'res_id': pos_delivery_order.id,
                        'model': 'picking.order',
                        'body': body_html,
                    })

        # order.action_picking_order_delivered()
        # order = http.request.env['sale.order'].sudo().browse(int(order_id))
        # order.action_delivered_sale_order()
        # _logger.info(
        #     _("Sale order %s has been cancelled from delivery control panel." % (order.name)))
        return json.dumps({'state': 'true'})

    @http.route('/pos/driver/issue/message', type='http', auth='public', website=True, csrf=False)
    def pos_driver_issue_message(self, **post):
        # picking_order = request.env['picking.order'].search([('id', '=', post.get('picking_order'))])
        pos_delivery_order = http.request.env['picking.order'].sudo().search([('id', '=', post.get('pos_delivery_number'))])

        message = post.get('driver_message')

        pos_delivery_order.message_post(body="{} - {}".format(message, pos_delivery_order.delivery_boy.name),
                                   type='comment')

        pos_delivery_order.state = 'assigned'
        # pos_delivery_order.delivery_boy.name = False

        return json.dumps({})

    @http.route('/change_delivery_boy_status', type='http', auth='public', website=True, csrf=False)
    def change_delivery_boy_status(self, **post):
        delivery_boy = post.get('delivery_boy')  # Res Partner
        delivery_boy_status = post.get('delivery_boy_status')
        picking_orders = request.env['picking.order'].sudo().search([('delivery_boy', '=', int(delivery_boy))])
        # pos_delivery_orders = http.request.env['picking.order'].sudo().search([('delivery_boy', '=', int(delivery_boy))])


        if delivery_boy and delivery_boy_status:
            # warehouse_driver = request.env['stock.warehouse.driver'].search([('driver_id', '=', int(delivery_boy))])
            res_partner = request.env['res.partner'].search([('id', '=', int(delivery_boy))])
            if delivery_boy_status.lower() == 'available' and res_partner :
                res_partner.write({'status': 'not_available'})
                # warehouse_driver.write({'status': 'not_available'})
                for picking in picking_orders:
                    if picking.state != 'accept':
                        if picking.order_source == 'sale':
                            picking.sale_order.write({'delivery_state': 'ready'})
                        picking.write({'state': 'created', 'delivery_boy': False})
                        picking.message_post(
                            body="Delivery Order Rejected By {}. Delivery Boy not available".format(picking.delivery_boy.name),
                            type='comment')
                return json.dumps({"driver_status": 'Not Available', 'status_changed': True})

            elif delivery_boy_status.lower() == 'not available' and res_partner :
                res_partner.write({'status': 'available'})
                # warehouse_driver.write({'status': 'available'})
                return json.dumps({"driver_status": 'Available', 'status_changed': True})

            else:
                return json.dumps({'status_changed': False})
