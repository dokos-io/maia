import frappe

def execute():
    docs = {
        "Hors nomenclature": {
            "old": "fa fa-flag-o",
            "new": "fas fa-flag"
        },
        "Nouvelles patientes": {
            "old": "fa fa-users",
            "new": "fas fa-users"
        },
        "Recettes totales": {
            "old": "fa fa-line-chart",
            "new": "fas fa-chart-line"
        },
        "Consultations / semaine": {
            "old": "fa fa-stethoscope",
            "new": "fas fa-stethoscope"
        },
        "Rendez-vous / semaine": {
            "old": "octicon octicon-calendar",
            "new": "fas fa-calendar"
        },
        "Rapprochements en attente": {
            "old": "fa fa-calculator",
            "new": "fas fa-calculator"
        },
        "Impayés patientes": {
            "old": "fa fa-eur",
            "new": "fas fa-euro-sign"
        },
        "Impayés sécurité sociale": {
            "old": "fa fa-hourglass-end",
            "new": "fas fa-hourglass-end"
        }
    }

    for doc in docs:
        if frappe.db.get_value("Dashboard Card", doc, "icon") == docs.get(doc, {}).get("old"):
            frappe.db.set_value("Dashboard Card", doc, "icon", docs.get(doc, {}).get("new"))

        if frappe.db.get_value("Dashboard Card", doc, "timespan") == "Preregistered":
            frappe.db.set_value("Dashboard Card", doc, "timespan", "Last Year")