# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Scope',
    'version': '1.0',
    'category': 'Productivity/Scope',
    'summary': 'Organize your work with memos and to-do lists',
    'sequence': 260,
    'depends': [
    ],
    'auto_install': True,
    'data': [
        'views/scope_management_menus.xml',
        'views/scope_management_views.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'project_todo/static/src/components/**/*',
            'project_todo/static/src/scss/todo.scss',
            'project_todo/static/src/views/**/*',
            'project_todo/static/src/web/**/*',
        ],
        'web.assets_tests': [
            'project_todo/static/tests/tours/**/*',
        ],
        'web.assets_unit_tests': [
            'project_todo/static/tests/**/*',
        ],
    },
    'license': 'LGPL-3',
}
