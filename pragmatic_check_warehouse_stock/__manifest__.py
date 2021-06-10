{
    'name': 'Assign Warehouse on stock availability.',
    'version': '13.0.3',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'category': 'Website',
    'summary': 'Assign Warehouse on stock availability.',
    'description': """
Assign Warehouse on stock availability
======================
List of features as below:

Features:
---------
    * Allow to assign warehouse based on stock availability.

    """,
    'depends': [ 'sale', 'website_sale_stock'],
    'data': [

        'views/template.xml',
    ],
    'images': ['static/description/icon.png'],
    # 'currency': 'USD',
    'license': 'OPL-1',
    # 'price': 299.00,
    'installable': True,
    'application': True,
    'auto_install': False,
}
