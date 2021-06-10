# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortal(CustomerPortal):

    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "partner_latitude", "partner_longitude"]
