import frappe, erpnext

from frappe import _

def get_level():
    activation_level = 0
    if frappe.db.get_single_value('System Settings', 'setup_complete'):
        activation_level = 1

    if frappe.db.count('Patient') > 5:
        activation_level += 1

    # recent login
    if frappe.db.sql('select name from tabUser where last_login > date_sub(now(), interval 2 day) limit 1'):
        activation_level += 1

    return activation_level

def get_help_messages():
    '''Returns help messages to be shown on Desktop'''
    if get_level() > 3:
        return []

    messages = []

    domain = frappe.db.get_value('Company', erpnext.get_default_company(), 'domain')

    message_settings = [
        frappe._dict(
            doctype='Patient',
            title=_('Create Patients'),
            description=_('Add your first five patients to the system'),
            action=_('Add Patient'),
            route='List/Patient',
            domain=('Midwife'),
            target=5
        ),
        frappe._dict(
            doctype='Letter Head',
            title=_('Create A Letter Head'),
            description=_('Create a Letter Head that will be printed on all your documents'),
            action=_('New Letter Head'),
            route='List/Letter Head',
            domain=('Midwife'),
            target=1
        ),
        frappe._dict(
            doctype='Professional Information Card',
            title=_('Professional Information Card'),
            description=_('Complete your Professional Information Card'),
            action=_('Professional Information Card'),
            route='List/Professional Information Card',
            domain=('Midwife'),
            target=1
        ),
        frappe._dict(
            doctype='Company',
            title=_('Company Information'),
            description=_('Complete your Company Information'),
            action=_('Company Information'),
            route='List/Company',
            domain=('Midwife'),
            target=1
        )
        ]


    for m in message_settings:
        if not m.domain or domain in m.domain:
            m.count = frappe.db.count(m.doctype)
            if m.count < m.target:
                messages.append(m)

    return messages
