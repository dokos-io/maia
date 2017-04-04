frappe.provide("maia.wiz");

frappe.pages['setup-wizard'].on_page_load = function(wrapper) {
	if(sys_defaults.company) {
		frappe.set_route("desk");
		return;
	}
};

function load_maia_slides() {
    $.extend(maia.wiz, {
	    select_domain: {
		domains: ["all"],
		title: __('Select your Domain'),
		fields: [{
		    fieldname: 'domain',
		    label: __('Domain'),
		    fieldtype: 'Select',
		    options: [{
			"label": __("Midwife"),
			"value": "Midwife"
		    }
			     ],
		    reqd: 1
		}, ],
		help: __('Select the nature of your business.'),
			onload: function(slide) {
				slide.get_input("domain").on("change", function() {
					frappe.wiz.domain = $(this).val();
					frappe.wizard.refresh_slides();
				});
			},
			css_class: "single-column"
		},
		org: {
			domains: ["all"],
			title: __("The Organization"),
			icon: "fa fa-building",
			fields: [
				{fieldname:'company_name',
					label: __('Practice Name'),
					fieldtype:'Data', reqd:1},
				{fieldname:'company_abbr',
					label: __('Practice Abbreviation'),
				        fieldtype:'Data'},
			        {fieldname:'company_siret',
					label: __('SIRET N°'),
					fieldtype:'Data'},
				{fieldname:'bank_account', label: __('Bank Name'), fieldtype:'Data', reqd:1},
				{fieldname:'chart_of_accounts', label: __('Chart of Accounts'),
					options: "", fieldtype: 'Select'},

				// TODO remove this
				{fieldtype: "Section Break"},
				{fieldname:'fy_start_date', label:__('Financial Year Start Date'), fieldtype:'Date',
					description: __('Your financial year begins on'), reqd:1},
				{fieldname:'fy_end_date', label:__('Financial Year End Date'), fieldtype:'Date',
					description: __('Your financial year ends on'), reqd:1},
			],
			help: (frappe.wiz.domain==='Education' ?
				__('The name of the institute for which you are setting up this system.'):
				__('The name of your company for which you are setting up this system.')),

			onload: function(slide) {
				maia.wiz.org.load_chart_of_accounts(slide);
				maia.wiz.org.bind_events(slide);
				maia.wiz.org.set_fy_dates(slide);
			},

			validate: function() {
				// validate fiscal year start and end dates
				if (this.values.fy_start_date=='Invalid date' || this.values.fy_end_date=='Invalid date') {
					msgprint(__("Please enter valid Financial Year Start and End Dates"));
					return false;
				}

				if ((this.values.company_name || "").toLowerCase() == "company") {
					msgprint(__("Company Name cannot be Company"));
					return false;
				}

				return true;
			},

			css_class: "single-column",

			set_fy_dates: function(slide) {
				var country = frappe.wizard.values.country;

				if(country) {
					var fy = maia.wiz.fiscal_years[country];
					var current_year = moment(new Date()).year();
					var next_year = current_year + 1;
					if(!fy) {
						fy = ["01-01", "12-31"];
						next_year = current_year;
					}

					var year_start_date = current_year + "-" + fy[0];
					if(year_start_date > get_today()) {
						next_year = current_year
						current_year -= 1;
					}
					slide.get_field("fy_start_date").set_input(current_year + "-" + fy[0]);
					slide.get_field("fy_end_date").set_input(next_year + "-" + fy[1]);
				}

			},

			load_chart_of_accounts: function(slide) {
				var country = frappe.wizard.values.country;

				if(country) {
					frappe.call({
						method: "erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_charts_for_country",
						args: {"country": country},
						callback: function(r) {
							if(r.message) {
								slide.get_input("chart_of_accounts").empty()
									.add_options(r.message);

								if (r.message.length===1) {
									var field = slide.get_field("chart_of_accounts");
									field.set_value(r.message[0]);
									field.df.hidden = 1;
									field.refresh();
								}
							}
						}
					})
				}
			},

			bind_events: function(slide) {
				slide.get_input("company_name").on("change", function() {
					var parts = slide.get_input("company_name").val().split(" ");
					var abbr = $.map(parts, function(p) { return p ? p.substr(0,1) : null }).join("");
					slide.get_field("company_abbr").set_input(abbr.slice(0, 5).toUpperCase());
				}).val(frappe.boot.sysdefaults.company_name || "").trigger("change");

				slide.get_input("company_abbr").on("change", function() {
					if(slide.get_input("company_abbr").val().length > 5) {
						msgprint("Company Abbreviation cannot have more than 5 characters");
						slide.get_field("company_abbr").set_input("");
					}
				});

				// TODO remove this
				slide.get_input("fy_start_date").on("change", function() {
					var year_end_date =
						frappe.datetime.add_days(frappe.datetime.add_months(
							frappe.datetime.user_to_obj(slide.get_input("fy_start_date").val()), 12), -1);
					slide.get_input("fy_end_date").val(frappe.datetime.obj_to_user(year_end_date));

				});
			}
		},

		branding: {
			domains: ["all"],
			icon: "fa fa-bookmark",
			title: __("The Brand"),
			help: __('Upload your letter head and logo. (you can edit them later).'),
			fields: [
				{fieldtype:"Attach Image", fieldname:"attach_letterhead",
					label: __("Attach Letterhead"),
					description: __("Keep it web friendly 900px (w) by 100px (h)"),
					is_private: 0
				},
				{fieldtype: "Column Break"},
				{fieldtype:"Attach Image", fieldname:"attach_logo",
					label:__("Attach Logo"),
					description: __("100px by 100px"),
					is_private: 0
				},
			],

			css_class: "two-column"
		},

		users: {
			domains: ["all"],
			icon: "fa fa-money",
			title: __("Add Users"),
			help: __("Add users to your organization, other than yourself"),
			fields: [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<3; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break"},
						{fieldtype:"Data", fieldname:"user_fullname_"+ i,
							label:__("Full Name")},
						{fieldtype:"Data", fieldname:"user_email_" + i,
							label:__("Email Address"), placeholder:__("user@example.com"),
							options: "Email"},
					]);
				}
			},
		    css_class: "single-column"
		},
	});

	// Source: https://en.wikipedia.org/wiki/Fiscal_year
	// default 1st Jan - 31st Dec

	maia.wiz.fiscal_years = {
		"Afghanistan": ["12-20", "12-21"],
		"Australia": ["07-01", "06-30"],
		"Bangladesh": ["07-01", "06-30"],
		"Canada": ["04-01", "03-31"],
		"Costa Rica": ["10-01", "09-30"],
		"Egypt": ["07-01", "06-30"],
		"Hong Kong": ["04-01", "03-31"],
		"India": ["04-01", "03-31"],
		"Iran": ["06-23", "06-22"],
		"Italy": ["07-01", "06-30"],
		"Myanmar": ["04-01", "03-31"],
		"New Zealand": ["04-01", "03-31"],
		"Pakistan": ["07-01", "06-30"],
		"Singapore": ["04-01", "03-31"],
		"South Africa": ["03-01", "02-28"],
		"Thailand": ["10-01", "09-30"],
		"United Kingdom": ["04-01", "03-31"],
	};
};

frappe.wiz.on("before_load", function() {
	load_maia_slides();

	frappe.wiz.add_slide(maia.wiz.select_domain);
	frappe.wiz.add_slide(maia.wiz.org);
	frappe.wiz.add_slide(maia.wiz.branding);

	if (!(frappe.boot.limits && frappe.boot.limits.users===1)) {
		frappe.wiz.add_slide(maia.wiz.users);
	}

	if(frappe.wizard && frappe.wizard.domain && frappe.wizard.domain !== 'Education') {
		frappe.wiz.welcome_page = "#welcome-to-maia";
	}
});
