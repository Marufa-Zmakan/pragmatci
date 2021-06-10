# -*- coding: utf-8 -*-

from math import radians, cos, sin, asin, sqrt
import logging
import googlemaps
import pprint

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    @staticmethod
    def _find_distance(lat1, long1, lat2, long2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
        # haversine formula
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        km = 6371 * c
        return km

    def find_nearest_store111(self, lat, long):
        """
        Find nearest store from client delivery address.
        :param lat (Float): customer latitude
        :param long (Float): customer longitude
        :return stock.warehouse: warehouse instance
        """
        warehouses = self.env['stock.warehouse'].sudo().search([('company_id','=',self.company_id.id)])
        min_dist = 1000
        warehouse_id = None
        for warehouse in warehouses:
            partner = warehouse.partner_id
            dist = self._find_distance(lat, long, partner.partner_latitude, partner.partner_longitude)
            _logger.info("Customer is away {} Km from {}.".format(dist, partner.name))
            if dist < min_dist:
                warehouse_id = warehouse.id
                min_dist = dist
        return warehouse_id

    def calculate_distance_matrix(self, origin, destinations):
        apikey = self.get_google_map_api_key()
        gmaps = googlemaps.Client(key=apikey)
        distance = gmaps.distance_matrix(origin, destinations)
        _logger.info('Distance Matrix result: \n%s', pprint.pformat(distance))
        if distance["status"] != 'OK':
            msg = "Something went wrong with googlemaps api."
            errmsg = distance["error_message"] if "error_message" in distance else msg
            raise ValidationError(_(errmsg))
        try:
            return distance["rows"][0]["elements"]
        except Exception as e:
            raise ValidationError(_("Invalid response return from googlemap distance matrix api."))

    def get_store_addresses(self):
        destinations = []
        warehouse_ids = []
        warehouses = self.env['stock.warehouse'].sudo().search([('company_id','=',self.company_id.id)])
        for warehouse in warehouses:
            partner = warehouse.partner_id
            if partner:
                store_addrs = partner.get_address_str()
                if not store_addrs:
                    _logger.warning("{} address components are missing.".format(warehouse.name))
                else:
                    destinations.append(store_addrs)
                    warehouse_ids.append(warehouse.id)
            else:
                _logger.warning("{} address is missing.".format(warehouse.name))
        return destinations, warehouse_ids

    def find_nearest_store(self, address):
        """
        Find nearest store from client delivery address.
        :param address (Char): customer address in string format
        :return stock.warehouse: warehouse instance
        """
        origin = address
        destinations, warehouse_ids = self.get_store_addresses()
        warehouse_id = None
        if origin and destinations:
            result = self.calculate_distance_matrix(origin, destinations)
            min_dist = 500000  # Assuming that possible largest distance between 2 stores cloud not be more than 500km
            for data in zip(warehouse_ids, result):
                _logger.info('Distance data: \n%s', pprint.pformat(data))
                if data[1]['status'] == 'OK' and data[1]['distance']['value'] < min_dist:
                    min_dist = data[1]['distance']['value']
                    warehouse_id = data[0]
        return warehouse_id

    # def _prepare_sale_order_values(self, partner, pricelist):
    #     self.ensure_one()
    #     values = super(Website, self)._prepare_sale_order_values(partner, pricelist)
    #     Partner = self.env['res.partner'].sudo()
    #     shipping_addr = Partner.browse(values["partner_shipping_id"])
    #     warehouse_id = self.find_nearest_store(shipping_addr.partner_latitude, shipping_addr.partner_longitude)
    #     if warehouse_id:
    #         values["warehouse_id"] = warehouse_id
    #     return values

    def get_google_map_api_key(self):
        apikey = self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
        if not apikey:
            apikey = self.env['ir.config_parameter'].sudo().get_param('google.api_key_geocode')
            if not apikey:
                raise UserError(_(
                    "Google map API key not configured.\n"
                    "Please reach out to your Admin."
                ))
        return apikey

    def get_gmap_url(self, callback):
        """
        Return google map script url.
        :param callback (String): Javascript function name where we may initialize google map
        :return:
        """
        apikey = self.get_google_map_api_key()
        return "https://maps.googleapis.com/maps/api/js?key={}&amp;callback={}".format(apikey, callback)