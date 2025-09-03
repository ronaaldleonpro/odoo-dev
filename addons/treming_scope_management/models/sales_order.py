from odoo import models, fields, api
import base64
from odoo.exceptions import UserError

# Optional: Import pypdf for adding form fields (for inputs/labels in Quote Builder)
# from pypdf import PdfWriter, PdfReader
# import io

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

    related_scope_products = fields.Char(
        string="Products with Scopes",
        compute="_compute_related_scope_products",
        store=True
    )

    scope_ids = fields.One2many("scope.management", "sale_order_id", string="Scopes")

    show_related_scope_products = fields.Boolean(
        string="Show Related Scope Products",
        compute="_compute_show_related_scope_products",
        store=True
    )

    technical_proposal_document_id = fields.Many2one(
        'quotation.document',  # Ajustado para el modelo personalizado quotation.document
        string="Technical Proposal Document",
        help="Documento PDF generado desde los scopes para adjuntar en Quote Builder."
    )

    @api.depends('related_scope_ids.product_id')
    def _compute_related_scope_products(self):
        for order in self:
            product_names = order.related_scope_ids.mapped('product_id.name')
            order.related_scope_products = ", ".join(product_names) if product_names else "No products"

    @api.depends('order_line.product_id')
    def _compute_related_scope_ids(self):
        for order in self:
            product_ids = order.order_line.mapped('product_id').ids
            scopes = self.env['scope.management'].search([('product_id', 'in', product_ids)])
            order.related_scope_ids = scopes

    @api.depends('related_scope_ids')
    def _compute_has_related_scopes(self):
        for order in self:
            order.has_related_scopes = bool(order.related_scope_ids)

    @api.depends('team_id', 'related_scope_ids.sales_team', 'team_include_technical_proposal')
    def _compute_show_related_scope_products(self):
        for order in self:
            team_matches = any(scope.sales_team == order.team_id for scope in order.related_scope_ids)
            order.show_related_scope_products = team_matches and order.team_include_technical_proposal

    def action_attach_technical_proposal(self):
        """Genera el PDF desde los scopes y lo adjunta como documento en Quote Builder."""
        self.ensure_one()
        if not self.related_scope_ids:
            raise UserError("No hay alcances relacionados para generar el PDF.")

        # Obtener el reporte
        try:
            report = self.env.ref('scope_management.action_report_scope_proposal')
        except ValueError:
            raise UserError("El reporte 'action_report_scope_proposal' no está definido o no se encuentra.")

        # Generar el PDF
        pdf_content, _ = report._render_qweb_pdf(report_ref=report, res_ids=[self.id])
        datas = base64.b64encode(pdf_content)

        # Opcional: Agregar form fields para inputs/labels en Quote Builder (requiere pypdf)
        # writer = PdfWriter()
        # reader = PdfReader(io.BytesIO(pdf_content))
        # writer.append(reader)
        # # Agregar campos de formulario (ejemplo)
        # writer.add_form_field(name="CustomerName", value="", type="text", x=100, y=100, page=0)
        # writer.add_form_field(name="TotalAmount", value="", type="text", x=200, y=200, page=0)
        # output = io.BytesIO()
        # writer.write(output)
        # datas = base64.b64encode(output.getvalue())

        # Si ya existe un documento, actualízalo (sin eliminarlo para evitar errores de FK)
        if self.technical_proposal_document_id:
            self.technical_proposal_document_id.write({
                'datas': datas,
                'mimetype': 'application/pdf',
                'name': f'Propuesta Técnica para {self.name}.pdf',
                'active': True,  # Desarchivar si estaba archivado
            })
        else:
            doc = self.env['quotation.document'].create({
                'name': f'Propuesta Técnica para {self.name}.pdf',
                'type': 'binary',
                'datas': datas,
                'mimetype': 'application/pdf',
                'attached_on_sale': 'inside',
            })
            self.technical_proposal_document_id = doc

        # Asegurar que esté en quotation_document_ids
        if self.technical_proposal_document_id.id not in self.quotation_document_ids.ids:
            self.quotation_document_ids = [(4, self.technical_proposal_document_id.id)]

        # Retornar acción para abrir la pestaña Quote Builder
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            'view_id': self.env.ref('sale_pdf_quote_builder.sale_order_form_inherit_sale_pdf_quote_builder').id,
        }

    def action_print_technical_proposal(self):
        """Adjunta el PDF y luego imprime."""
        self.ensure_one()
        self.action_attach_technical_proposal()
        try:
            report = self.env.ref('scope_management.action_report_scope_proposal')
        except ValueError:
            raise UserError("El reporte 'action_report_scope_proposal' no está definido o no se encuentra.")
        return report.report_action(self)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_scope(self):
        if self.order_id:
            product_ids = self.order_id.order_line.mapped('product_id').ids
            scopes = self.env['scope.management'].search([('product_id', 'in', product_ids)])
            self.order_id.related_scope_ids = [(6, 0, scopes.ids)]