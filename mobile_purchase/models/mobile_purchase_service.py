"""Purchase orders on mobile: approval of orders above the company threshold.

With "Purchase Order Approval" (Settings > Purchase), confirming an order
above the amount puts it in "To Approve" until a purchase manager approves
it: managers get a push and a "to approve" list, the buyer gets a push when
it is approved or cancelled. Buttons come from the real form view, so
customer approval levels (custom buttons/states) work too.
"""
from collections import defaultdict

from odoo import _, api, models

# E-mails, PDFs, receipts and invoicing stay on the web client.
DESKTOP_ONLY_BUTTONS = {
    'object:action_rfq_send', 'object:print_quotation', 'object:action_create_invoice',
    'object:action_view_invoice', 'object:action_view_picking',
}


class MobilePurchaseService(models.AbstractModel):
    _name = 'mobile.purchase.service'
    _inherit = 'mobile.record.service'
    _description = 'Mobile Purchase Service'

    _mobile_model = 'purchase.order'
    _mobile_feature = 'purchase'
    _mobile_create_capability = None
    _mobile_scope_capabilities = {'mine': 'view', 'to_approve': 'approve'}
    _mobile_core_field_names = [
        'partner_id', 'partner_ref', 'user_id', 'date_order', 'date_approve', 'date_planned', 'origin',
        'payment_term_id', 'amount_untaxed', 'amount_tax', 'amount_total', 'currency_id', 'state',
    ]
    _mobile_list_field_names = ['name', 'partner_id', 'date_order', 'amount_total', 'currency_id', 'state', 'user_id']
    _mobile_line_field = 'order_line'
    _mobile_line_field_names = ['display_type', 'name', 'product_qty', 'product_uom', 'price_unit', 'price_subtotal']

    @api.model
    def _mobile_domain(self, scope, params):
        if scope == 'mine':
            return [('user_id', '=', self.env.uid)]
        if scope == 'to_approve':
            return [('state', '=', 'to approve')]
        return super()._mobile_domain(scope, params)

    @api.model
    def _mobile_search_domain(self, query):
        return ['|', '|', ('name', 'ilike', query), ('partner_id', 'ilike', query), ('partner_ref', 'ilike', query)]

    @api.model
    def _mobile_order(self, scope):
        return 'date_order desc, id desc'

    @api.model
    def _mobile_buttons(self, record, buttons):
        return [b for b in super()._mobile_buttons(record, buttons) if b['key'] not in DESKTOP_ONLY_BUTTONS]

    # ------------------------------------------------------------------
    # Push
    # ------------------------------------------------------------------

    @api.model
    def _mobile_approvers(self, order):
        group = self.env.ref('purchase.group_purchase_manager', raise_if_not_found=False)
        if not group:
            return self.env['res.users']
        return group.sudo().users.filtered(lambda u: not u.share and order.company_id in u.company_ids)

    @api.model
    def _mobile_on_state_change(self, order, old_state, new_state):
        """Approvers: an order waits for approval. Buyer: their order was approved / cancelled."""
        Push = self.env['mobile.push.message']
        data = {'type': 'purchase', 'model': 'purchase.order', 'res_id': order.id, 'state': new_state}
        if new_state == 'to approve':
            by_lang = defaultdict(lambda: self.env['res.users'])
            for user in self._mobile_approvers(order) - self.env.user:
                by_lang[user.lang] |= user
            for lang, users in by_lang.items():
                title, body = self.with_context(lang=lang)._mobile_push_text(order, new_state)
                Push._enqueue(users, title, body, data)
            return
        buyer = order.user_id
        if old_state == 'to approve' and new_state in ('purchase', 'cancel') and buyer and buyer != self.env.user:
            title, body = self.with_context(lang=buyer.lang)._mobile_push_text(order, new_state)
            Push._enqueue(buyer, title, body, data)

    @api.model
    def _mobile_push_text(self, order, state):
        """Texts in `self.env.lang` (the recipient's language)."""
        order = order.with_context(lang=self.env.lang)
        amount = f'{order.amount_total:,.2f} {order.currency_id.name or ""}'.strip()
        body = f'{order.name} · {order.partner_id.display_name} · {amount}'
        if state == 'to approve':
            return _('Purchase order to approve'), body
        if state == 'purchase':
            return _('Purchase order approved'), body
        return _('Purchase order cancelled'), body
