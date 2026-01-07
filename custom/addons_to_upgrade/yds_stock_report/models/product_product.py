# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    today = fields.Date(string='Your string', default=lambda self: fields.Date.today())
    
    report_in_qty = fields.Float(
        string='Report_in_qty', 
        required=False)

    def set_quantity_in(self, start_date, end_date):
        today = date.today()
        if not end_date:
            end_date = today

        print('start date before >>>', start_date)
        if not start_date:
            print('no start date')
            start_date_str = '1900-01-01'
            start_date = datetime.strptime(start_date_str, "%d-%B-%Y")

        print('start date after >>>', start_date)
        if start_date and end_date:
            move_lines = self.env['stock.move.line'].search(
                [(' ', '=', self.id), ('date', '>=', start_date), ('date', '<=', end_date)])
            in_qty = sum(
                move_lines.filtered(lambda x: x.picking_id.picking_type_id.code == 'incoming').mapped('qty_done'))
            print('in >>>', in_qty)
            out_qty = sum(
                move_lines.filtered(lambda x: x.picking_id.picking_type_id.code == 'outgoing').mapped('qty_done'))
            print('out >>>', out_qty)
            print('in + out', in_qty+out_qty)
            return in_qty - out_qty
