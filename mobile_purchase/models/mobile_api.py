from odoo import _, api, models


class MobileApi(models.AbstractModel):
    _inherit = 'mobile.api'

    @api.model
    def _mobile_features(self):
        return super()._mobile_features() + ['purchase']

    @api.model
    def _mobile_record_services(self):
        return dict(super()._mobile_record_services(), purchase='mobile.purchase.service')

    @api.model
    def _mobile_access(self):
        access = super()._mobile_access()
        user = self.env.user
        if not self.env['purchase.order'].check_access_rights('read', raise_exception=False):
            return access
        capabilities = {
            'view': user.has_group('purchase.group_purchase_user'),
            # Second step of "Purchase Order Approval" (Settings > Purchase).
            'approve': user.has_group('purchase.group_purchase_manager'),
        }
        if any(capabilities.values()):
            access['purchase'] = capabilities
            if capabilities['approve']:
                access.setdefault('dashboard', {})['view'] = True  # the overview shows what they can manage
        return access

    @api.model
    def _mobile_home_tiles(self):
        return super()._mobile_home_tiles() + [
            {'key': 'purchase_to_approve', 'label': _('Approve purchases'), 'feature': 'purchase', 'capability': 'approve', 'sequence': 50},
            {'key': 'purchase_mine', 'label': _('My purchase orders'), 'feature': 'purchase', 'capability': 'view', 'sequence': 51},
        ]

    @api.model
    def _mobile_home_tabs(self):
        return super()._mobile_home_tabs() + [
            {'key': 'purchases', 'label': _('Purchases'), 'feature': 'purchase', 'capability': 'view', 'sequence': 70},
        ]
