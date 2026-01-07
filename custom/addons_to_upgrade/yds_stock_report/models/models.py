# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    today = fields.Datetime(string='Your string', default=lambda self: fields.Datetime.now())

    def set_quantity_in(self, product_id=None, start_date=None, end_date=None):
        if not product_id and self:
            product_id = self.id
        if not start_date:
            start_date = datetime(1900, 1, 1)
        if not end_date:
            end_date = datetime.now()

        move_lines = self.env['stock.move.line'].search([
            ('product_id', 'in', [product_id]),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('picking_id.origin', 'not ilike', '%إرجاع%'),
            ('picking_id.origin', 'not ilike', '%Return%')
        ])

        in_qty = sum(move_lines.mapped('in_qty'))
        return in_qty

    def set_quantity_out(self, product_id=None, start_date=None, end_date=None):
        if not product_id and self:
            product_id = self.id
        if not start_date:
            start_date = datetime(1900, 1, 1)
        if not end_date:
            end_date = datetime.now()

        move_lines = self.env['stock.move.line'].search([
            ('product_id', 'in', [product_id]),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            '|',
            ('picking_id.origin', 'not ilike', '%إرجاع%'),
            ('picking_id.origin', 'not ilike', '%Return%')
        ])

        out_qty = sum(move_lines.mapped('out_qty'))
        return out_qty

    def set_quantity_rtn(self, product_id=None, start_date=None, end_date=None):
        if not product_id and self:
            product_id = self.id
        if not start_date:
            start_date = datetime(1900, 1, 1)
        if not end_date:
            end_date = datetime.now()

        move_lines = self.env['stock.move.line'].search([
            ('product_id', 'in', [product_id]),
            ('date', '>=', start_date),
            ('date', '<=', end_date)
        ])
        returned_qty = sum(move_lines.mapped('returned_qty'))
        return returned_qty
