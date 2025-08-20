# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.tools import html2plaintext

class ScopeManagement(models.Model):
    _name = 'scope.management'
    _description = 'Scope Management'

    name = fields.Char(string='Scope Title', required=True)
    description = fields.Html(string='Description')
    color = fields.Integer(string="Color")
    sequence = fields.Integer(string="Sequence")
    active = fields.Boolean(default=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
    ], string='Priority', default='1')

    categories = fields.Selection([
        ('0', 'Implementacion Odoo'),
        ('1', 'Facturacion electronica'),
        ('2', 'SLA'),
        ('3', 'Outsourcing'),
        ('4', 'Desarrollo'),
        ('5', 'Reclutamiento'),
    ], string="Linea de negocio", default='0')

    product_name = fields.Many2one(
        'product.template', string='Product'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], string="State", default='draft')

    user_ids = fields.Many2many(
        'res.users', string='Assigned Users',
        relation='scope_management_user_rel',
        column1='scope_id', column2='user_id',
    )

    tag_ids = fields.Many2many(
        'scope.tags', string='Tags',
        relation='scope_management_tags_rel',
        column1='scope_id', column2='tag_id'
    )

    #project_id = fields.Many2one(
    #    'project.project', string='Project'
    #)

    parent_id = fields.Many2one(
        'scope.management', string='Parent Scope', index=True
    )

    #company_id = fields.Many2one(
    #    'res.company', string='Company',
    #    default=lambda self: self.env.company,
    #    required=True
    #)
    

    is_closed = fields.Boolean(
        string='Closed',
        compute='_compute_is_closed',
        store=True
    )

    date_last_stage_update = fields.Datetime(string="Last Status Update")

    # Campos computados
    @api.depends('state')
    def _compute_is_closed(self):
        for record in self:
            record.is_closed = record.state in ('completed', 'canceled')

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