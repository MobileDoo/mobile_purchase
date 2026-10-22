from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def write(self, vals):
        if 'state' not in vals:
            return super().write(vals)
        before = {order.id: order.state for order in self}
        result = super().write(vals)
        service = self.env['mobile.purchase.service']
        for order in self:
            if before.get(order.id) != order.state:
                service._mobile_on_state_change(order, before.get(order.id), order.state)
        return result
