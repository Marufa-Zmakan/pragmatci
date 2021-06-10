# -*- coding: utf-8 -*-
{
    'name': 'Google Maps',
    'version': '13.0.0.2',
    'license': 'AGPL-3',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'category': 'Extra Tools',
    'description': """
Web Google Map and google places autocomplete address form
==========================================================

This module brings two features:
1. Allows user to view all partners addresses on google maps.
2. Enabled google places autocomplete address form into partner
form view, provide autocomplete feature when typing address of partner
""",
    'depends': [
        'base_setup',
        'base_geolocalize',
        'pragmatic_odoo_website_order_display',
        'pragmatic_delivery_control_app'
    ],
    'website': '',
    'data': [
        'data/google_maps_libraries.xml',
        'views/google_places_template.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml'
    ],
    'demo': [],
    'images': ['static/description/thumbnails.png'],
    'qweb': ['static/src/xml/widget_places.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
