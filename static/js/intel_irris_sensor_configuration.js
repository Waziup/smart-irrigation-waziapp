var intel_irris_sensor_configurations_url = 'intel-irris-sensor-configurations';
var intel_irris_active_device_url = 'intel-irris-active-device';
var request_device_sensors_url = 'request-device-sensors';

var active_device = document.getAnimations("active_device");
var active_device_id = document.getElementById("active_device_id");

var sensor_case;
var configs;
var number_of_configurations;
var sensor_config_data;
var selected_sensor_id;
var selected_temperature_source;

/* sensor configuration parameters */
var sensor_id;
var sensor_type;
var sensor_age;
var sensor_max;
var sensor_min;
var soil_type;
var soil_irrigation_type;
var soil_salinity;
var soil_bulk_density;
var soil_temperature_value;
var soil_temperature_device_id;
var soil_temperature_sensor_id;
var plant_crop;
var plant_sub_type;
var plant_planting_date;
var weather_region;

var global_soil_salinity;
var global_soil_bulk_density;

/* *** */

async function inform_on_configurations() {
		const response = await fetch(intel_irris_sensor_configurations_url);
		console.log(response);
		sensor_config_data = await response.json();
		configs = sensor_config_data['sensors'];

		number_of_configurations = Object.keys(configs).length;
		console.log('number_of_configurations made = ' + number_of_configurations);

		var no_config_made = document.getElementById("no_config_made");
		
		if (number_of_configurations == 0) {
				no_config_made.style.display = "block";
		}
		else if (number_of_configurations != 0) {
				no_config_made.style.display = "none";
		}
}

/* *** */

/* functions that GET sensor IDs of active device and display in radio */
var active_device_id;
var sensors_list;
var no_sensors;
var sensor_ids;

async function getActiveID() {
		const response = await fetch(intel_irris_active_device_url);
		//console.log(response);
		active_device_id = await response.json();

		request_device_sensors(active_device_id);
}

async function request_device_sensors() {
		const response = await fetch(request_device_sensors_url + '?deviceID=' +active_device_id);
		//console.log(response);
		sensors_list_response = await response.json();
		sensors_list = sensors_list_response;
		sensors_list_response = JSON.stringify(sensors_list_response);

		if (sensors_list_response != '[{"status":"404"}]') { // show sensor ids if device ID exist
				update_sensor_select();
		}
}

function update_sensor_select() {
		if (typeof (sensors_list) != undefined) {

				no_sensors = sensors_list.length;
				//console.log("number of sensors = " + no_sensors);

				var sensor_radio = document.getElementById('select_sensor_radio');
				sensor_radio.innerHTML = "";

				for (j = 0; j <= no_sensors; j++) {
						var sensor_name = sensors_list[j]['name']
						
						if (sensor_name.match(/humidity/i)) {
								var sensor_id = sensors_list[j]['id'];
								var newRadio = document.createElement('input');
								newRadio.type = 'radio';
								newRadio.id = sensor_id;
								newRadio.name = "select_sensor_radio";
								newRadio.value = sensor_id;
								var newLabel = document.createElement('label');
								//var t = document.createTextNode(sensor_id);
								var t = document.createTextNode(sensors_list[j]['name']+'/'+sensors_list[j]['meta']['kind']+' ('+sensor_id+')');
								newLabel.setAttribute("for", sensor_id);
								sensor_radio.appendChild(newRadio);
								sensor_radio.appendChild(t);
								sensor_radio.appendChild(document.createElement('br'));
						}

						newRadio.addEventListener('click', function () {
								document.getElementById('soil_temperatureForm').style.display = 'block';
								check_selected_sensor_id();
						})
				}
		}
}

/* function gets the sensor case of the active device_id */

/* DO WE NEED THIS FUNCTION?

function getDevice_SensorCase() {

		fetch('intel-irris-added-devices')
				.then((response) => {
						return response.json();
				})
				.then((data) => {
						added_devices = data;

						added_devices = added_devices.slice(1);	 // remove 'defaults'
						number_of_added = Object.keys(added_devices).length; // number of added devices

						if (number_of_added != 0) {
								for (i = 0; i <= number_of_added; i++) {
										if (added_devices[i]['device_id'] == active_device_id) {
												sensor_case = added_devices[i]['sensors_structure']
										}
								}
						}		
				})
}
*/

