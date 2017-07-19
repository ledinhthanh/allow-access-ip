# coding: utf-8
{
    "name": "Allow IP to Login odoo",
    "version": "8.0.0.1.6",
    "author": "ThanhLd",
    "category": "Base",
    "summary": "User can not login if he has not assigned IP address from where he is accessing Odoo",
    "website": "www.retech.com.vn",
    'description':
        """
Allow IP to Login odoo.
========================

User can not login if he has not assigned IP address from where he is accessing Odoo.
        """,
    "license": "",
    "depends": [
    ],
    "demo": [],
    'data': [
        'security/ir.model.access.csv',
        'views/allow_view.xml'
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
