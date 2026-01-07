from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    in_qty = fields.Float(string='in_qty', compute='_compute_in_qty')
    out_qty = fields.Float(string='out_qty', compute='_compute_out_qty')
    returned_qty = fields.Float(string='returned_qty', compute='_compute_returned_qty')

    # operation = fields.Char(string='Operation', compute='_compute_operation', store=True)

    # receipt_qty = fields.Char(string='Receipt Qty', compute='_compute_receipt_qty', store=True)
    # delivery_qty = fields.Char(string='Delivery Qty', compute='_compute_delivery_qty', store=True)
    # internal_tran_qty = fields.Char(string='Internal Tran Qty', compute='_compute_internal_tran_qty', store=True)
    # mrp_qty = fields.Char(string='Manufacture Qty', compute='_compute_mrp_qty', store=True)

    @api.depends('location_dest_id.usage', 'location_id.usage', 'qty_done', 'picking_type_id')
    def _compute_returned_qty(self):
        for rec in self:
            rec.returned_qty = 0.0
            if (rec.location_id.usage not in ['internal', 'transit'] and rec.location_dest_id.usage in
                    ['internal', 'transit'] and rec.picking_type_id.name == "Returns"):
                rec.returned_qty += rec.qty_done

    @api.depends('location_dest_id.usage', 'location_id.usage', 'qty_done')
    def _compute_in_qty(self):
        for rec in self:
            rec.in_qty = 0.0
            # print('rec origin >>', rec.move_id.picking_id.origin)
            if rec.location_id.usage not in ['internal', 'transit'] and rec.location_dest_id.usage in ['internal','transit'] :
                rec.in_qty += rec.qty_done

    @api.depends('location_dest_id.usage', 'location_id.usage', 'qty_done')
    def _compute_out_qty(self):
        for rec in self:
            rec.out_qty = 0.0
            if (rec.location_id.usage in ['internal', 'transit'] and rec.location_dest_id.usage not in ['internal',
                                                                                                        'transit'] and 'إرجاع' not in [
                rec.move_id.picking_id.origin] and 'Return' not in [rec.move_id.picking_id.origin]):
                rec.out_qty += rec.qty_done

    # @api.depends('picking_id.picking_type_id.code', 'qty_done')
    # def _compute_internal_tran_qty(self):
    #     for rec in self:
    #         rec.internal_tran_qty = 0.0
    #         if rec.picking_id.picking_type_id.code == 'internal' and rec.qty_done:
    #             rec.internal_tran_qty = rec.qty_done
    #
    # @api.depends('picking_id.picking_type_id.code', 'qty_done')
    # def _compute_mrp_qty(self):
    #     for rec in self:
    #         rec.mrp_qty = 0.0
    #         if rec.picking_id.picking_type_id.code == 'mrp_operation' and rec.qty_done:
    #             rec.mrp_qty = rec.qty_done

    # @api.depends('picking_id.picking_type_id.code')
    # def _compute_operation(self):
    #     for rec in self:
    #         rec.operation = ''
    #         if rec.picking_id and rec.picking_id.picking_type_id and rec.picking_id.picking_type_id.code:
    #             rec.operation = rec.picking_id.picking_type_id.code
