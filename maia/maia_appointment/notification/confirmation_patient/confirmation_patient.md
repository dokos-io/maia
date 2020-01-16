{% if doc.patient_record %}
{% set prenom = frappe.db.get_value("Patient Record", doc.patient_record, "patient_first_name") %}
{% else %}
{% set prenom = frappe.db.get_value("User", doc.user, "first_name") %}
{% endif %}

{% set type_rendez_vous = frappe.db.get_value("Maia Appointment Type", doc.appointment_type, "appointment_type") %}
{% set date = frappe.utils.formatdate(frappe.utils.get_datetime_str(doc.start_dt), "dd/MM/yyyy") %}
{% set heure = frappe.utils.get_datetime(self.start_dt).strftime("%H:%M") %}
{% set lien = frappe.get_url("/login") %}

<div>
    <p>Bonjour {{ prenom or "" }},</p>
    <p>Votre rendez-vous {{ type_rendez_vous }}" est confirmé le {{ date }}, à {{ heure }}.</p>
    <p>Pour toute annulation jusqu'à 48H avant le rendez-vous, veuillez cliquer <a href={{ lien }}>ici</a>.</p>
    <p>En cas d'empêchement dans les dernières 48H, veuillez me contacter.</p>
    <p>Merci beaucoup.</p>
    <p>{{ doc.practitioner }}</p>
</div>