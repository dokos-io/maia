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
			title: __('Select your Activity'),
			fields: [
				{fieldname:'domain', label: __('Activity'), fieldtype:'Select',
					options: [
					    {"label": __("Midwife"), "value": "Midwife"}
					], "default": "Midwife", reqd:1},
			],
			help: __('Select the nature of your activity.'),
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
			title: __("The Practice"),
			icon: "fa fa-building",
			fields: [
				{fieldname:'company_name',
					label: frappe.wiz.domain==='Education' ?
					 	__('Institute Name') : __('Practice Name'),
					fieldtype:'Data', reqd:1},
				{fieldname:'company_abbr',
					label: frappe.wiz.domain==='Education' ?
					 	__('Institute Abbreviation') : __('Company Abbreviation'),
				        fieldtype:'Data'},
			        {fieldtype: "Section Break"},
			        {fieldname: "company_email", label: __("Practice Email Address"), fieldtype:'Data'},
			        {fieldname:'company_siret',
					label: __('SIRET N°'),
				        fieldtype:'Data'},
			        {fieldtype: "Column Break"},
			        {fieldname: "company_phone", label: __("Practice Phone Number"), fieldtype:'Data'},
			        {fieldname:'rpps_number',
					label: __('RPPS N°'),
				        fieldtype:'Data'},
			        {fieldtype: "Section Break"},
				{fieldname:'bank_account', label: __('The Name of your Bank'), fieldtype:'Data', reqd:1},
			        {fieldtype: "Section Break"},
			        {fieldname:'chart_of_accounts', label: __('Chart of Accounts'),
					options: "", fieldtype: 'Select'},
				{fieldname:'fy_start_date', label:__('Financial Year Start Date'), fieldtype:'Date',
				reqd:1},
				{fieldname:'fy_end_date', label:__('Financial Year End Date'), fieldtype:'Date',
				reqd:1},
			],
			help: (frappe.wiz.domain==='Education' ?
				__('The name of the institute for which you are setting up this system.'):
				__('The name of the practice for which you are setting up this system. Contact our team if you have any question.')),

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
									field.df.hidden = 0;
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
			title: __("Your Brand"),
			help: __('Upload your letterhead and logo. (you can edit them later).'),
			fields: [
				{fieldtype:"Attach Image", fieldname:"attach_letterhead",
					label: __("Attach a Letterhead"),
					description: __("Keep it web friendly 900px (w) by 100px (h)"),
					is_private: 0
				},
				{fieldtype: "Column Break"},
				{fieldtype:"Attach Image", fieldname:"attach_logo",
					label:__("Attach a Logo"),
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

		taxes: {
			domains: ['manufacturing', 'services', 'retail', 'distribution'],
			icon: "fa fa-money",
			title: __("Add Taxes"),
			help: __("List your tax heads (e.g. VAT, Customs etc; they should have unique names) and their standard rates. This will create a standard template, which you can edit and add more later."),
			"fields": [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<4; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break"},
						{fieldtype:"Data", fieldname:"tax_"+ i, label:__("Tax") + " " + i,
							placeholder:__("e.g. VAT") + " " + i},
						{fieldtype:"Column Break"},
						{fieldtype:"Float", fieldname:"tax_rate_" + i, label:__("Rate (%)"), placeholder:__("e.g. 5")},
					]);
				}
			},
			css_class: "two-column"
		},

		customers: {
			domains: ['manufacturing', 'services', 'retail', 'distribution'],
			icon: "fa fa-group",
			title: __("Your Customers"),
			help: __("List a few of your customers. They could be organizations or individuals."),
			fields: [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<6; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break"},
						{fieldtype:"Data", fieldname:"customer_" + i, label:__("Customer") + " " + i,
							placeholder:__("Customer Name")},
						{fieldtype:"Column Break"},
						{fieldtype:"Data", fieldname:"customer_contact_" + i,
							label:__("Contact Name") + " " + i, placeholder:__("Contact Name")}
					])
				}
				slide.fields[1].reqd = 1;
			},
			css_class: "two-column"
		},

		suppliers: {
			domains: ['manufacturing', 'services', 'retail', 'distribution'],
			icon: "fa fa-group",
			title: __("Your Suppliers"),
			help: __("List a few of your suppliers. They could be organizations or individuals."),
			fields: [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<6; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break"},
						{fieldtype:"Data", fieldname:"supplier_" + i, label:__("Supplier")+" " + i,
							placeholder:__("Supplier Name")},
						{fieldtype:"Column Break"},
						{fieldtype:"Data", fieldname:"supplier_contact_" + i,
							label:__("Contact Name") + " " + i, placeholder:__("Contact Name")},
					])
				}
				slide.fields[1].reqd = 1;
			},
			css_class: "two-column"
		},

		items: {
			domains: ['manufacturing', 'services', 'retail', 'distribution'],
			icon: "fa fa-barcode",
			title: __("Your Products or Services"),
			help: __("List your products or services that you buy or sell. Make sure to check the Item Group, Unit of Measure and other properties when you start."),
			fields: [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<6; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break", show_section_border: true},
						{fieldtype:"Data", fieldname:"item_" + i, label:__("Item") + " " + i,
							placeholder:__("A Product or Service")},
						{fieldtype:"Select", label:__("Group"), fieldname:"item_group_" + i,
							options:[__("Products"), __("Services"),
								__("Raw Material"), __("Consumable"), __("Sub Assemblies")],
							"default": __("Products")},
						{fieldtype:"Select", fieldname:"item_uom_" + i, label:__("UOM"),
							options:[__("Unit"), __("Nos"), __("Box"), __("Pair"), __("Kg"), __("Set"),
								__("Hour"), __("Minute"), __("Litre"), __("Meter"), __("Gram")],
							"default": __("Unit")},
						{fieldtype: "Check", fieldname: "is_sales_item_" + i, label:__("We sell this Item"), default: 1},
						{fieldtype: "Check", fieldname: "is_purchase_item_" + i, label:__("We buy this Item")},
						{fieldtype:"Column Break"},
						{fieldtype:"Currency", fieldname:"item_price_" + i, label:__("Rate")},
						{fieldtype:"Attach Image", fieldname:"item_img_" + i, label:__("Attach Image"), is_private: 0},
					])
				}
				slide.fields[1].reqd = 1;

				// dummy data
				slide.fields.push({fieldtype: "Section Break"});
				slide.fields.push({fieldtype: "Check", fieldname: "add_sample_data",
					label: __("Add a few sample records"), "default": 1});
				slide.fields.push({fieldtype: "Check", fieldname: "setup_website",
					label: __("Setup a simple website for my organization"), "default": 1});
			},
			css_class: "two-column"
		},

		program: {
			domains: ["education"],
			title: __("Program"),
			help: __("Example: Masters in Computer Science"),
			fields: [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<6; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break", show_section_border: true},
						{fieldtype:"Data", fieldname:"program_" + i, label:__("Program") + " " + i, placeholder: __("Program Name")},
					])
				}
				slide.fields[1].reqd = 1;
			},
			css_class: "single-column"
		},

		course: {
			domains: ["education"],
			title: __("Course"),
			help: __("Example: Basic Mathematics"),
			fields: [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<6; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break", show_section_border: true},
						{fieldtype:"Data", fieldname:"course_" + i, label:__("Course") + " " + i,  placeholder: __("Course Name")},
					])
				}
				slide.fields[1].reqd = 1;
			},
			css_class: "single-column"
		},


		instructor: {
			domains: ["education"],
			title: __("Instructor"),
			help: __("People who teach at your organisation"),
			fields: [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<6; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break", show_section_border: true},
						{fieldtype:"Data", fieldname:"instructor_" + i, label:__("Instructor") + " " + i,  placeholder: __("Instructor Name")},
					])
				}
				slide.fields[1].reqd = 1;
			},
			css_class: "single-column"
		},

		room: {
			domains: ["education"],
			title: __("Room"),
			help: __("Classrooms/ Laboratories etc where lectures can be scheduled."),
			fields: [],
			before_load: function(slide) {
				slide.fields = [];
				for(var i=1; i<4; i++) {
					slide.fields = slide.fields.concat([
						{fieldtype:"Section Break", show_section_border: true},
						{fieldtype:"Data", fieldname:"room_" + i, label:__("Room") + " " + i},
						{fieldtype:"Column Break"},
						{fieldtype:"Int", fieldname:"room_capacity_" + i, label:__("Room") + " " + i + " Capacity"},
					])
				}
				slide.fields[1].reqd = 1;
			},
			css_class: "two-column"
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

	/*if (!(frappe.boot.limits && frappe.boot.limits.users===1)) {
		frappe.wiz.add_slide(maia.wiz.users);
	}*/

	/*frappe.wiz.welcome_page = "#welcome-to-maia";*/
	
});
