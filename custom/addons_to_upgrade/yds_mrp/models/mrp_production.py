from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        unavailable_components = []
        unavail_str = ''
        for move in self.move_raw_ids:
            if move.state not in ['assigned', 'done']:
                unavailable_components.append(move.product_id.name)
                unavail_str = "\n - ".join((str(i) for i in unavailable_components))

        if len(unavailable_components) > 0:
            raise ValidationError(
                _(f'Please check the total availability of the following components: \n - {unavail_str}'))

        return res


