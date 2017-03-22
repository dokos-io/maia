from frappe import _

def get_data():
    return {
        'fieldname': 'prenatal_interview_folder',
        'transactions': [
            {
                'label': _('Prenatal Interview'),
                'items': ['Prenatal Interview Consultation']
             },
            {
                'label': _('Birth Preparation'),
                'items': ['Birth Preparation Consultation']
             }
        ]
    }
            
