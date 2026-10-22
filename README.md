# Mobile Purchase

![Odoo 17.0](https://img.shields.io/badge/Odoo-17.0-714B67) ![License LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue) ![Version 17.0.1.0.0](https://img.shields.io/badge/version-17.0.1.0.0-informational)

> Purchase order approval (two-step validation) in the MobileDoo app.

Odoo 17 addon of [MobileDoo](https://github.com/MobileDoo) (`mobile_purchase`).

## Overview

Purchase order approval in the MobileDoo app. Buyers follow their orders; managers approve the orders that exceed the company's
approval threshold, using Odoo's real `button_approve`.

## Features

- **My purchase orders** for buyers and **Approve purchases** for managers, as two scopes of one record service.
- Order detail with **lines** (description, quantity, unit, unit price, subtotal; section and note rows rendered as headings).
- Works with *Settings > Purchase > Purchase Order Approval* (two-step validation by amount): confirming an order above the threshold
  moves it to *To Approve*, and a manager approves it from the phone.
- **Push**: managers receive "Purchase order to approve"; the buyer is told when the order is approved or cancelled.
- Management overview cards `purchase_to_approve` and `purchase_spend_month` (spend converted to the company currency at today's
  rate, so multi-currency totals are correct).
- Print, e-mail, vendor bill and receipt buttons stay on the web.

## Requirements

| | |
|---|---|
| Odoo | 17.0 (Community or Enterprise) |
| Odoo modules | `purchase` |
| MobileDoo addons | [`mobile_connector`](https://github.com/MobileDoo/mobile_connector/tree/17.0) (same branch) |
| Client | the [MobileDoo](https://github.com/MobileDoo) app for Android and iPhone |

This branch targets **Odoo 17** only; use the branch of your Odoo version.

## Installation

```bash
git clone --branch 17.0 https://github.com/MobileDoo/mobile_purchase.git
git clone --branch 17.0 https://github.com/MobileDoo/mobile_connector.git
# add the cloned folders to addons_path in odoo.conf, then:
odoo -d <database> -i mobile_purchase --stop-after-init
```

The addon is the `mobile_purchase/` folder at the root of the repository, so the repository folder itself can go on `addons_path`.

`auto_install` is set: Odoo installs `mobile_purchase` by itself as soon as all its dependencies are installed, so putting the folders on `addons_path` and updating the Apps list is enough.

To upgrade after pulling a newer version: `odoo -d <database> -u mobile_purchase --stop-after-init`.

## How it works

| Piece | Technical detail |
|---|---|
| Record service | `purchase` on `purchase.order`: scope `mine` (capability `view`, domain `user_id = uid`) and `to_approve` (`approve`, domain `state = 'to approve'`) |
| Services | `mobile.purchase.service` (`_mobile_domain`, `_mobile_search_domain`, `_mobile_buttons`, `_mobile_approvers`, `_mobile_on_state_change`, `_mobile_push_text`) |
| Routes | Generic `/records/purchase/*`; the spec carries `lines` |

### Capabilities

| Capability | Granted when |
|---|---|
| `view` | member of `purchase.group_purchase_user` |
| `approve` | member of `purchase.group_purchase_manager` (second step of the approval; also unlocks the management overview) |

Approvers notified by push are the active internal users of the manager group belonging to the order's company.

## Security

No groups, ACLs or data are added; every call runs as the signed-in user with Odoo's access rights and record rules on
`purchase.order`. Without read access to the model there is no `purchase` feature.

## Extending

Customer approval workflows change the list with `_mobile_domain('to_approve', params)`, who is notified with `_mobile_approvers(order)`,
the buttons with `_mobile_buttons(record, buttons)` and the text of the notification with `_mobile_push_text`.

```python
class MobilePurchaseService(models.AbstractModel):
    _inherit = 'mobile.purchase.service'

    @api.model
    def _mobile_domain(self, scope, params):
        if scope == 'to_approve':
            return [('state', 'in', ('to approve', 'x_waiting_director'))]
        return super()._mobile_domain(scope, params)
```

## Contributing

Issues and pull requests are welcome. Open pull requests against the branch of the Odoo version you are fixing (this one is `17.0`) and
keep the change inside the `mobile_purchase/` folder.

These repositories are published from MobileDoo's development repository, which remains the source of truth. A merged pull request is
taken back there, and the branches of the other Odoo versions are updated by the maintainers, so a fix is usually welcome even if you can
only test it on one version. `README.md` and `LICENSE` are generated at each release; changes to them are not carried back.

## License

LGPL-3: see [LICENSE](LICENSE).