function check_selected_sensor_id() {
		const radioButtons = document.querySelectorAll('input[name="select_sensor_radio"]');
		for (const radioButton of radioButtons) {
				radioButton.addEventListener('change', showSelected);
		}
		function showSelected(e) {
				console.log(e);
				if (this.checked) {
						console.log("you have checked "+ `${this.value}`);
						selected_sensor_id = this.value;
						get_configuration_data();

				}
		}
}

/* functions that update parameters accordion with configuration of checked sensor */
function get_configuration_data() { //obtain global variables and sensor configurations
		// reset variables
		sensor_id = '';
		sensor_type = '';
		sensor_age = '0';
		sensor_max = '';
		sensor_min = '0';
		soil_type = 'undefined';
		soil_irrigation_type = 'undefined';
		soil_salinity ='';
		soil_bulk_density = '';
		soil_temperature_value = '';
		soil_temperature_device_id = '';
		soil_temperature_sensor_id = '';				
		plant_crop = 'undefined';
		plant_sub_type = 'undefined';
		plant_planting_date = 'undefined';
		weather_region = 'undefined';

		global_soil_salinity = '';
		global_soil_bulk_density = '';
		
		global_soil_salinity = sensor_config_data['globals']['soil_salinity'];
		global_soil_bulk_density = sensor_config_data['globals']['soil_bulk_density'];

		if (global_soil_salinity == 'disabled' || typeof(global_soil_salinity) == "undefined") {
				global_soil_salinity = '';
		}
		if (global_soil_bulk_density == 'disabled' || typeof(global_soil_salinity) == "undefined") {
				global_soil_bulk_density = '';
		}

		sensor_id = selected_sensor_id;
	
		if (number_of_configurations != 0) { // can only display config data if config exists
				for (x = 0; x < number_of_configurations; x++) {	
						if (sensor_config_data['sensors'][x]['device_id'] == active_device_id && sensor_config_data['sensors'][x]['sensor_id'] == sensor_id ) {
								//sensor_id = sensor_config_data['sensors'][x]['sensor_id'];
								sensor_type = sensor_config_data['sensors'][x]['value']['sensor_type'];
								sensor_age = sensor_config_data['sensors'][x]['value']['sensor_age'];
								sensor_max = sensor_config_data['sensors'][x]['value']['sensor_max'];
								sensor_min = sensor_config_data['sensors'][x]['value']['sensor_min'];
								soil_type = sensor_config_data['sensors'][x]['value']['soil_type'];
								soil_irrigation_type = sensor_config_data['sensors'][x]['value']['soil_irrigation_type'];
								soil_salinity = sensor_config_data['sensors'][x]['value']['soil_salinity'];
								soil_bulk_density = sensor_config_data['sensors'][x]['value']['soil_bulk_density'];																 
								soil_temperature_value = sensor_config_data['sensors'][x]['soil_temperature_source']['soil_temperature_value'];
								soil_temperature_device_id = sensor_config_data['sensors'][x]['soil_temperature_source']['soil_temperature_device_id'];
								soil_temperature_sensor_id = sensor_config_data['sensors'][x]['soil_temperature_source']['soil_temperature_sensor_id'];
								plant_crop = sensor_config_data['sensors'][x]['value']['plant_crop'];
								plant_sub_type = sensor_config_data['sensors'][x]['value']['plant_sub_type'];
								plant_planting_date = sensor_config_data['sensors'][x]['value']['plant_planting_date'];
								weather_region = sensor_config_data['sensors'][x]['value']['weather_region'];
								break;
						}
				}
		}
		
		if (typeof(sensor_age) == "undefined" || sensor_age == "undefined") {
				sensor_age = '0';
		}
		if (typeof(sensor_max) == "undefined" || sensor_max == "undefined") {
				sensor_max = '';
		}
		if (typeof(sensor_min) == "undefined" || sensor_min == "undefined") {
				sensor_min = '0';
		}
		if (typeof(soil_temperature_value) == "undefined" || soil_temperature_value == "undefined") {
				soil_temperature_value = '';
		}
		if (typeof(soil_temperature_device_id) == "undefined" || soil_temperature_device_id == "undefined") {
				soil_temperature_device_id = '';
		}
		if (typeof(soil_temperature_sensor_id) == "undefined" || soil_temperature_sensor_id == "undefined") {
				soil_temperature_sensor_id = '';
		}

		//console.log('sensor_id = ' + sensor_id);
		console.log('=================================');
		console.log('device_id = ' + active_device_id);
		console.log('sensor_id = ' + sensor_id);
		console.log('sensor_type = ' + sensor_type);
		console.log('sensor_age = ' + sensor_age);
		console.log('sensor_max = ' + sensor_max);
		console.log('sensor_min = ' + sensor_min);		
		console.log('soil_type = ' + soil_type);
		console.log('soil_irrigation_type = ' + soil_irrigation_type);
		console.log('soil_salinity = ' + soil_salinity);
		console.log('soil_bulk_density = ' + soil_bulk_density);
		console.log('soil_temperature_value = ' + soil_temperature_value);
		console.log('soil_temperature_device_id = ' + soil_temperature_device_id);
		console.log('soil_temperature_sensor_id = ' + soil_temperature_sensor_id);		
		console.log('plant_crop = ' + plant_crop);
		console.log('plant_sub_type = ' + plant_sub_type);
		console.log('plant_planting_date = ' + plant_planting_date);
		console.log('weather_region = ' + weather_region);		
		console.log('=================================');
		
		update_accordion_parameters();
}

