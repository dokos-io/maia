<template>
	<div>
		<div class="row py-5">
			<div class="col-12 col-md-4 pt-3 pt-md-0">
				<span>{{ __("Midwife") }}</span>
				<v-select :options="practitioners_names" v-model="selected_practitioner"></v-select>
			</div>
			<div class="col-12 col-md-4 pt-3 pt-md-0" v-show="this.show_categories">
				<span>{{ __("Category") }}</span>
				<v-select :options="appointment_groups" v-model="selected_appointment_category"></v-select>
			</div>
			<div class="col-12 col-md-4 pt-3 pt-md-0" v-show="this.show_appointment_types">
				<span>{{ __("Appointment Type") }}</span>
				<v-select :options="appointment_types" v-model="selected_appointment_type"></v-select>
			</div>
		</div>
		<div class="row card mb-5 appointment-description" v-show="appointment_description">
			<div class="col-12 py-2">
				<div v-html="appointment_description"></div>
			</div>
		</div>
		<div class="row">
			<FullCalendar
				v-show="show_calendar"
				eventClassName='booking-calendar'
				ref="fullCalendar"
				:defaultView="defaultView"
				:header="{
					left: 'dayGridWeek,dayGridDay',
					center: 'title',
					right: 'prev,today,next',
				}"
				:plugins="calendarPlugins"
				:weekends="calendarWeekends"
				:events="getAvailableSlots"
				:locale="locale"
				:buttonText="buttonText"
				:noEventsMessage="noEventsMessage"
				:selectAllow="selectAllow"
				@eventClick="eventClick"
				:validRange="validRange"
				:defaultDate="defaultDate"
				timeZone="local"
			/>
			<div class="appointment-modal" v-if="!show_calendar && selected_slot && !loading">
				<div class="appointment-modal-close" @click="cancelEventSelection"><i class="fas fa-times"></i></div>
				<div class="appointment-modal-header">
					<h2 class="appointment-modal-date">{{ formatted_date(selected_slot.start) }}</h2>
					<h3 class="appointment-modal-time">{{ formatted_time(selected_slot.start) }} - {{ formatted_time(selected_slot.end) }}</h3>
				</div>
				<div class="appointment-modal-header">
					<h2 class="appointment-modal-appointment-type">{{ selected_appointment_type }}</h2>
					<h3 v-if="is_group_appointment" class="appointment-modal-seats-left">{{ seats_left }} {{ seats_left === 1 ? __("Remaining seat") : __("Remaining seats") }}</h3>
				</div>
				<div class="form">
					<div class="form-box">
						<div class="form-fields">
							<textarea id="message" class="form-input" rows="3" name="message" :placeholder="__('Your message')" v-model="message"></textarea>
						</div>
					</div>
					<button class="form-button" @click="submitEvent" :disabled="btn_disabled">{{ btn_disabled ? __("Confirmation...") : __("Confirm") }}</button>
				</div>
			</div>
			<div class="appointment-modal" v-if="!show_calendar && !selected_slot && next_date && !loading">
				<div v-if="next_date_status === 200">
					<div class="appointment-modal-header">
						<h2 class="appointment-modal-title">{{ __("The next available slot is on:") }}</h2>
						<h2 class="appointment-modal-date">{{ formatted_date(next_date) }}</h2>
					</div>
					<button class="form-button" @click="goToNextDate">{{ __("See this date") }}</button>
				</div>
				<div v-else>
					<div class="appointment-modal-close" @click="goToNextDate"><i class="fas fa-times"></i></div>
					<div class="appointment-modal-header">
						<h2 class="appointment-modal-title pt-5">{{ __('No additional slots available for this appointment type') }}</h2>
					</div>
				</div>
			</div>
			<div class="mx-auto fa-3x" v-show="loading">
				<i class="fas fa-spinner fa-pulse"></i>
			</div>
		</div>
	</div>
</template>

<script>
import FullCalendar from '@fullcalendar/vue';
import dayGridPlugin from '@fullcalendar/daygrid';
import vSelect from 'vue-select';

