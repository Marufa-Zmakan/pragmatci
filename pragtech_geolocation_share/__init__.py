
from odoo import api, SUPERUSER_ID
from . import controllers
from . import models

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='13.0':raise Warning('Module support Odoo series 12.0 found {}.'.format(server_serie))

def _auto_configuration(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ir_values_obj = env['ir.config_parameter'].sudo()
    google_maps_api_key = ir_values_obj.get_param('google_maps_api_key')
    if not google_maps_api_key:
        google_maps_api_key = ir_values_obj.set_param('google_maps_api_key', ('AIzaSyDLoYEb_ymP3n5mdC-OZIvdhwFjGHWZbII' or '').strip())