# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Scopes',
    'version': '1.0',
    'category': 'Productivity/Scopes',
    'summary': 'Organize your quotazion with scopes',
    'depends': ['base', 'sale', 'stock', 'crm', 'product', 'web', 'mail', 'sale_management','sale_pdf_quote_builder',],
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/sales_team_views.xml',
        'views/sales_team_document_views.xml',
        'views/sales_order_views.xml',
        'views/product_template_views.xml',
        'views/scope_management_views.xml',
        'report/paperformat.xml',
        'report/scope_pdf_template.xml',
        'views/scope_management_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
