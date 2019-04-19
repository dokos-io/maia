// Copyright (c) 2017, DOKOS and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide('maia');

// add toolbar icon
$(document).bind('toolbar_setup', function() {
	frappe.app.name = "Maia";

	frappe.help_feedback_link = '<p><a class="text-muted" \
		href="https://forum.maia-by-dokos.fr">Feedback</a></p>'

	$('.navbar-home').html('<img class="maia-icon" src="'+
			frappe.urllib.get_base_url()+'/assets/maia/images/maia_squirrel.svg" />');

	$('[data-link="docs"]').attr("href", "https://maia-by-dokos.fr/docs")
	$('[data-link="issues"]').attr("href", "https://github.com/DOKOS-IO/maia/issues")

	var $help_menu = $('.dropdown-help ul .documentation-links');
	$help_menu.prev().remove();
	$help_menu.prev().remove();
	$help_menu.prev().remove();

	$('<li><a data-link-type="forum" href="https://forum.maia-by-dokos.fr" \
		target="_blank">'+__('User Forum')+'</a></li>').insertBefore($help_menu);
	$('<li><a href="mailto:help@dokos.io" \
		target="">'+__('Report an Issue')+'</a></li>').insertBefore($help_menu);
	$('<li><a href="https://www.cnil.fr/fr/modele/mention/affiche-dinformation-pour-un-cabinet-medical-ou-paramedical" \
		target="_blank">'+__('Affichette CNIL')+'</a></li>').insertBefore($help_menu);
	$('<li><a href="https://maia-by-dokos.fr/files/MODELE_DE_NOTE_D%E2%80%99INFORMATION_DES_USAGERS_RELATIVE_A_L%E2%80%99HEBERGEMENT_DE_DONNEES_DE_SANTE_A_CARACTERE_PERSONNEL.pdf" \
		target="_blank">'+__('Information Légale')+'</a></li>').insertBefore($help_menu);
});
