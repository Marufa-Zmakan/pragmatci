# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_map_view_portal_url(self):
        portal_link = "%s/page/store/map/view?partner=%d" % (self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
                                                             self.partner_shipping_id.id)
        return portal_link

    def mapview_nearest_store(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_map_view_portal_url(),
        }