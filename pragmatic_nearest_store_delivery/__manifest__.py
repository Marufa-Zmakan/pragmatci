{
    'name': 'Nearest Store Delivery',
    'version': '13.0.2',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'category': 'Website',
    'summary': 'Allow to deliver sale order from nearest store.',
    'description': """
Nearest Store Delivery
======================
List of features as below:

Features:
---------
    * Allow to create stock pickings to delivered product from nearest store.
    * If product not available in nearest store location then create backorder.

    """,
    'depends': ['base_geolocalize', 'sale', 'website_sale_stock'],
    'data': [
        # 'security/res_groups.xml',
        # 'data/order_data.xml',
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/store_customer_mapview.xml',
        'views/sale_views.xml',
    ],
    'images': ['static/description/icon.png'],
    # 'currency': 'USD',
    'license': 'OPL-1',
    # 'price': 299.00,
    'installable': True,
    'application': True,
    'auto_install': False,
}
