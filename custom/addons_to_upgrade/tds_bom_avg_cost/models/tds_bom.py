from odoo import models, fields, api


class TDSBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    tds_cost = fields.Float(string="Cost", related='product_id.standard_price')
    tds_avg_cost = fields.Float(string="Total Cost", compute='_calc_avg_cost',store=True)

    @api.depends('tds_cost', 'product_qty')
    def _calc_avg_cost(self):
        for line in self:
            if line.tds_cost and line.product_qty:
                line.tds_avg_cost = line.tds_cost * line.product_qty
            else:
                line.tds_avg_cost = 0.0



class TDSBom(models.Model):
    _inherit = 'mrp.bom'
    total_tds_cost = fields.Float(string="Total Components Cost",compute='_calc_total_tds_cost',store=True)
    tds_avg_cost = fields.Float(string="Avg cost", compute='_calc_tds_avg_cost',store=True)

    # @api.depends('tds_avg_cost')
    # def _calc_total_tds_cost(self):
    #     for bom in self:
    #         total = 0  # Initialize total inside the outer loop
    #         for line in bom.bom_line_ids:
    #             if line.tds_avg_cost:
    #                 total += line.tds_avg_cost
    #         bom.total_tds_cost = total

    @api.depends('bom_line_ids.tds_avg_cost')
    def _calc_total_tds_cost(self):
        for bom in self:
            bom.total_tds_cost = sum(
                bom.bom_line_ids.mapped('tds_avg_cost')
            )


    @api.depends('total_tds_cost', 'product_qty')
    def _calc_tds_avg_cost(self):
        for bom in self:
            if bom.total_tds_cost and bom.product_qty:
                bom.tds_avg_cost = bom.total_tds_cost / bom.product_qty
            else:
                bom.tds_avg_cost = 0.0

