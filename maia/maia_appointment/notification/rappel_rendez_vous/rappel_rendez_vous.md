{% if doc.patient_record %}
{% set prenom = frappe.db.get_value("Patient Record", doc.patient_record, "patient_first_name") %}
{% else %}
{% set prenom = frappe.db.get_value("User", doc.user, "first_name") %}
{% endif %}

{% set type_rendez_vous = frappe.db.get_value("Maia Appointment Type", doc.appointment_type, "appointment_type") %}
{% set date = frappe.utils.formatdate(frappe.utils.get_datetime_str(doc.start_dt), "dd/MM/yyyy") %}
{% set heure = frappe.utils.get_datetime(doc.start_dt).strftime("%H:%M") %}

<div>
    <p>Bonjour {{ prenom }},</p>
    <p>Votre rendez-vous est toujours prévu le {{ date }}, à {{ heure }}.</p>
    <p>Si vous avez un empêchement, veuillez me l'indiquer au plus vite par retour de mail.</p>
    <p>Merci beaucoup.</p>
    <p>{{doc.practitioner }}</p>
</div>