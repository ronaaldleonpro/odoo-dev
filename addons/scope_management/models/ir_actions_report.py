from odoo import models
import io
from odoo.tools import pdf  # Importar el módulo pdf
import logging

_logger = logging.getLogger(__name__)

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        """Override to add scope PDF to the quotation PDF."""
        collected_streams = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)

        # Check if the report is for sale.order
        if self._get_report(report_ref).report_name != 'sale.report_saleorder':
            return collected_streams

        orders = self.env['sale.order'].browse(res_ids)
        for order in orders:
            if order.related_scope_ids:
                try:
                    # Use action_report_scope_proposal for sale.order
                    scope_report = self.env.ref('scope_management.action_report_scope_proposal')
                    scope_pdf, _ = scope_report._render_qweb_pdf(report_ref=scope_report, res_ids=[order.id])
                    # Merge with the existing stream
                    if order.id in collected_streams:
                        initial_stream = collected_streams[order.id]['stream']
                        merged_pdf = pdf.merge_pdf([initial_stream.getvalue(), scope_pdf])
                        collected_streams[order.id]['stream'] = io.BytesIO(merged_pdf)
                except Exception as e:
                    _logger.error(f"Failed to render or merge scope PDF for order {order.name}: {str(e)}")
                    continue

        return collected_streams