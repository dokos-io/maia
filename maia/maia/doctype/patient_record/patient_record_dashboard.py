from frappe import _

def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on interactions with this Patient. See timeline below for details'),
		'fieldname': 'patient',
		'transactions': [
			{
				'label': _('Folders'),
				'items': ['Pregnancy', 'Perineum Rehabilitation', 'Prenatal Interview', 'Gynecology']
			},
			{
				'label': _('Consultations'),
				'items': ['Pregnancy Consultation', 'Birth Preparation Consultation', 'Early Postnatal Consultation', 'Postnatal Consultation', 'Perineum Rehabilitation Consultation', 'Gynecological Consultation', 'Prenatal Interview Consultation', 'Free Consultation']
			},
                        {
				'label': _('Payments'),
				'items': ['Payment Entry']
			},
                        {
				'label': _('Free Prescriptions'),
				'items': ['Free Prescription']
			}
		]
	}
