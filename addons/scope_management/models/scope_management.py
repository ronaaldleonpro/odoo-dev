# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#project_id -> scope_id
#project_todo > scope_management
#project_task_view_todo -> scope_management_view

from odoo import api, models, Command, fields
from odoo.tools import html2plaintext


class Task(models.Model):
    _name = 'scope.management'
    _description = 'Scope Management'
    _inherit = ['mail.activity.mixin']  # necesario para activity_ids, activity_state

    name = fields.Char(string='To-do Title', required=True)
    description = fields.Html(string='Description')

    color = fields.Integer(string="Color")  # usado en kanban + tags
    sequence = fields.Integer(string="Sequence")
    active = fields.Boolean(default=True)

    state = fields.Selection([
        ('1_todo', 'To Do'),
        ('1_done', 'Done'),
        ('1_canceled', 'Canceled'),
    ], string="State", default='1_todo')

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'High'),
    ], string='Priority', index=True, default='0')

    user_ids = fields.Many2many(
        'res.users', string='Assignees',
        relation='scope_management_user_rel',
        column1='todo_id', column2='user_id',
    )

    tag_ids = fields.Many2many(
        'project.tags', string='Tags',
        relation='scope_management_tags_rel',
        column1='todo_id', column2='tag_id'
    )

    personal_stage_type_id = fields.Many2one(
        'project.task.type', string='Stage'
    )

    displayed_image_id = fields.Many2one(
        'ir.attachment', string="Cover Image"
    )

    project_id = fields.Many2one(
        'project.project', string='Project'
    )

    parent_id = fields.Many2one(
        'scope.management', string='Parent To-do', index=True
    )

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    is_closed = fields.Boolean(
        string='Closed',
        compute='_compute_is_closed',
        store=True
    )

    date_last_stage_update = fields.Datetime(string="Last Stage Update")

    # Actividades (Odoo chatter)
    activity_ids = fields.One2many('mail.activity', 'res_id',
                                   domain=lambda self: [('res_model', '=', self._name)],
                                   string='Activities')
    activity_state = fields.Selection(string='Activity State', compute='_compute_activity_state')

    # Método auxiliar
    def _compute_is_closed(self):
        for record in self:
            record.is_closed = record.state in ('1_done', '1_canceled')

    def _compute_activity_state(self):
        for record in self:
            record.activity_state = record._compute_activity_state_helper()

    def _compute_activity_state_helper(self):
        """ Simplified helper, Odoo normally uses internal logic for this. """
        return False  # Odoo handles this automatically if mail.activity.mixin is inherited


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') and not vals.get('scope_id') and not vals.get('parent_id'):
                if vals.get('description'):
                    # Generating name from first line of the description
                    text = html2plaintext(vals['description'])
                    name = text.strip().replace('*', '').partition("\n")[0]
                    vals['name'] = (name[:97] + '...') if len(name) > 100 else name
                else:
                    vals['name'] = self.env._('Untitled to-do')
        return super().create(vals_list)

    def _ensure_onboarding_todo(self):
        if not self.env.user.has_group('scope_management.group_onboarding_todo'):
            self._generate_onboarding_todo(self.env.user)
            onboarding_group = self.env.ref('scope_management.group_onboarding_todo').sudo()
            onboarding_group.write({'users': [Command.link(self.env.user.id)]})

    def _generate_onboarding_todo(self, user):
        user.ensure_one()
        self_lang = self.with_context(lang=user.lang or self.env.user.lang)
        body = self_lang.env['ir.qweb']._render(
            'scope_management.todo_user_onboarding',
            {'object': user},
            minimal_qcontext=True,
            raise_if_not_found=False
        )
        if not body:
            return
        title = self_lang.env._('Welcome %s!', user.name)
        self.env['scope_service'].create([{
            'user_ids': user.ids,
            'description': body,
            'name': title,
        }])

    def action_convert_to_task(self):
        self.ensure_one()
        self.company_id = self.scope_id.company_id
        return {
            'view_mode': 'form',
            'res_model': 'scope_service',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }

    @api.model
    def get_todo_views_id(self):
        """ Returns the ids of the main views used in the To-Do app.

        :return: a list of views id and views type
                 e.g. [(kanban_view_id, "kanban"), (list_view_id, "list"), ...]
        :rtype: list(tuple())
        """
        return [
            (self.env['ir.model.data']._xmlid_to_res_id("scope_management.scope_management_view_kanban"), "kanban"),
            (self.env['ir.model.data']._xmlid_to_res_id("scope_management.scope_management_view_tree"), "list"),
            (self.env['ir.model.data']._xmlid_to_res_id("scope_management.scope_management_view_form"), "form"),
            (self.env['ir.model.data']._xmlid_to_res_id("scope_management.scope_management_view_activity"), "activity"),
        ]
