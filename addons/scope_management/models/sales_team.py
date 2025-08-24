from odoo import models, fields

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    x_include_technical_proposal = fields.Boolean(
        string="Include Technical Proposal",
        default=False,
        help="If enabled, quotations for this team can include a Technical Proposal PDF built from product Scopes."
    )
