{% set sagefemme = frappe.db.get_value("Professional Information Card", doc.practitioner, "first_name") %}
{% set patiente = frappe.get_doc("User", doc.user) %}
{% set type_rendez_vous = frappe.db.get_value("Maia Appointment Type", doc.appointment_type, "appointment_type") %}
{% set date = frappe.utils.formatdate(frappe.utils.get_datetime_str(doc.start_dt), "dd/MM/yyyy") %}
{% set heure = frappe.utils.get_datetime(doc.start_dt).strftime("%H:%M") %}

<div>
    <p>Bonjour {{ sagefemme or "" }},</p>
    <p>{{ patiente.first_name or "" }} {{ patiente.last_name or "" }} vient de prendre rendez-vous sur votre plateforme de réservation.</p>
    <p><strong>Date:</strong> {{ date }}</p>
    <p><strong>Heure:</strong> {{ heure }}</p>
    <p><strong>Type de Rendez-Vous:</strong> {{ type_rendez_vous or "" }}</p>
    <p><strong>Message:</strong> {{ doc.notes or "" }}</p>
    
    <p>L'Équipe Maia</p>
</div>