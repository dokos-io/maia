from frappe import _

def get_data():
	return {
		'fieldname': 'consultation',
		'transactions': [
			{
				'label': _('Revenue'),
				'items': ['Revenue']
			}
		]
	}