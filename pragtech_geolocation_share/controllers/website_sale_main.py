# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        partnerId = int(kw.get('partner_id', -1))
        res = super(WebsiteSale, self).address(**kw)
        if partnerId > 0:
            partnerObj = request.env['res.partner'].sudo().browse(partnerId)
            if 'submitted' not in kw:
                res.qcontext.update({
                    'partner_latitude': partnerObj.partner_latitude,
                    'partner_longitude': partnerObj.partner_longitude,
                })
            else:
                self.updateLatLong(partnerObj, kw)
        return res

    def _checkout_form_save(self, mode, checkout, all_values):

        if all_values.get('building'):
            checkout['building']=all_values.get('building')
        if all_values.get('street_number'):
            checkout['street_number']=all_values.get('street_number')
        if all_values.get('zone'):
            checkout['zone'] = all_values.get('zone')

        res = super(WebsiteSale, self)._checkout_form_save(mode, checkout, all_values)
        partnerId = int(all_values.get('partner_id', -1))
        if partnerId == -1:
            partnerObj = request.env['res.partner'].sudo().browse(res)
            partnerObj.contact_address = partnerObj._display_address()
            if 'submitted' in all_values:
                self.updateLatLong(partnerObj, all_values)
        return res

    def updateLatLong(self, partnerObj, addressArray):
        partnerObj.write({
            'partner_latitude': addressArray.get('partner_latitude', False) or partnerObj.partner_latitude,
            'partner_longitude': addressArray.get('partner_longitude', False) or partnerObj.partner_longitude
        })
        return True