export default {
    name: 'AppointmentCalendar',
	components: {
		FullCalendar,
		vSelect
	},
	data() {
		return {
			error: null,
			reference: "Item Booking",
			buttonText: {
				today: __("Today"),
				dayGridWeek: __("Week"),
				dayGridDay: __("Day")

			},
			calendarPlugins: [
				dayGridPlugin
			],
			locale: 'fr',
			slots: [],
			defaultDate: moment().add(1,'d').format("YYYY-MM-DD"),
			loading: false,
			noEventsMessage: __("No events to display"),
			practitioners: [],
			selected_practitioner: null,
			selected_appointment_category: null,
			selected_appointment_type: null,
			selected_slot: null,
			next_date: null,
			next_date_status: null,
			message: "",
			btn_disabled: false
		}
	},
	computed: {
		selectAllow: function(selectInfo) {
			return moment().diff(selectInfo.start) <= 0
		},
		validRange: function() {
			return { start: moment().add(1,'d').format("YYYY-MM-DD") }
		},
		practitioners_names: function() {
			return this.practitioners.reduce((acc, val) => acc.concat(val.name), [])
		},
		appointment_groups: function() {
			return this.selected_practitioner ? 
			this.practitioners
				.filter(f => f.name === this.selected_practitioner)
				.reduce((acc, val) => acc.concat(val.categories), [])
			: []
		},
		appointment_types: function() {
			return (this.selected_practitioner&&this.selected_appointment_category) ? 
			this.practitioners
				.filter(f => f.name === this.selected_practitioner)
				.reduce((acc, val) => acc.concat(val.appointment_types), [])[0][this.selected_appointment_category]
				.reduce((acc, val) => acc.concat(val.name), [])
			: []
		},
		show_categories: function() {
			return this.selected_practitioner && this.appointment_groups.length
		},
		show_appointment_types: function() {
			return this.selected_practitioner && (this.selected_appointment_category || !this.appointment_groups.length)
		},
		appointment_description: function() {
			return this.selected_appointment_type ? this.practitioners
				.filter(f => f.name === this.selected_practitioner)
				.reduce((acc, val) => acc.concat(val.appointment_types), [])[0][this.selected_appointment_category]
				.filter(f => f.name === this.selected_appointment_type)[0].description
			: null
		},
		show_calendar: function() {
			return this.selected_appointment_type && !this.selected_slot && !this.next_date_status && !this.loading
		},
		is_group_appointment: function() {
			return this.selected_appointment_type ? this.practitioners
				.filter(f => f.name === this.selected_practitioner)
				.reduce((acc, val) => acc.concat(val.appointment_types), [])[0][this.selected_appointment_category]
				.filter(f => f.name === this.selected_appointment_type)[0].group_appointment
			: null
		},
		calendarWeekends: function() {
			const weekEnd = this.selected_practitioner ?  this.practitioners
				.filter(f => f.name === this.selected_practitioner)[0].week_end : 0
			return this.selected_practitioner ? 
				(weekEnd === 1 ? true : false)
			: false
		},
		defaultView: function() {
			return window.innerWidth >= 768 ? "dayGridWeek" : "dayGridDay"
		},
		seats_left() {
			return this.selected_slot ? this.selected_slot.extendedProps.seats_left : 0
		},
	},
	mounted() {
		this.getPractitioners()
	},
	watch: {
		selected_practitioner: function() {
			this.selected_appointment_category = null
			this.selected_appointment_type = null
		},
		selected_appointment_category: function() {
			this.selected_appointment_type = null
		},
		selected_appointment_type: function() {
			this.cancelEventSelection()
			this.next_date = null
			this.next_date_status = null
			const defaultDate = moment().add(1,'d').format("YYYY-MM-DD")
			this.defaultDate = defaultDate
			this.$refs.fullCalendar.getApi().gotoDate(defaultDate)
			this.$refs.fullCalendar.getApi().refetchEvents();
		}
	},
	methods: {
		getAvailableSlots(parameters, callback) {
			frappe.call(this.slotAvailabilityMethod(), {
				start: moment(parameters.start).format("YYYY-MM-DD"),
				end: moment(parameters.end).format("YYYY-MM-DD"),
				practitioner: this.selected_practitioner,
				appointment_type: this.selected_appointment_type
			}).then(result => {
				this.slots = result.message || []

				if (!this.slots.length) {
					this.loading = true
					this.getNextAvailability(parameters.start)
				}

				callback(this.slots);
			})
		},
		getPractitioners() {
			frappe.call({
				method: "maia.templates.pages.appointment.get_practitioners_and_appointment_types"
			}).then((r) => {
					this.practitioners = r.message

					if (r.message.length===1) {
						this.selected_practitioner = r.message[0].name
					}
			})
		},
		getNextAvailability(start_dt) {
			if (start_dt && this.selected_practitioner && this.selected_appointment_type) {
				frappe.call({
					method: "maia.templates.pages.appointment.get_next_availability",
					type: "GET",
					args: {
						"practitioner": this.selected_practitioner,
						"start": moment(start_dt).format("YYYY-MM-DD"),
						"appointment_type": this.selected_appointment_type,
						"is_group": this.is_group_appointment
					}
				}).then(r => {
					this.loading = false
					if (r.message.status == 200) { this.next_date = r.message.date }
					this.next_date_status = r.message.status
					if (!this.next_date) { this.next_date = this.defaultDate }
				})
			} else {
				this.loading = false
			}
		},
		eventClick(event) {
			this.selected_slot = event.event
		},
		formatted_date: function(dt) {
			return moment(dt).locale('fr').format("LL")
		},
		formatted_time: function(dt) {
			return moment(dt).locale('fr').format("LT")
		},
		cancelEventSelection() {
			this.selected_slot = null
			this.message = ""
		},
		goToNextDate: function() {
			this.next_date_status = null
			this.defaultDate = this.next_date
			this.$refs.fullCalendar.getApi().gotoDate(this.next_date)
			this.$refs.fullCalendar.getApi().refetchEvents();
		},
		slotAvailabilityMethod() {
			return this.is_group_appointment ? "maia.templates.pages.appointment.check_group_events_availabilities" : "maia.templates.pages.appointment.check_availabilities"
		},
		submitEvent() {
			this.btn_disabled = true
			frappe.call({
				method: "maia.templates.pages.appointment.submit_appointment",
				args: {
					email: frappe.session.user,
					practitioner: this.selected_practitioner,
					appointment_type: this.selected_appointment_type,
					start: moment(this.selected_slot.start).format('YYYY-MM-DD H:mm:SS'),
					end: moment(this.selected_slot.end).format('YYYY-MM-DD H:mm:SS'),
					notes: this.message
				}
			}).then(r => {
				this.btn_disabled = false
				this.$refs.fullCalendar.getApi().refetchEvents();
				this.cancelEventSelection()
				const message = r.message.appointment ? __("Thank you ! You will receive a confirmation message in a few minutes.")
					: __("An unexpected error prevented the submission of your request. Please contact your midfiwe directly.")
				const indicator = r.message.appointment ? "green" : "red"
				frappe.show_alert({ message: message, indicator:  indicator})
			})
		}
	}
}
</script>

