from odoo import api, models, fields
from odoo.tools import html2plaintext

class ScopeManagement(models.Model):
    _name = 'scope.management'
    _description = 'Scopes Management'

    name = fields.Char(string='Service', required=True)
    description = fields.Html(string='Description')
    product_id = fields.Many2one('product.product', string='Product')
    product_ids = fields.One2many('product.template', 'scope_id', string='Products')
    sales_team = fields.Many2one('crm.team', string='Sales Team')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], string="State", default='draft')
    active = fields.Boolean(default=True)

    sale_order_id = fields.Many2one("sale.order", string="Sale Order", ondelete="cascade")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') and vals.get('description'):
                text = html2plaintext(vals['description'])
                name = text.strip().replace('*', '').partition("\n")[0]
                vals['name'] = (name[:97] + '...') if len(name) > 100 else name
        return super().create(vals_list)

    def action_mark_completed(self):
        self.write({'state': 'completed'})

    def action_mark_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_mark_canceled(self):
        self.write({'state': 'canceled'})

    def action_reopen(self):
        self.write({'state': 'draft'})

    
class ProductProduct(models.Model):
    _inherit = 'product.product'

    scope_ids = fields.One2many('scope.management', 'product_id', string='Scopes')