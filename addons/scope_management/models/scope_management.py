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
    description = fields.Html(string="Description")

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

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        streams = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
        if report_ref in ('sale.report_saleorder', 'sale.report_saleorder_pro_forma'):
            for order_id in streams:
                order = self.env['sale.order'].browse(order_id)
                if order.team_include_technical_proposal:
                    for line in order.order_line:
                        if line.include_technical_proposal and line.product_id.scope_id:
                            scope_report = self.env.ref('scope_management.action_report_scope_proposal')
                            line_pdf, _ = scope_report._render_qweb_pdf(line.id)
                            streams[order_id]['stream'].write(line_pdf)
        return streams
    
class ProductProduct(models.Model):
    _inherit = 'product.product'

    scope_ids = fields.One2many('scope.management', 'product_id', string='Scopes')