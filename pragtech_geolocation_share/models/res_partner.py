# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.tools.translate import _
ADDRESS_FIELDS = ('building','street_number','zone','street', 'street2', 'zip', 'city', 'state_id', 'country_id')


class CustomResPartner(models.Model):
    _inherit = 'res.partner'

    building = fields.Char('Building',copy=False,placeholder="Building")
    zone = fields.Char('Zone',copy=False,placeholder="Zone")
    street_number = fields.Char('Street Number',copy=False,placeholder="Street Number")


    @api.model
    def _get_default_address_format(self):
        if self.zone or self.building or self.street_number:
            return "Building No: %(building)s\nStreet no: %(street_number)s\nZone no: %(zone)s\n%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        return "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"


    @api.model
    def _get_address_format(self):
        return self._get_default_address_format()


    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return list(ADDRESS_FIELDS)
