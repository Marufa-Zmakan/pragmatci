# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    inventory_availability = fields.Selection([
        ('never', 'Sell regardless of inventory'),
        ('always', 'Show inventory on website and prevent sales if not enough stock'),
        ('always_allow', 'Show inventory on website and allow sales if enough stock at different location'),
        ('threshold', 'Show inventory below a threshold and prevent sales if not enough stock'),
        ('custom', 'Show product-specific notifications'),
    ], string='Inventory Availability', help='Adds an inventory availability status on the web product page.',
        default='never')

class ProductProduct(models.Model):
    _inherit = 'product.product'

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    inventory_availability = fields.Selection([
        ('never', 'Sell regardless of inventory'),
        ('always', 'Show inventory on website and prevent sales if not enough stock'),
        ('threshold', 'Show inventory when below the threshold and prevent sales if not enough stock'),
        ('always_allow', 'Show inventory on website and allow sales if enough stock at different location'),
        ('custom', 'Show product-specific notifications'),
    ], string='Inventory Availability', default='never')