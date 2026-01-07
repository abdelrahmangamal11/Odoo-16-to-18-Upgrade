# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    today = fields.Datetime(string='Your string', default=lambda self: fields.Datetime.now())

    def set_quantity_in(self, product_id, start_date, end_date):
        today = date.today()
        if not end_date:
            end_date = today
        if not start_date:
            start_date = datetime(2010, 10, 25, 15, 2, 52)

        in_qty = 0.0
        if product_id and start_date and end_date:
            move_lines = self.env['stock.move.line'].search(
                [('product_id', 'in', [product_id]), ('create_date', '>=', start_date),
                 ('create_date', '<=', end_date),('picking_id.origin', 'not like', '%إرجاع%'),
                 ('picking_id.origin', 'not like', '%Return%')])

            in_qty = sum(move_lines.mapped('in_qty'))
            return in_qty

    def set_quantity_out(self, product_id, start_date, end_date):
        today = date.today()
        if not end_date:
            end_date = today
        if not start_date:
            start_date = datetime(2010, 10, 25, 15, 2, 52)

        if product_id and start_date and end_date:
            move_lines = self.env['stock.move.line'].search(
                [('product_id', 'in', [product_id]), ('create_date', '>=', start_date),
                 ('create_date', '<=', end_date), '|', ('picking_id.origin', 'not like', '%إرجاع%'),
                 ('picking_id.origin', 'not like', '%Return%')])

            for move in move_lines:
                print('move name', move.move_id.picking_id.name)
                print('move origin', move.move_id.picking_id.origin)
                print('move qty', move.move_id.quantity_done)
                print('==========')
            out_qty = sum(move_lines.mapped('out_qty'))
            return out_qty

    def set_quantity_rtn(self, product_id, start_date, end_date):
        today = date.today()
        if not end_date:
            end_date = today
        if not start_date:
            start_date = datetime(2010, 10, 25, 15, 2, 52)

        if product_id and start_date and end_date:
            move_lines = self.env['stock.move.line'].search(
                [('product_id', 'in', [product_id]), ('create_date', '>=', start_date),
                 ('create_date', '<=', end_date)])
            returned_qty = sum(move_lines.mapped('returned_qty'))
            return returned_qty
