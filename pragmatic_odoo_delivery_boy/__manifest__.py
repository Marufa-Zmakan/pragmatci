{
    'name': 'Odoo Delivery Driver Boy',
    'version': '13.0.13',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'category': 'Website',
    'summary': 'Odoo Delivery Driver Boy odoo Delivery Boy Delivery Control System odoo restaurants delivery control system restaurant management system restaurant management software restaurant management app',
    'description': """
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

    """,
    'depends': ['pragmatic_delivery_control_app','website_sale_stock','point_of_sale'],
    'data': [
        'data/website_menus_driver.xml',
        'data/res_groups.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/order_details.xml',
        'views/stock_driver_views.xml',
        'views/res_partner_view.xml',
        'views/picking_order_view.xml',
        'views/server_action.xml',
        'views/sale_order_view.xml',
        'views/job_list_template.xml',
        'views/order_details_admin.xml',
        'views/logged_in_template.xml',
        'wizards/picking_order_wizard_view.xml',
        # 'views/driver_settings.xml'
        'views/admin_drivers_details_template.xml',
        'views/route_map_admin.xml',
        'views/res_config_settings_view.xml',
        'views/whatsapp_scan_qr_code_view.xml',
        'views/website_menu.xml',
        'views/job_list_customer_template.xml',
        'views/route-map-customer-view.xml',
        'views/driver_location_views.xml'

    ],
    'images': ['static/description/odoo-delivery-driver-boy-gif.gif'],
    'currency': 'USD',
    'license': 'OPL-1',
    'price': 299.00,
    'installable': True,
    'application': True,
    'auto_install': False,
}
