# -*- coding: utf-8 -*-

import logging
import json

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    @http.route('/page/store/map/view', type='http', auth='public', website=True)
    def nearest_store_map_view(self, **post):
        Partner = request.env['res.partner'].sudo()
        partner = Partner.browse(int(post.get("partner", 0)))
        warehouses = request.env['stock.warehouse'].sudo().search([])
        stores = list(map(
            lambda warehouse: {"lat": warehouse.partner_id.partner_latitude, "lng": warehouse.partner_id.partner_longitude},
            warehouses
        ))
        # gmap_url = request.website.get_gmap_url("initNearestStoreMap")
        values = {
            # 'gmap_url': gmap_url,
            'cust_addr': json.dumps({"lat": partner.partner_latitude, "lng": partner.partner_longitude} if partner else {}),
            'store_addrs': json.dumps(stores)
        }
        return request.render("pragmatic_nearest_store_delivery.mapview_nearest_store", values)

    def _checkout_form_save(self, mode, checkout, all_values):
        partner_id = super(WebsiteSale, self)._checkout_form_save(mode, checkout, all_values)
        Partner = request.env['res.partner'].sudo()
        partner = Partner.browse(partner_id)
        cust_addrs = partner.get_address_str()
        warehouse_id = request.website.find_nearest_store(cust_addrs)
        if warehouse_id:
            order = request.website.sale_get_order()
            order.warehouse_id = warehouse_id
        return partner_id