<template>
  <div class="widget widget-card" v-if="preparedData.length">
	<img class="widget-img" :src="cardIcon">

	<div v-for="(item, index) in preparedData" :key="index">
		<div class="patient-dashboard-data">
			<span v-if="!item.value_label" class="text-muted small">{{ item.label }}</span>
			<h4 v-if="!item.value_fields" :style="{color: item.color}">{{ item.value }}</h4>
			<div v-else>
				<div v-for="(v, i) in item.value" :key="i">
					<span v-if="item.value_label" class="text-muted small">{{ v[item.value_label] }}</span>
					<h4 v-for="(w, j) in item.value_fields" :key="j" :style="{color: item.color}">{{ v[w] }}</h4>
				</div>
			</div>
		</div>
	</div>

</div>
</template>

<script>
export default {
	props: ["dashboardData", "itemName"],
	computed: {
		cardIcon: function() {
			return this.dashboardData[this.itemName]["icon"]
		},
		cardData: function() {
			return this.dashboardData[this.itemName]
		},
		preparedData: function() {
			let result = []
			Object.keys(this.cardData).forEach(value => {
				if (!["enabled", "icon"].includes(value) && this.cardData[value].hasOwnProperty("enabled")
					&& this.cardData[value]["enabled"] === 1) {
						if ((typeof this.cardData[value]["value"] === 'object' && this.cardData[value]["value"] !== null)
							&& this.cardData[value]["enabled"]===1) {
								if (Object.keys(this.cardData[value]["value"].length)) {
									result.push(this.cardData[value]);
								}
						} else if (this.cardData[value]["value"] !== null && this.cardData[value]["enabled"]===1) {
							result.push(this.cardData[value]);
						}
				} else if (!["enabled", "icon"].includes(value) && !this.cardData[value].hasOwnProperty("enabled")) {
					Object.keys(this.cardData[value]).forEach(v => {
						if (this.cardData[value][v]["value"] !== null) {
							result.push(this.cardData[value][v]);
						}
					});
				}
			})
			return result;
		}

	}
}
</script>

<style lang="scss">

.widget.widget-card {
	position: relative;
	background-color: #fff;
	padding: 15px 15px;
	margin: 7px 0px;
	box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.15);
	border-radius: 2px;
}

.widget-img {
	max-width:40px;
	height: 50px;
	position: absolute;
    top: 0px;
	right: 0px;
	padding: 3px;
}

.patient-dashboard-data {
	color: #425668;
	word-wrap: break-word;

	h4 {
		margin-top: 2px;
		font-size: 15px;
	}
}
</style>