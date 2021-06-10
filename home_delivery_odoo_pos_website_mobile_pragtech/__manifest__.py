{
    'name': 'Home Delivery All in One POS, Website and Mobile Orders for any Business',
    'version': '13.0.11',
    'category': 'Website',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'summary': 'Odoo Home Delivery Control System  Restaurants Delivery Control System restaurant management system restaurants management restaurant management software restaurant management app Home Delivery Food Delivery boy Delivery tracking Courier delivery',
    'description': """
Delivery Control System
========================
Delivery Control System is an online system which allows the delivery manager to process the sale orders. 
It's feature includes assign a delivery control guy, collect payment from the guy, handle any delivery related issues etc.


Odoo Delivery Driver Boy
========================
Odoo delivery boy app allows you to assign the delivery boys and manage the delivery orders through our app. You could be running a restaurant or groceries or any kind of store and can use this app for managing a fleet of drivers to do home delivery.

Features:
---------
    * Makes it easy for delivery boys to track and manage their orders.
    * Provides GPS tracking feature for easy and fast delivery from the start point to endpoint.
    * Odoo delivery boy app provides easy user interface for delivery boys.
    * Manages the order status.
    * Send messages and call customers in case of need.

<keywords>
Odoo - Restaurants Delivery Control System
restaurant management system
restaurants
odoo restaurant
restaurant management
restaurant management software
restaurant management app 
Delivery
Home Delivery
Food Delivery
Delivery tracking
Courier delivery
Odoo Delivery Driver Boy odoo Delivery Boy Delivery Control System odoo restaurants delivery control system restaurant management system restaurant management software restaurant management app   
    """,
    'depends': ['point_of_sale','pos_restaurant', 'stock', 'account', 'pragmatic_odoo_delivery_boy'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_view.xml',
        'views/pos_order_view.xml',
        'views/pos_home_delivery_templates.xml',
        'views/control_delivery_app.xml',
        'views/delivery_boy_app.xml',
        'views/route_map_pos.xml',
        'views/route_map_admin_view.xml',
        'views/pos_job_list_customer_template.xml',
        'views/pos_route_map_customer_view.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': ['static/description/Home-Delivery-All-in-One.gif'],
    'currency': 'USD',
    'license': 'OPL-1',
    'price': 301.00,
    'installable': True,
    'application': False,
    'auto_install': False,
}
