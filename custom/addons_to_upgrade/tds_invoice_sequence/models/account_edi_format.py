from odoo import models, fields, api


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    @api.model
    def _l10n_eg_eta_prepare_eta_invoice(self, invoice):

        def group_tax_retention(base_line, tax_values):
            tax = tax_values['tax_repartition_line'].tax_id
            return {'l10n_eg_eta_code': tax.l10n_eg_eta_code.split('_')[0]}

        date_string = invoice.invoice_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        grouped_taxes = invoice._prepare_edi_tax_details(
            grouping_key_generator=group_tax_retention)
        invoice_line_data, totals = self._l10n_eg_eta_prepare_invoice_lines_data(
            invoice, grouped_taxes['tax_details_per_record'])
        eta_invoice = {
            'issuer': self._l10n_eg_eta_prepare_address_data(invoice.journal_id.l10n_eg_branch_id, invoice, issuer=True,),
            'receiver': self._l10n_eg_eta_prepare_address_data(invoice.partner_id, invoice),
            'documentType': 'i' if invoice.move_type == 'out_invoice' else 'c' if invoice.move_type == 'out_refund' else 'd' if invoice.move_type == 'in_refund' else '',
            'documentTypeVersion': '1.0',
            'dateTimeIssued': date_string,
            'taxpayerActivityCode': invoice.journal_id.l10n_eg_activity_type_id.code,
            'internalID': invoice.name.split("/")[-1],
        }
        eta_invoice.update({
            'invoiceLines': invoice_line_data,
            'taxTotals': [{
                'taxType': tax['l10n_eg_eta_code'].split('_')[0].upper(),
                'amount': self._l10n_eg_edi_round(abs(tax['tax_amount'])),
            } for tax in grouped_taxes['tax_details'].values()],
            'totalDiscountAmount': self._l10n_eg_edi_round(totals['discount_total']),
            'totalSalesAmount': self._l10n_eg_edi_round(totals['total_price_subtotal_before_discount']),
            'netAmount': self._l10n_eg_edi_round(abs(invoice.amount_untaxed_signed)),
            'totalAmount': self._l10n_eg_edi_round(abs(invoice.amount_total_signed)),
            'extraDiscountAmount': 0.0,
            'totalItemsDiscountAmount': 0.0,
        })
        if invoice.ref:
            eta_invoice['purchaseOrderReference'] = invoice.ref
        if invoice.invoice_origin:
            eta_invoice['salesOrderReference'] = invoice.invoice_origin
        return eta_invoice


# class AccountMove(models.Model):
#     _inherit = 'account.move'
#     tds_eta_name = fields.Char('ETA Name', compute='_compute_eta_name')

#     @api.depends('name')
#     def _compute_eta_name(self):
#         for invoice in self:
#             invoice.tds_eta_name = invoice.name.split("/")[-1]