function update_accordion_parameters() {
		if (soil_temperature_value == '' && soil_temperature_device_id == '' && soil_temperature_sensor_id == ''){
				document.getElementById('p_currentSource').style.display = "none";
				document.getElementById('soil_temperature_value').value = '';
				document.getElementById('soil_temperature_device_id').value = '';
				document.getElementById('soil_temperature_sensor_id').value = '';
				
				//selected_temperature_source = 'user'; //default option
				//show_temperature_source_fields();
				check_selected_temperature_source();
		}
		/* update sensor id select with selected id (select)*/
		let sensor_id_select = document.getElementById("sensor_id_select");
		sensor_id_select.innerHTML = "";
		sensor_id_select.options[sensor_id_select.options.length] = new Option(sensor_id);
		/* *** */
		/* show current sensor type (radio)*/
		let sensor_type_radios = document.getElementsByName('sensor_type');
		let current_sensor_type = sensor_type;

		for (let t = 0, length = sensor_type_radios.length; t < length; t++) {
				if (sensor_type_radios[t].value == current_sensor_type) {
						sensor_type_radios[t].checked = true;
						// only one radio can be logically checked, don't check the rest
						//break;
				}
				else
						sensor_type_radios[t].checked = false;
		}
		
		// clear radio if no option is configured
		/*
		if (current_sensor_type == ''){ 
				document.querySelector('input[name="sensor_type"]:checked').checked = false;
		}
		*/
		/* *** */
		/* show current sensor age (input)*/
		document.querySelector('input[name="sensor_age"]').value = sensor_age;
		/* *** */
		/* show current max value (input)*/
		document.querySelector('input[name="sensor_max"]').value = sensor_max;
		/* *** */
		/* show current min value (input)*/
		document.querySelector('input[name="sensor_min"]').value = sensor_min;
		/* *** */
		/* show current soil type (select)*/
		soil_type_select = document.getElementById('soil_type');
		soil_type_select.value = soil_type;
				
		/* *** */
		/* show current irrigation type (radio)*/
		let soil_irrigation_type_radios = document.getElementsByName('soil_irrigation_type');
		let current_soil_irrigation_type = soil_irrigation_type;

		for (let k = 0, length = soil_irrigation_type_radios.length; k < length; k++) {
				if (soil_irrigation_type_radios[k].value == current_soil_irrigation_type) {
						soil_irrigation_type_radios[k].checked = true;
						// only one radio can be logically checked, don't check the rest
						break;
				}
		}
		if (current_soil_irrigation_type == ''){ // clear radio if no option is configured
				document.querySelector('input[name="soil_irrigation_type"]:checked').checked = false;
		}
		/* *** */
		/* show current soil salinity (input)*/
		document.querySelector('input[name="soil_salinity"]').value = soil_salinity;
		/* *** */
		/* show current soil bulk density (input)*/
		document.querySelector('input[name="soil_bulk_density"]').value = soil_bulk_density;
		/* *** */
		/* show current plant/crop (select)*/

		let current_plant_crop = document.getElementById('plant_crop');
		current_plant_crop.value = plant_crop;

		/* *** */
		/* show current plant sub type (select)*/
		let current_plant_sub_type = document.getElementById('plant_sub_type');
		current_plant_sub_type.value = plant_sub_type;

		/* *** */
		/* show current planting date (date input)*/
		let current_plant_planting_date = document.getElementById('plant_planting_date');
		current_plant_planting_date.value = plant_planting_date;

		/* **** */
		/* show current weather parameters (select)*/
		let current_weather_region = document.getElementById('weather_region');
		current_weather_region.value = weather_region;

		/* *** */
		/* show current soil temperature value (radio)*/
		if (soil_temperature_value != '') {
				document.getElementById('p_currentSource').style.display = "block";
				document.getElementById('span_currentSource').innerHTML = "user input";

				selected_temperature_source = 'user';
				
				let temp_source_radios = document.getElementsByName('soil_temp_source');
				temp_source_radios[0].checked = true;
								
				show_temperature_source_fields();
		}
		/* **** */
		/* show current soil temperature device and sensor id source (radio)*/
		if (soil_temperature_device_id != '' && soil_temperature_sensor_id != '') {

				document.getElementById('p_currentSource').style.display = "block";
				document.getElementById('span_currentSource').innerHTML = "a real sensor";
				document.getElementById('soil_temperature_device_id').value = soil_temperature_device_id;
				document.getElementById('soil_temperature_sensor_id').value = soil_temperature_sensor_id;

				selected_temperature_source = 'sensor';
				
				let temp_source_radios = document.getElementsByName('soil_temp_source');
				temp_source_radios[1].checked = true;
								
				show_temperature_source_fields();
		}
		/* *** */
		/* Handle selecting soil temperature source */
		check_selected_temperature_source();
		/* *** */
}
/* *** */
function check_selected_temperature_source() {
		const radioButtons = document.querySelectorAll('input[name="soil_temp_source"]');
		for (const radioButton of radioButtons) {
				radioButton.addEventListener('change', showSelected);
		}
		function showSelected(e) {
				//console.log(e);
				if (this.checked) {
						//console.log("you have checked source : " + `${this.value}`)
						selected_temperature_source = this.value;
						show_temperature_source_fields();
				}
		}
}

