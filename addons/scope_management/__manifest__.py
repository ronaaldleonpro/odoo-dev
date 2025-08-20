# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Scopes',
    'version': '1.0',
    'category': 'Productivity/Scopes',
    'summary': 'Organize your quotazion with scopes',
    'depends': ['base'],
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/scope_management_menus.xml',
        'views/scope_management_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
