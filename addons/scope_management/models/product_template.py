from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    scope_id = fields.Many2one(
        'scope.management',
        string="Scope",
        help="Technical scope (alcance) associated with this product."
    )