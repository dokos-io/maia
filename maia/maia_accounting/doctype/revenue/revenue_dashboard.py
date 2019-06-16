from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'revenue',
		'non_standard_fieldnames': {
			'Payment': 'reference_name',
            'Auto Repeat': 'reference_document'
		},
		'transactions': [
			{
				'label': _('Payments'),
				'items': ['Payment']
			},
			{
				'label': _('Subscription'),
				'items': ['Auto Repeat']
			},
		]
	}
