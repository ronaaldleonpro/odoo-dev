from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'
    scope_id = fields.Many2one(
        related='product_tmpl_id.scope_id',
        string="Scope",
        readonly=True,
        store=True
    )