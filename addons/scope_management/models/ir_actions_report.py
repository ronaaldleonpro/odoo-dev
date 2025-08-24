from odoo import models

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        result = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
        if self._get_report(report_ref).report_name != "sale.report_saleorder":
            return result

        orders = self.env["sale.order"].browse(res_ids)
        for order in orders:
            if not order.scope_ids:
                continue

            initial_stream = result[order.id]["stream"]
            if not initial_stream:
                continue

            writer = self._init_writer(initial_stream)
            # Renderizar scopes en PDF usando tu plantilla QWeb
            scope_pdf, _ = self.env.ref("scope_management.scope_pdf_report")._render_qweb_pdf(order.scope_ids.ids)
            self._add_pages_to_writer(writer, scope_pdf)

            # Guardar el resultado en el stream final
            import io
            with io.BytesIO() as _buffer:
                writer.write(_buffer)
                stream = io.BytesIO(_buffer.getvalue())
            result[order.id].update({"stream": stream})
        return result

    def _init_writer(self, initial_stream):
        from odoo.tools.pdf import PdfFileWriter, PdfFileReader
        import io
        writer = PdfFileWriter()
        reader = PdfFileReader(io.BytesIO(initial_stream.getvalue()), strict=False)
        for page in reader.pages:
            writer.addPage(page)
        return writer
