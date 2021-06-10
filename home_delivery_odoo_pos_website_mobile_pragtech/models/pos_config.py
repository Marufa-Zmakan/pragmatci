from odoo import models, fields


class PosConfigInherit(models.Model):
    _inherit = "pos.config"

    home_delivery = fields.Boolean('POS Home Delivery',default=False)

    floor_home_delivery = fields.Boolean('Display Home Delivery Button', default=False)
    floor_parcel = fields.Boolean('Display Parcel Button', default=False)