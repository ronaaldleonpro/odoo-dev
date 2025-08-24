from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    team_include_technical_proposal = fields.Boolean(
        related='team_id.x_include_technical_proposal',
        string="Team Includes Technical Proposal",
        readonly=True
    )

    related_scope_ids = fields.Many2many(
        'scope.management',
        string="Detected Scopes",
        help="Scopes automatically detected from products in the quotation.",
        compute="_compute_related_scope_ids",
        store=True
    )

    has_related_scopes = fields.Boolean(
        string="Has Related Scopes",
        compute="_compute_has_related_scopes",
        store=True
    )

    scope_ids = fields.One2many("scope.management", "sale_order_id", string="Scopes")

    # --- Computa los scopes a partir de las líneas del pedido ---
    @api.depends('order_line.product_id.scope_id')
    def _compute_related_scope_ids(self):
        for order in self:
            scopes = order.order_line.mapped('product_id.scope_id')
            order.related_scope_ids = scopes

    @api.depends('related_scope_ids')
    def _compute_has_related_scopes(self):
        for order in self:
            order.has_related_scopes = bool(order.related_scope_ids)

    def action_print_technical_proposal(self):
        self.ensure_one()
        # Lanza el reporte PDF (QWeb) que compila las descripciones HTML de los Scopes
        return self.env.ref('scope_management.action_report_scope_proposal').report_action(self)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_scope(self):
        """Cuando selecciono un producto, refresca los scopes en la orden"""
        if self.order_id:
            scopes = self.order_id.order_line.mapped('product_id.scope_id')
            self.order_id.related_scope_ids = [(6, 0, scopes.ids)]