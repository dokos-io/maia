frappe.pages['maia-standard-letter'].on_page_load = function(wrapper) {
	frappe.maia_standard_letter = new frappe.MaiaStandardLetter(wrapper);
	frappe.breadcrumbs.add("Maia", "Standard Letter");
}

frappe.pages['maia-standard-letter'].on_page_show = function(wrapper) {
	var route = frappe.get_route();
	if(route.length>1) {
		frappe.model.with_doc('Maia Standard Letter', route[1], function() {
			frappe.maia_standard_letter.standard_letter = frappe.get_doc('Maia Standard Letter', route[1]);
			frappe.maia_standard_letter.refresh();
		});
	} else if(frappe.route_options) {
		if(frappe.route_options.make_new) {
			var doctype = frappe.route_options.doctype;
			var name = frappe.route_options.name;
			frappe.route_options = null;
			frappe.maia_standard_letter.setup_new_print_format(doctype, name);
		} else {
			frappe.maia_standard_letter.standard_letter = frappe.route_options.doc;
			frappe.route_options = null;
			frappe.maia_standard_letter.refresh();
		}
	} else if(route.length==1 && frappe.route_history.length>1) {
		frappe.ui.toolbar.clear_cache();
	}
}

frappe.MaiaStandardLetter = class MaiaStandardLetter {
	constructor(parent) {
		this.parent = parent;
		this.make();
		this.refresh();
	}

	refresh() {
		this.custom_html_count = 0;
		if(!this.standard_letter) {
			this.show_start();
		} else {
			this.page.set_title(this.standard_letter.name);
			this.setup_print_format();
		}
	}

	make() {
		this.page = frappe.ui.make_app_page({
			parent: this.parent,
			title: __("Standard Letter"),
			single_column: true
		});

		this.page.main.css({"border-color": "transparent"});

		this.page.sidebar = $('<div class="maia-standard-letter-sidebar"></div>').appendTo(this.page.main);
		this.page.main = $('<div class="border maia-standard-letter-main" \
			style="width: calc(100% - 200px);"></div>').appendTo(this.page.main);

	}

	show_start() {
		this.page.main.html(frappe.render_template("maia_standard_letter_start", {}));
		this.page.sidebar.html("");
		this.page.clear_actions();
		this.page.set_title(__("Standard Letter Builder"));
		this.start_edit_standard_letter();
		this.start_new_standard_letter();
	}

	start_edit_standard_letter() {
		// Maia Standard Letter control
		var me = this;
		this.standard_letter_input = frappe.ui.form.make_control({
			parent: this.page.main.find(".standard-letter-selector"),
			df: {
				fieldtype: "Link",
				options: "Maia Standard Letter",
				filters: {
					maia_standard_letter: 1
				},
				label: __("Select a Standard Letter to edit"),
				only_select: true
			},
			render_input: true
		});

		// Select a doctype
		me.page.main.find(".doctype-item").on("click", function() {
			me.doctype_input = $(this).attr("data-doctype");
			me.page.main.find('.doctype-icon').removeClass("active");
			$(this).find('.doctype-icon').addClass("active");
		})

		// create a new Maia Standard Letter.
		this.page.main.find(".btn-edit-standard-letter").on("click", function() {
			var name = me.standard_letter_input.get_value();
			if(!name) return;
			frappe.model.with_doc("Maia Standard Letter", name, function(doc) {
				frappe.set_route('maia-standard-letter', name);
			});
		});
	}

	start_new_standard_letter() {
		var me = this;

		this.name_input = frappe.ui.form.make_control({
			parent: this.page.main.find(".name-selector"),
			df: {
				fieldtype: "Data",
				label: __("Name of the new Maia Standard Letter"),
			},
			render_input: true
		});

		this.page.main.find(".btn-new-standard-letter").on("click", function() {
			let doctype = me.doctype_input;
			let name = me.name_input.get_value();
			if(!(doctype && name)) {
				frappe.msgprint(__("A reference and a name are required"));
				return;
			}
			me.setup_new_print_format(doctype, name);
		});
	}

	setup_new_print_format(doctype, name) {
		var me = this;
		frappe.call({
			method: "frappe.client.insert",
			args: {
				doc: {
					doctype: "Maia Standard Letter",
					name: name,
					standard: "No",
					doc_type: doctype,
					maia_standard_letter: 1
				}
			},
			callback(r) {
				me.standard_letter = r.message;
				me.refresh();
			}
		});
	}

	setup_print_format() {
		var me = this;
		me.fields = me.get_usable_fields(me.standard_letter.doc_type)
	}

	get_usable_fields(doctype) {
		let me = this;
		frappe.model.with_doctype(doctype, function(d) {
			let excluded_fields = ['naming_series', 'letter_head', 'print_settings', 'echography', 'change_in_patient', 'customer']
			let main_fields = frappe.get_meta(doctype).fields;
			let fields = main_fields.filter(f => !excluded_fields.includes(f.fieldname));

			function get_linked_fields(value) {
				return new Promise(resolve => {
					frappe.model.with_doctype(value.options, function(doctype) {
						let field_meta = frappe.get_meta(value.options).fields;
						field_meta.forEach(f=> {
							f["reference"] = value.fieldname;
						})
						resolve(field_meta.filter(f => !excluded_fields.includes(f.fieldname)));
					})
				})
			}

			let promises = []
			main_fields.forEach(value => {
				let p = new Promise(resolve => {
					if (value.fieldtype == "Link" && value.fieldname == "patient_record" && !excluded_fields.includes(value.fieldname)) {
						get_linked_fields(value).then((result) => {
							fields.push(...result);
							resolve();
						});
					} else {
						resolve();
					}
				})
				promises.push(p);
			})
			
			Promise.all(promises).then(() => {
				me.fields = fields;
				me.setup_sidebar();
				me.render_layout();
				me.page.set_primary_action(__("Save"), function() {
					me.save_print_format();
				});
				me.page.clear_menu();
				me.page.add_menu_item(__("Start new Format"), function() {
					me.standard_letter = null;
					me.refresh();
				}, true);
				me.page.add_menu_item(__("Duplicate"), function() {
					const dialog = new frappe.ui.Dialog({
						title: __('What is the name of this Standard Letter'),
						fields: [{
							'fieldtype': 'Data',
							'label': __('Name'),
							'fieldname': 'name'
						}]
					});
					dialog.set_primary_action(__('Save'), args => {
						let new_std_letter = me.standard_letter;
						new_std_letter.name = args.name;
						new_std_letter.standard = "No";
						insert_doc(new_std_letter);
						frappe.set_route('maia-standard-letter', new_std_letter.name);
					});
					dialog.show();
				}, true);
				me.page.clear_inner_toolbar();
				me.page.add_inner_button(__("Print preview"), function() {
					if (!me.editable_text.val()) {
						frappe.msgprint(__("Your standard letter cannot be empty"));
						return;
					};
					const dialog = new frappe.ui.Dialog({
						title: __('Test your standard letter'),
						fields: [{
							'fieldtype': 'Link',
							'label': __('Reference Document'),
							'fieldname': 'reference',
							'options': me.standard_letter.doc_type
						}]
					});

					dialog.set_primary_action(__('Print'), args => {
						if (!args) return;
						let w = window.open(
							frappe.urllib.get_full_url("/api/method/maia.maia.print.download_standard_letter_pdf?"
								+ "doctype=" + encodeURIComponent(me.standard_letter.doc_type)
								+ "&name=" + encodeURIComponent(args.reference)
								+ "&template=" + encodeURIComponent(me.standard_letter.name)
						));
						if (!w) {
							frappe.msgprint(__("Please enable pop-ups")); return;
						}
					});
					dialog.show();
				});
			})
		});
	}

	setup_sidebar() {
		let me = this;
		this.page.sidebar.empty();

		function groupBy(objectArray, property) {
			return new Promise(resolve => {
				let arr = objectArray.reduce(function (acc, obj) {
					var key = obj[property];
					if (!acc[key]) {
					acc[key] = [];
					}
					acc[key].push(obj);
					return acc;
				}, {});
				resolve(arr);
			})
		}

		groupBy(me.fields, 'parent').then(fields => {
			fields['addVariables'] = [{"label": __("Midwife Name"), "function": "midwife", "fieldtype": "data", "print_hide": 0}, {"label": __("Current Date"), "function": "current_date", "fieldtype": "data", "print_hide": 0}];
			$(frappe.render_template("maia_standard_letter_sidebar", {fields: fields})).appendTo(this.page.sidebar);
		})	

		this.setup_field_filter();
		this.bind_doctypes_fields();
		this.bind_docfields();
	}

	render_layout() {
		let me = this;
		this.page.main.empty();
		this.prepare_data();
		$(frappe.render_template("maia_standard_letter_layout", { data: this.layout_data, me: this})).appendTo(this.page.main);
		this.setup_text_editor(this.data);

		this.disabled_input = frappe.ui.form.make_control({
			parent: this.page.main.find(".maia-standard-letter-disabled"),
			df: {
				fieldtype: "Check",
				label: __("Disable this Standard Letter"),
				fieldname: "disabled"
			},
			render_input: true
		});
		this.signature_input = frappe.ui.form.make_control({
			parent: this.page.main.find(".maia-standard-letter-signature"),
			df: {
				fieldtype: "Check",
				label: __("Add a signature"),
				fieldname: "signature"
			},
			render_input: true
		});
		$(this.disabled_input.input).prop("checked", me.standard_letter.disabled);
		$(this.signature_input.input).prop("checked", me.standard_letter.signature);
	}

	setup_text_editor(data) {
		this.editable_text = new EditableText({
			parent: $(this.page.main).find('.maia-standard-letter-texteditor'),
			data: data
		});
	}

	prepare_data() {
		this.layout_data = [];
		this.data = this.standard_letter.editor_data || "";
	}

	setup_field_filter() {
		var me = this;
		this.page.sidebar.find(".filter-fields").on("keyup", function() {
			var text = $(this).val();
			me.page.sidebar.find(".field-label").each(function() {
				var show = !text || $(this).text().toLowerCase().indexOf(text.toLowerCase())!==-1;
				$(this).parent().toggle(show);
			})
		});
	}

	bind_doctypes_fields() {
		let me = this;
		this.page.sidebar.on("click", ".field-doctype-label", function() {
			let dt = $(this).attr("data-fieldtype");
			me.page.sidebar.find(`[data-dtref='${dt}']`).toggleClass('hidden');
		});
	}

	bind_docfields() {
		const me = this;

		function createField(label, name, doctype, reference, dataFunction, fieldtype) {
			let linkNode = $('<span></span>');
			linkNode.text(__(label));
			linkNode.attr('data-fieldname', name);
			linkNode.attr('data-doctype', doctype);
			linkNode.attr('data-reference', reference);
			linkNode.attr('data-function', dataFunction);
			linkNode.attr('data-fieldtype', fieldtype)
			linkNode.addClass('fieldlabel');
			return linkNode[0]
		  }

		this.page.sidebar.on("click", ".field-label", function() {
			let label = $(this).text();
			let name = $(this).attr("data-fieldname");
			let doctype = $(this).attr("data-doctype");
			let reference = $(this).attr("data-reference");
			let dataFunction = $(this).attr("data-function");
			let fieldtype = $(this).attr("data-fieldtype");
			me.editable_text.input.summernote('insertNode', createField(label, name, doctype, reference, dataFunction, fieldtype));
			me.editable_text.input.summernote('pasteHTML', '&nbsp;');
		});
	}

	save_print_format() {
		let me = this;

		editor_data = this.editable_text.val();

		frappe.call({
			method: "maia.maia.page.maia_standard_letter.maia_standard_letter.save_print_format",
			args: {
				name: me.standard_letter.name,
				formatted_data: editor_data,
				doctype: me.standard_letter.doc_type,
				disabled: me.disabled_input.get_value(),
				signature: me.signature_input.get_value()
			},
			callback: function(r) {
				me.standard_letter = r.message;
				frappe.show_alert({message: __("Saved"), indicator: 'green'});
			}
		})
	}
 }


