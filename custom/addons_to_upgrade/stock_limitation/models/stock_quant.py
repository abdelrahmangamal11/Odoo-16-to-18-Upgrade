# -*- coding: utf-8 -*-

from odoo import api, models


class stock_quant(models.Model):
    """
    Override to avoide security bugs
    """
    _inherit = 'stock.quant'

    @api.model
    def _get_removal_strategy(self, product_id, location_id):
        product_id = product_id.sudo()
        location_id = location_id.sudo()
        if product_id.categ_id.removal_strategy_id:
            return product_id.categ_id.removal_strategy_id.with_context(lang=None).method
        loc = location_id
        while loc:
            if loc.removal_strategy_id:
                return loc.removal_strategy_id.with_context(lang=None).method
            loc = loc.location_id
        return 'fifo'
 
    # @api.model
    # def _get_removal_strategy(self, product_id, location_id):
    #     product_id = product_id.sudo()
    #     location_id = location_id.sudo()
    #     if product_id.categ_id.removal_strategy_id:
    #         return product_id.categ_id.removal_strategy_id.with_context(lang=None).method
    #     loc = location_id
    #     while loc:
    #         if loc.removal_strategy_id:
    #             return loc.removal_strategy_id.with_context(lang=None).method
    #         loc = loc.location_id
    #     return 'fifo'