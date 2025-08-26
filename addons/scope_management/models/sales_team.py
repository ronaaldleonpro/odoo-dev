from odoo import models, fields

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    x_include_technical_proposal = fields.Boolean(
        string="Include Technical Proposal",
        default=False,
        help="If enabled, quotations for this team can include a Technical Proposal PDF built from product Scopes."
    )

    quotation_document_ids = fields.Many2many(
        'quotation.document',
        'crm_team_quotation_document_rel',  # nombre de la tabla intermedia
        'crm_team_id',                      # FK hacia crm.team
        'quotation_document_id',            # FK hacia quotation.document
    )