EditableText = class EditableText {

	constructor({ parent = null, data= null }) {
		this.parent = $(parent);
		this.data = data;

		this.make();
	}

	make() {
		this.setup_dom();
		this.setup_summernote();
		this.bind_events();
		if (this.data !== null) {
			this.val(this.data);
		}
	}

	setup_dom() {
		this.wrapper = $(`
			<div class="editabletext-input-wrapper">
				<div class="editabletext-input-container">
					<div class="form-control editabletext-input"></div>
				</div>
			</div>
		`);
		this.wrapper.appendTo(this.parent);
		this.input = this.parent.find('.editabletext-input');
	}

	setup_summernote() {
		const { input } = this;

		input.summernote({
			height: 300,
			toolbar: [
				['magic', ['style']],
				['style', ['bold', 'italic', 'underline', 'clear']],
				['fontsize', ['fontsize']],
				['color', ['color']],
				['para', ['ul', 'ol', 'paragraph', 'hr']],
				//['height', ['height']],
				['media', ['link', 'picture', 'camera', 'video', 'table']],
				['misc', ['fullscreen', 'codeview']]
			],
			airMode: false,
			disableDragAndDrop: true,
			icons: {
				'align': 'fa fa-align',
				'alignCenter': 'fa fa-align-center',
				'alignJustify': 'fa fa-align-justify',
				'alignLeft': 'fa fa-align-left',
				'alignRight': 'fa fa-align-right',
				'indent': 'fa fa-indent',
				'outdent': 'fa fa-outdent',
				'arrowsAlt': 'fa fa-arrows-alt',
				'bold': 'fa fa-bold',
				'caret': 'caret',
				'circle': 'fa fa-circle',
				'close': 'fa fa-close',
				'code': 'fa fa-code',
				'eraser': 'fa fa-eraser',
				'font': 'fa fa-font',
				'frame': 'fa fa-frame',
				'italic': 'fa fa-italic',
				'link': 'fa fa-link',
				'unlink': 'fa fa-chain-broken',
				'magic': 'fa fa-magic',
				'menuCheck': 'fa fa-check',
				'minus': 'fa fa-minus',
				'orderedlist': 'fa fa-list-ol',
				'pencil': 'fa fa-pencil',
				'picture': 'fa fa-image',
				'question': 'fa fa-question',
				'redo': 'fa fa-redo',
				'square': 'fa fa-square',
				'strikethrough': 'fa fa-strikethrough',
				'subscript': 'fa fa-subscript',
				'superscript': 'fa fa-superscript',
				'table': 'fa fa-table',
				'textHeight': 'fa fa-text-height',
				'trash': 'fa fa-trash',
				'underline': 'fa fa-underline',
				'undo': 'fa fa-undo',
				'unorderedlist': 'fa fa-list-ul',
				'video': 'fa fa-video-camera'
			}
		});

		this.note_editor = this.wrapper.find('.note-editor');
		this.note_editor.on('click', () => input.summernote('focus'));
	}

	reset() {
		this.val('');
	}

	destroy() {
		this.input.summernote('destroy');
	}

	bind_events() {
		//this.button.on('click', this.submit.bind(this));
	}

	val(value) {
		// Return html if no value specified
		if(value === undefined) {
			return this.input.summernote('code');
		}
		// Set html if value is specified
		this.input.summernote('code', value);
	}
};

function insert_doc(doc) {
	return frappe.call({
		method: "frappe.client.insert",
		args: {
			doc: doc
		},
		callback: function() {
			frappe.show_alert({ message: __("Saved"), indicator: 'green' }, 1);
		}
	});
}