// shows an input for sensor value or device_id && sensor_id
function show_temperature_source_fields() {

		if (selected_temperature_source == 'user') {
				document.getElementById('show_sensor_field').style.display = "block";
				document.getElementById('soil_temperature_value').style.display = "block";
				document.getElementById('soil_temperature_value').value = soil_temperature_value;
				document.getElementById('soil_temperature_source').style.display = "none";

				// if user input is checked clear values in device and sensor id
				document.getElementById('soil_temperature_device_id').value = '';
				document.getElementById('soil_temperature_sensor_id').value = '';
		}
		else if (selected_temperature_source == 'sensor') {
				document.getElementById('show_sensor_field').style.display = "block";
				document.getElementById('soil_temperature_value').style.display = "none";
				document.getElementById('soil_temperature_source').style.display = "block";
				document.getElementById('soil_temperature_device_id').value = soil_temperature_device_id;
				document.getElementById('soil_temperature_sensor_id').value = soil_temperature_sensor_id;

				// if sensor input is checked clear values in soil temperature input field
				document.getElementById('soil_temperature_value').value = '';
		}
}
/* *** */
var sensorIDRadio_updated = false;

function foo() {
		if (!sensorIDRadio_updated) {
				inform_on_configurations();
				getActiveID();
				//getDevice_SensorCase();
		}
		// prevent refreshing dropdowns when an option is selected
		sensorIDRadio_updated = true; 

		setTimeout(foo, 6000);
}

foo();