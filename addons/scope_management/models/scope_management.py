# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.tools import html2plaintext

class ScopeManagement(models.Model):
    _name = 'scope.management'
    _description = 'Scopes Management'

    name = fields.Char(string='Scope Title', required=True)
    description = fields.Html(string='Description')

    sales_team = fields.Many2one(
        'crm.team', string='Sales Team'
    )

    product_name = fields.Many2one(
        'product.template', string='Product'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], string="State", default='draft')

    # Métodos de creación
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') and vals.get('description'):
                # Generar nombre desde la descripción si no se proporciona
                text = html2plaintext(vals['description'])
                name = text.strip().replace('*', '').partition("\n")[0]
                vals['name'] = (name[:97] + '...') if len(name) > 100 else name
        return super().create(vals_list)

    # Acciones
    def action_mark_completed(self):
        self.write({'state': 'completed'})

    def action_mark_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_mark_canceled(self):
        self.write({'state': 'canceled'})

    def action_reopen(self):
        self.write({'state': 'draft'})