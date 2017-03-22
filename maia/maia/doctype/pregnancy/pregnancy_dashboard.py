from frappe import _

def get_data():
    return {
        'fieldname': 'pregnancy_folder',
        'transactions': [
            {
                'label': _('Dedicated Consultations'),
                'items': ['Pregnancy Consultation', 'Early Postnatal Consultation', 'Postnatal Consultation']
             },
            {
                'label': _('Other Consultations'),
                'items': ['Birth Preparation Consultation', 'Perineum Rehabilitation Consultation']
             }
        ]
    }
            
