from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_sales_person = fields.Boolean(string="Is Sales Person", default=False)


