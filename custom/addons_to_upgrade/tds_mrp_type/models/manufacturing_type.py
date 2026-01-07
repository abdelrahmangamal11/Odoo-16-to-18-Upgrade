from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.tools import float_compare, OrderedSet



class ManufacturingType(models.Model):
    _name = 'manufacturing.type'

    name = fields.Char(string="Description")

    _sql_constraints = [
        ('unique_mrp_type_name', 'unique (name,active)', 'Description must be unique .'), 
    ]


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mrp_type_id = fields.Many2one('manufacturing.type', string="Manufacturing Type" , required=True, tracking=True) 


    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material', readonly=False,
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
        check_company=True, compute='_compute_bom_id', store=True, precompute=True,
        help="Bills of Materials, also called recipes, are used to autocomplete components and work order instructions.")
 

    @api.constrains('mrp_type_id')
    def _constrains_mrp_type_id(self):
        for rec in self:
            if rec.bom_id.mrp_type_id != rec.mrp_type_id:
                rec.bom_id = None
class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    mrp_type_id = fields.Many2one('manufacturing.type', string="Manufacturing Type" , required=True)      



class StockRule(models.Model):
    _inherit = 'stock.rule'


    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, bom):
        date_planned = self._get_date_planned(product_id, company_id, values)
        date_deadline = values.get('date_deadline') or date_planned + relativedelta(days=product_id.produce_delay)
        mo_values = {
            'origin': origin,
            'product_id': product_id.id,
            'product_description_variants': values.get('product_description_variants'),
            'product_qty': product_uom._compute_quantity(product_qty, bom.product_uom_id) if bom else product_qty,
            'product_uom_id': bom.product_uom_id.id if bom else product_uom.id,
            'location_src_id': self.location_src_id.id or self.picking_type_id.default_location_src_id.id or location_dest_id.id,
            'location_dest_id': location_dest_id.id,
            'mrp_type_id':bom.mrp_type_id.id,
            'bom_id': bom.id,
            'date_deadline': date_deadline,
            'date_planned_start': date_planned,
            'date_planned_finished': fields.Datetime.from_string(values['date_planned']),
            'procurement_group_id': False,
            'propagate_cancel': self.propagate_cancel,
            'orderpoint_id': values.get('orderpoint_id', False) and values.get('orderpoint_id').id,
            'picking_type_id': self.picking_type_id.id or values['warehouse_id'].manu_type_id.id,
            'company_id': company_id.id,
            'move_dest_ids': values.get('move_dest_ids') and [(4, x.id) for x in values['move_dest_ids']] or False,
            'user_id': False,
            
        }
        # Use the procurement group created in _run_pull mrp override
        # Preserve the origin from the original stock move, if available
        if location_dest_id.warehouse_id.manufacture_steps == 'pbm_sam' and values.get('move_dest_ids') and values.get('group_id') and values['move_dest_ids'][0].origin != values['group_id'].name:
            origin = values['move_dest_ids'][0].origin
            mo_values.update({
                'name': values['group_id'].name,
                'procurement_group_id': values['group_id'].id,
                'origin': origin,
            })
        return mo_values    