<style lang='scss'>
@import 'node_modules/@fullcalendar/core/main';
@import 'node_modules/@fullcalendar/list/main';
@import 'frappe/public/scss/variables.scss';
@import '../../../node_modules/vue-select/src/scss/vue-select.scss';

.fc-view-container {
	background-color: #FBFBFB;
	color: #333;
}

.fc-row.fc-widget-header {
	border-bottom: 1px solid #ececec;
}

.fc-row.fc-widget-header .fc-day-header {
	font-size: 12px;
	font-weight: 600;
	color: #acacac;
}

.fc-axis {
	color: #acacac;
	font-size: 0.9em;
}

.fc-state-default {
	text-shadow: none;
	box-shadow: none;
	background-image: none;
	background-color: white;
	border-color: white;
}

.fc-button {
	text-transform: uppercase;
	font-weight: 600;
	font-size: 0.6em;
	border: 0px;
	outline: none;
	background-color: #ff8eb5;
	border-color: #ff8eb5;
}

.fc-button-primary {
	background-color: #ff8eb5;
	border-color: #ff8eb5;
}

.fc-button-primary:disabled {
	background-color: #ffc9dc;
	border-color: #ffc9dc;
}

.fc-button-primary:not(:disabled):active,
.fc-button-primary:not(:disabled).fc-button-active {
	background-color: #ff4081;
	border-color: #ff4081;
}

.fc-button:not(:disabled):hover,
.fc-button:active,
.fc-button:focus {
	background-color: #ff4081;
	border-color: #ff4081;
	outline: None;
}

.fc-content-skeleton {
	border-top: 1px solid #DDD;
}

.fc .fc-toolbar {
	padding-left: 30px;
	padding-right: 30px;
	margin-bottom: 0;
	border-bottom: 1px solid #ececec;
	min-height: 48px;
}

.fc .fc-toolbar>*>button {
	padding: 15px 17px;
	height: auto;
	outline: 0;
	margin-left: 0;
	transition: opacity 0.2s ease;
	opacity: 0.3;
}

.fc .fc-toolbar>*>button:hover {
	opacity: 1;
}

.fc .fc-toolbar>*>button.fc-state-disabled {
	transition: opacity 0s;
	opacity: 0;
}

.fc .fc-toolbar>*>button.fc-prev-button {
	padding-right: 8px;
}

.fc .fc-toolbar>*>button.fc-next-button {
	padding-left: 8px;
}

.fc .fc-toolbar>*>button .fc-icon {
	font-size: 1.1em;
}

.fc .fc-toolbar>.fc-right>button.fc-today-button {
	padding: 15px 5px;
}

.fc .fc-toolbar>.fc-right h2 {
	font-size: 13px;
	padding: 15px 0px 15px 20px;
	color: #333;
	font-weight: 600;
}

.fc-unthemed td.fc-today {
	background: white;
}

.fc-body>tr>.fc-widget-content, .fc-head>tr>.fc-widget-header {
	border: 0 !important;
}

.fc th {
	border-color: white;
	padding: 5px;
}

.fc-unthemed .fc-divider, .fc-unthemed .fc-popover .fc-header {
	background-color: transparent;
}

