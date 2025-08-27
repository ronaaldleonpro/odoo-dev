from odoo import api, models, fields
from odoo.tools import html2plaintext

class ScopeManagement(models.Model):
    #Model name & description. Inherits from models.Model (Odoo base class)
    _name = 'scope.management'
    _description = 'Scopes Management'

    name = fields.Char(string='Service', required=True)
    description = fields.Html(string='Description')
    sales_team = fields.Many2one('crm.team', string='Sales Team')
    active = fields.Boolean(default=True)

    # Relación con el producto (cada scope tiene UN producto)
    product_id = fields.Many2one('product.product', string='Product')

    # Relación con la orden (cada scope pertenece a UNA orden)
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", ondelete="cascade")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('description'):
                text = html2plaintext(vals['description'])
                name = text.strip().replace('*', '').partition("\n")[0]
                vals['name'] = (name[:97] + '...') if len(name) > 100 else name
        return super().create(vals_list)