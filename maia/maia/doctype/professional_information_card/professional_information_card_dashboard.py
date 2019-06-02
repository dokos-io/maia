from frappe import _

def get_data():
	return {
		'fieldname': 'practitioner',
		'transactions': [
			{
				'label': _('Replacement'),
				'items': ['Replacement']
			}
		]
	}
