export const AddressDialog = (title = __('Edit address'), action={}) => {
	const fields = [
		{
			fieldtype: 'Data',
			fieldname: 'address_line1',
			label: __('Address Line 1'),
			reqd: 1
		},
		{
			fieldtype: 'Data',
			fieldname: 'address_line2',
			label: __('Address Line 2')
		},
		{
			fieldtype: 'Data',
			fieldname: 'pincode',
			label: __('Zip Code'),
			reqd: 1
		},
		{
			fieldtype: 'Data',
			fieldname: 'city',
			label: __('City'),
			reqd: 1
		},
		{
			fieldtype: 'Select',
			fieldname: 'country',
			label: __('Country'),
			reqd: 1,
			options: ["France"]
		}

	];

	let dialog = new frappe.ui.Dialog({
		title: title,
		fields: fields,
		primary_action_label: action.label || __('Update'),
		primary_action: () => {
			const form_values = dialog.get_values();
			if ("data" in action) {
				form_values["name"] = action.data.name;
			}
			action.on_submit(form_values);
		}
	});

	if ("data" in action) {
		fields.forEach(field => {
			dialog.set_value(field.fieldname, action.data[field.fieldname] || "");
		})
	}

	return dialog;
}