.empty-calendar .fc-event {
	opacity: 0;
}

.fc-event {
	transition: color .2s ease, border-color .2s ease, opacity .6s ease, box-shadow .2s ease;
	border: none;
	border-left: 2px solid #ffdde9;
	padding: 3px;
	background-color: white;
	border-radius: 3px;
	color: #333;
	margin: 1px 0;
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.07);
	cursor: pointer;
	margin-bottom: 2px;
	opacity: 1;
}

.fc-event:hover, .fc-event-clicked {
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
	border-left: 3px solid #ff4081;
	color: #ff4081;
	font-weight: 600;
	padding-left: 2px;
}

.fc-event .fc-content {
	transform: translateX(0);
	transition: transform .2s ease;
}

.fc-event:hover .fc-content {
	transform: translateX(2px);
}

.fc-event .fc-bg {
	opacity: 0;
}

.fc-day-grid-event {
	padding: 13px 15px;
	margin: 1px 0 3px;
}

.fc-day-grid-event:hover, .fc-day-grid-event-clicked {
	padding-left: 14px;
}

.fc-day-grid-event .fc-time {
	font-size: 12px;
	font-weight: 500;
}

.fc-day-grid-event .fc-title {
	padding: 0 5px 5px;
	font-size: 12px;
	font-weight: 500;
}

.fc-day-grid-event:hover .fc-time, .fc-day-grid-event-clicked .fc-time, .fc-day-grid-event:hover .fc-title, .fc-day-grid-event-clicked .fc-title {
	font-weight: 600;
}

.fc-time-grid .fc-slats .fc-minor td {
	border-top-style: none;
}

.fc-time-grid .fc-slats td {
	border-top-color: #FBFBFB;
}

.fc-time-grid .fc-slats td.fc-axis {
	border-top-color: #ececec;
}

.fc-time-grid-event.fc-short .fc-content {
	font-size: 0.7em;
	line-height: 0.2em;
}

.fc-time-grid-event.fc-short .fc-time:after {
	content: '';
}

.fc-time-grid-event .fc-time {
	font-size: 1.1em;
	padding: 5px;
}

.fc-time-grid-event .fc-title {
	padding: 0 5px 5px;
	font-weight: bold;
}

.fc-unthemed th, .fc-unthemed td, .fc-unthemed thead, .fc-unthemed tbody, .fc-unthemed .fc-divider, .fc-unthemed .fc-row, .fc-unthemed .fc-popover {
	border-color: #ececec;
}

.fc-agendaMonthly-view .fc-event {
	color: white;
}

.fc-now-indicator {
	border-color: rgba(255, 0, 0, 0.5);
}

.fc-unthemed .fc-basic-view .fc-scroller {
	padding: 5px 15px;
}

.fc-unthemed .fc-basic-view .fc-content-skeleton {
	border-top: 0px;
}

.fc-unthemed .fc-list-view .fc-scroller {
	padding: 0px 15px;
}

.fc-list-view {
	border-width: 0px;
}

.fc-list-table {
	width: 80%;
	max-width: 400px;
	margin: 0 auto;
}

.fc-unthemed .fc-list-heading td {
	background: transparent;
	border-color: transparent;
	font-size: 1.3em;
	line-height: 1em;
	padding: 20px 19px 15px 19px;
	font-weight: 500;
	color: #2e5bec;
}

.fc-unthemed .fc-list-heading td .fc-list-heading-alt {
	color: #acacac;
}

.is-small .fc-unthemed .fc-list-heading td {
	font-size: 1.1em;
}

.fc-list-item {
	display: block;
	transition: color .2s ease, border-color .2s ease, opacity .6s ease, box-shadow .2s ease;
	border: none;
	border-left: 2px solid #939393;
	padding: 3px;
	background-color: #fff;
	border-radius: 3px;
	color: #333;
	margin: 1px 0;
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.07);
	cursor: pointer;
	margin-bottom: 3px;
	font-weight: 500;
	font-size: 12px;
}

.fc-list-item:hover {
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
	border-left: 3px solid #2e5bec;
	color: #2e5bec;
	font-weight: 600;
	padding-left: 2px;
}

.fc-list-item td {
	background: transparent;
	border-color: transparent;
	transform: translateX(0);
	transition: transform .2s ease;
}

.fc-list-item:hover td {
	background: transparent;
	transform: translateX(2px);
}

.fc-list-item .fc-list-item-marker {
	display: none;
}

.fc-list-item .fc-list-item-time {
	padding-right: 0px;
	min-width: 110px;
}

.fc-list-item .fc-list-item-title a {
	font-weight: 600;
}

.fc-unthemed .fc-list-empty {
	background-color: transparent;
}

.appointment-description {
	margin-right: 0;
	margin-left: 0;
}

</style>
