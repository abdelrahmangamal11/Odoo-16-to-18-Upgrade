# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    today = fields.Date(string='Your string', default=lambda self: fields.Date.today())
    
    report_in_qty = fields.Float(
        string='Report_in_qty', 
        required=False)

    def set_quantity_in(self, product_id=None, start_date=None, end_date=None):
        if not product_id and self:
            product_id = self.id
        if not start_date:
            start_date = datetime.now(1900, 1, 1)
        if not end_date:
            end_date = fields.Datetime.now()

        move_lines = self.env['stock.move.line'].search([
            ('product_id', '=', product_id),
            ('date', '>=', start_date),
            ('date', '<=', end_date)
        ])

        in_qty = sum(move_lines.filtered(lambda x: x.picking_id and x.picking_id.picking_type_id and x.picking_id.picking_type_id.code == 'incoming').mapped('quantity'))
        out_qty = sum(move_lines.filtered(lambda x: x.picking_id and x.picking_id.picking_type_id and x.picking_id.picking_type_id.code == 'outgoing').mapped('quantity'))
        return in_qty - out_qty
