from odoo import _, api, models


class MobileDashboardService(models.AbstractModel):
    _inherit = 'mobile.dashboard.service'

    @api.model
    def _card_defs(self):
        return super()._card_defs() + [
            {'key': 'purchase_to_approve', 'section': 'approvals', 'feature': 'purchase', 'capability': 'approve',
             'build': '_card_purchase_to_approve'},
            {'key': 'purchase_spend_month', 'section': 'purchases', 'feature': 'purchase', 'capability': 'approve',
             'build': '_card_purchase_spend_month'},
        ]

    @api.model
    def _card_purchase_to_approve(self):
        service = self.env['mobile.purchase.service']
        return self._count_card(service._mobile_model, service._mobile_scope_domain('to_approve', {}),
                                _('Purchase orders to approve'), 'cart-check', 'fuchsia',
                                tile='purchase_to_approve', tone_if_any='warn')

    @api.model
    def _card_purchase_spend_month(self):
        return self._amount_card('purchase.order', [('state', 'in', ('purchase', 'done'))], 'date_order',
                                 'amount_untaxed', _('Purchases this month'), 'cart-arrow-down', 'fuchsia', 'month',
                                 trend_months=6)
