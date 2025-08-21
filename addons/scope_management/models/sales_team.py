# models/sales_team_inherit.py
from odoo import models, fields

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    x_scope_enabled = fields.Boolean(
        string="Enable Scopes",
        default=False,
        help="Indicates if this sales team uses the Scopes module"
    )
