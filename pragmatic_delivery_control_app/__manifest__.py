{
    'name': 'Odoo Home Delivery Control System For Any Business',
    'version': '13.0.6',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'category': 'Website',
    'summary': 'Delivery Control System odoo restaurants delivery control system restaurant management system restaurant management software restaurant management app',
    'description': """
Delivery Control System
========================
Delivery Control System is an online system which allows the delivery manager to process the sale orders. 
It's feature includes assign a delivery control guy, collect payment from the guy, handle any delivery related issues etc.

<keywords>
Odoo - Restaurants Delivery Control System
restaurant management system
restaurants
odoo restaurant
restaurant management
restaurant management software
restaurant management app    
    """,
    'depends': ['website_sale', 'stock', 'base_geolocalize', 'sale_management', 'delivery', 'purchase', 'portal'],
    'data': [
        'data/website_menus.xml',
        'data/res_groups.xml',
        'security/ir.model.access.csv',
        'views/website_menu_views.xml',
        'views/res_users_views.xml',
        'views/res_company_view.xml',
        'views/sale_views.xml',
        'views/templates.xml',
        'views/delivery_control_panel.xml',
        'views/order_details.xml',
        'views/portal_templates.xml',
        'views/ir_cron.xml',
        'views/route_map.xml',
        'views/stock_views.xml',
        'views/route-map-view-driver.xml',
    ],
    'images': ['static/description/home-delivery-control-system-for-any-business-gif.gif'],
    'currency': 'USD',
    'license': 'OPL-1',
    'price': 399.00,
    'installable': True,
    'application': False,
    'auto_install': False,
}
