from datetime import date, datetime

from odoo import api, fields, models
import base64
import xlsxwriter
import io


class StockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'
    _description = 'Stock Report Wizard'

    excel_sheet = fields.Binary()
    start_date = fields.Datetime('Start Date', default=fields.Datetime.now())
    end_date = fields.Datetime('End Date')
    # product_id = fields.Many2one(comodel_name='product.product', string='Product',required=False)
    location_id = fields.Many2one(comodel_name='stock.location', string='Location', required=False)
    category_id = fields.Many2one(comodel_name='product.category', string='Product Category', required=False)
    product_ids = fields.Many2many(comodel_name='product.product', string='Products')
    move_line_ids = fields.Many2many(comodel_name='stock.move.line', string='stock_move_lines')

    today = fields.Datetime(string='Your string', default=lambda self: fields.Datetime.now())

    # opening = fields.Char(string='Opening')
    #
    # def _compute_opening(products):
    #     opening ={}
    #     if not products:
    #         products = self.env['product.product'].search([])
    #     for product in products:
    #         opening[product.id] = product.name
    #     for key, value in opening:
    #         print('opening ', key+ " "+ value)
    #     self.opening = opening

    def action_create_search(self):
        self.move_line_ids = False
        domain = []
        product = self.product_ids
        if product:
            domain += [("product_id", "in", product.ids)]

        start_date = self.start_date
        if start_date:
            domain += [('date', '>=', start_date)]

        end_date = self.end_date
        if end_date:
            domain += [('date', '<=', end_date)]

        location_id = self.location_id
        if location_id:
            domain += [('location_id', '=', location_id.id)]

        self.move_line_ids = self.env['stock.move.line'].search(domain, order='product_id ASC').sorted(
            key='product_id')
        return self.move_line_ids

    def action_create_search_html(self):
        self.action_create_search()
        return self.env.ref('yds_stock_report.stock_report_html_action').report_action(self)

    def action_create_search_pdf(self):
        self.action_create_search()
        return self.env.ref('yds_stock_report.stock_report_pdf_action').report_action(self)

    def action_create_search_xlsx(self):
        report_name = "Stock Report "
        self.action_create_search()
        start_date = datetime(2000, 1, 1, 10, 0, 0, 0)
        if self.start_date:
            start_date = self.start_date
        end_date = datetime(2100, 1, 1, 10, 0, 0, 0)
        if self.end_date:
            end_date = self.end_date
        date_from = "From"
        date_to = "To"

        header_product = "Product Name"
        header_opening_balance = "Opening Balance"
        header_in = "In"
        header_out = "Out"
        header_returned = "Returned"
        header_qty_scrap = "Scrap"
        header_ending = "Ending"

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        header_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': 1, 'border': 2,
                                             'bg_color': '#BBDEFB'})
        content_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': 1, 'border': 2})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#BBDEFB'})

        merge_left_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'fg_color': '#BBDEFB'})

        merge_right_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'})

        borders = workbook.add_format()
        borders.set_border(1)

        sheet = workbook.add_worksheet(report_name)
        sheet.conditional_format('A1:ZZ120000', {'type': 'no_errors', 'format': borders})
        sheet.set_column('A:AK', None, center)
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:G', 30)
        sheet.set_column('F:F', 35)
        sheet.set_column('H:J', 15)

        sheet.merge_range('A1:E1', report_name, merge_format)

        # sheet.write(1, 2, date_from, header_format)
        # sheet.write(1, 3, str(start_date), header_format)
        # sheet.write(1, 4, date_to, header_format)
        # sheet.write(1, 5, str(end_date), header_format)

        row = 3

        sheet.write(2, 0, header_product, header_format)
        sheet.write(2, 1, header_opening_balance, header_format)
        sheet.write(2, 2, header_in, header_format)
        sheet.write(2, 3, header_out, header_format)
        sheet.write(2, 4, header_returned, header_format)
        sheet.write(2, 5, header_qty_scrap, header_format)
        sheet.write(2, 6, header_ending, header_format)

        for product in (self.product_ids or self.move_line_ids.mapped('product_id')):
            opening_qty = 0
            opening_qty = sum(self.env['stock.valuation.layer'].search(
                [('product_id', '=', product.id), ('create_date', '<=', self.start_date)]).mapped('quantity'))
            qty_in = product.set_quantity_in(product.id, start_date=self.start_date, end_date=self.end_date)
            qty_out = product.set_quantity_out(product.id, start_date=self.start_date, end_date=self.end_date)
            # qty_rtn = product.set_quantity_rtn(product.id, start_date=self.start_date, end_date=self.end_date)
            rtn_moves = self.env['stock.move.line'].search(
                [('product_id', '=', product.id), ('create_date', '>=', start_date), ('create_date', '<=', end_date),
                 ('location_dest_id.name', 'not like', '%Scrap%'),
                 ('state', '=', 'done'), '|', ('picking_id.origin', 'like', '%إرجاع%'),
                 ('picking_id.origin', 'like', '%Return%')])
            qty_rtn = sum(rtn_moves.mapped('quantity'))
            qty_scrap = 0.0
            scrap_moves = self.env['stock.scrap'].search([('product_id', '=', product.id), ('create_date', '>=', start_date),
                                                          ('create_date', '<=', end_date), ('state', '=', 'done')])
            qty_scrap = sum(scrap_moves.mapped('scrap_qty'))
            in_quantities = 0.0
            out_quantities = 0.0
            return_qty = 0.0
            for move in rtn_moves:
                if 'IN' in move.picking_id.origin:
                    in_quantities += move.quantity
                    return_qty += move.quantity

                if 'OUT' in move.picking_id.origin:
                    out_quantities += move.quantity
                    return_qty -= move.quantity

            out_quantities = out_quantities - qty_scrap
            qty_out -= in_quantities
            qty_out -= qty_scrap
            # return_qty = out_quantities + in_quantities + qty_scrap

            ending = opening_qty + qty_in - qty_out - return_qty - qty_scrap

            sheet.write(row, 0, product.name if product else '', content_format)
            sheet.write(row, 1, opening_qty if opening_qty else '0', content_format)
            sheet.write(row, 2, qty_in if qty_in else '0', content_format)
            sheet.write(row, 3, qty_out if qty_out else '0', content_format)
            sheet.write(row, 4, abs(return_qty) if return_qty else '0', content_format)
            sheet.write(row, 5, qty_scrap if qty_scrap else '0', content_format)
            sheet.write(row, 6, ending if ending else '0', content_format)
            # sheet.write(row, 2, product.set_quantity_in(product.id, start_date=self.start_date,
            #                                         end_date=self.end_date), content_format)
            # sheet.write(row, 3, str(invoice.invoice_date) if invoice.invoice_date else '', content_format)
            # sheet.write(row, 4, invoice.invoice_payment_term_id.name if invoice.invoice_payment_term_id else '', content_format)
            # sheet.write(row, 5, str(invoice.invoice_date_due) if invoice.invoice_date_due else '', content_format)

            row += 1

        workbook.close()
        output.seek(0)
        # Use standard b64encode and store as text to avoid binary/newline issues
        self.write({'excel_sheet': base64.b64encode(output.getvalue()).decode('ascii')})

        return {
            'type': 'ir.actions.act_url',
            'name': report_name,
            'url': '/web/content/stock.report.wizard/%s/excel_sheet/{}.xlsx?download=true'.format(
                report_name) % self.id,
            'target': 'self'
        }
