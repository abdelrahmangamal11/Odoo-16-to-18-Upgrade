from odoo import models, fields, api


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    @api.model
    def _l10n_eg_eta_prepare_eta_invoice(self, invoice):
        eta_invoice=super(AccountEdiFormat, self.sudo())._l10n_eg_eta_prepare_eta_invoice(invoice)
        eta_invoice["internalID"]=invoice.split("/")[-1]

        return eta_invoice


# class AccountMove(models.Model):
#     _inherit = 'account.move'
#     tds_eta_name = fields.Char('ETA Name', compute='_compute_eta_name')

#     @api.depends('name')
#     def _compute_eta_name(self):
#         for invoice in self:
#             invoice.tds_eta_name = invoice.name.split("/")[-1]
