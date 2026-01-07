from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('default_code')
    def _check_default_code(self):
        new_default_code = self.env['product.template'].search([('default_code', '=', self.default_code)])
        print('internal reference >>', new_default_code)
        if self.default_code and len(new_default_code) > 1:
            raise ValidationError(_('Internal Reference Must Be Unique'))
