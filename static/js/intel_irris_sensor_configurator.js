window.onload = function(){
	// check if the device/sensor IDs exist on WaziGate
	check_if_WaziGate_device_sensor();
};

const exists_on_WaziGate_devicesensor_ID_url = 'exists_on_WaziGate_devicesensor_ID'
const sensors_configurations_url = 'sensors_configurations'

const sensorConfigurationHttpPOSTRequest_Baseurl = '/devices/';

const iiwa_headers = {
	'Content-Type': 'application/json'
};


/* sensor configuration parameters variables */
var sensor_type;
var sensor_age;
var sensor_max_value;
var soil_type;
var soil_irrigation_type;
var soil_temperature_value;
var soil_temperature_device_id;
var soil_temperature_sensor_id;
var plant;
var plant_sub_type;
var planting_date;
var global_region;
var global_soil_salinity;
var global_soil_bulk_density;

var sensors_configurations_response_asJSON; // stores the current IIWA sensor config file content

var selected_temperature_source; // for HTML content 

async function check_if_WaziGate_device_sensor(){
	const exists_on_WaziGate_devicesensor_ID_response = await fetch(exists_on_WaziGate_devicesensor_ID_url + '?deviceID=' + deviceID + '&sensorID=' + sensorID);
	var exists_on_WaziGate_devicesensor_ID_response_asJSON = await exists_on_WaziGate_devicesensor_ID_response.json();
	exists_on_WaziGate_devicesensor_ID_response_asJSON = JSON.stringify(exists_on_WaziGate_devicesensor_ID_response_asJSON);
	console.log('request_ifValid_devicesensor_ID Response : ' + exists_on_WaziGate_devicesensor_ID_response_asJSON);

	// if the device/sensor ID exists, obtain it's current configuration
	if (exists_on_WaziGate_devicesensor_ID_response_asJSON == '[{"status":"200"}]'){
		// obtain all current configurations
		fetch_sensors_configurations();
	}
}

async function fetch_sensors_configurations(){
	const sensors_configurations_response = await fetch(sensors_configurations_url);
	sensors_configurations_response_asJSON = await sensors_configurations_response.json();

	const read_sensors_configurations = JSON.stringify(sensors_configurations_response_asJSON);
	//console.log("Current IIWA sensors configurations : " + read_sensors_configurations);

	get_DeviceSensorID_configuration();
}

/* get current sensor's configuration */
function get_DeviceSensorID_configuration() { 
	global_soil_salinity = sensors_configurations_response_asJSON['globals']['soil_salinity'];
	global_soil_bulk_density = sensors_configurations_response_asJSON['globals']['soil_bulk_density'];
	global_region = sensors_configurations_response_asJSON['globals']['region'];

	if (global_soil_salinity == 'undefined' || typeof (global_soil_salinity) == "undefined") {
		global_soil_salinity = '';
	}
	if (global_soil_bulk_density == 'undefined' || typeof (global_soil_salinity) == "undefined") {
		global_soil_bulk_density = '';
	}
	if (global_region == 'undefined' || typeof (global_region) == "undefined") {
		global_region = '';
	}

	number_of_configurations = sensors_configurations_response_asJSON['sensors'].length;
	//console.log("number_of_configurations = " + number_of_configurations);

	if (number_of_configurations != 0) { // can only display config data if config exists
		for (x = 0; x < number_of_configurations; x++) {
			if (sensors_configurations_response_asJSON['sensors'][x]['device_id'] == deviceID && sensors_configurations_response_asJSON['sensors'][x]['sensor_id'] == sensorID) {
				sensor_type = sensors_configurations_response_asJSON['sensors'][x]['value']['sensor_type'];
				sensor_age = sensors_configurations_response_asJSON['sensors'][x]['value']['sensor_age'];
				sensor_max_value = sensors_configurations_response_asJSON['sensors'][x]['value']['sensor_max_value'];
				soil_type = sensors_configurations_response_asJSON['sensors'][x]['value']['soil_type'];
				soil_irrigation_type = sensors_configurations_response_asJSON['sensors'][x]['value']['soil_irrigation_type'];
				soil_temperature_value = sensors_configurations_response_asJSON['sensors'][x]['soil_temperature_source']['soil_temperature_value'];
				soil_temperature_device_id = sensors_configurations_response_asJSON['sensors'][x]['soil_temperature_source']['soil_temperature_device_id'];
				soil_temperature_sensor_id = sensors_configurations_response_asJSON['sensors'][x]['soil_temperature_source']['soil_temperature_sensor_id'];
				plant = sensors_configurations_response_asJSON['sensors'][x]['value']['plant'];
				plant_sub_type = sensors_configurations_response_asJSON['sensors'][x]['value']['plant_sub_type'];
				planting_date = sensors_configurations_response_asJSON['sensors'][x]['value']['planting_date'];
				break;
			}
		}
	}

	if (typeof (sensor_age) == "undefined" || sensor_age == "undefined") {
		sensor_age = '0';
	}
	if (typeof (sensor_max_value) == "undefined" || sensor_max_value == "undefined") {
		sensor_max_value = '';
	}
	if (typeof (soil_temperature_value) == "undefined" || soil_temperature_value == "undefined") {
		soil_temperature_value = '';
	}
	if (typeof (soil_temperature_device_id) == "undefined" || soil_temperature_device_id == "undefined") {
		soil_temperature_device_id = '';
	}
	if (typeof (soil_temperature_sensor_id) == "undefined" || soil_temperature_sensor_id == "undefined") {
		soil_temperature_sensor_id = '';
	}

	console.log('=================================');
	console.log('device_id = ' + deviceID);
	console.log('sensor_id = ' + sensorID);
	console.log('sensor_type = ' + sensor_type);
	console.log('sensor_age = ' + sensor_age);
	console.log('sensor_max_value = ' + sensor_max_value);
	console.log('soil_type = ' + soil_type);
	console.log('soil_irrigation_type = ' + soil_irrigation_type);
	console.log('soil_temperature_value = ' + soil_temperature_value);
	console.log('soil_temperature_device_id = ' + soil_temperature_device_id);
	console.log('soil_temperature_sensor_id = ' + soil_temperature_sensor_id);
	console.log('plant = ' + plant);
	console.log('plant_sub_type = ' + plant_sub_type);
	console.log('planting_date = ' + planting_date);
	console.log('global_region = ' + global_region);
	console.log('global_soil_salinity = ' + global_soil_salinity);
	console.log('global_soil_bulk_density = ' + global_soil_bulk_density);
	console.log('=================================');

	update_accordion_parameters();
}

function update_accordion_parameters() {
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

	/* show current sensor age (input)*/
	document.querySelector('input[name="sensor_age"]').value = sensor_age;
	/* *** */

	/* show current max value (input)*/
	document.querySelector('input[name="sensor_max_value"]').value = sensor_max_value;
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
	if (current_soil_irrigation_type == '') { // clear radio if no option is configured
		document.querySelector('input[name="soil_irrigation_type"]:checked').checked = false;
	}
	/* *** */

	/* show current soil salinity (input)*/
	document.querySelector('input[name="global_soil_salinity"]').value = global_soil_salinity;
	/* *** */

	/* show current soil bulk density (input)*/
	document.querySelector('input[name="global_soil_bulk_density"]').value = global_soil_bulk_density;
	/* *** */
	/* show current plant/crop (select)*/

	let current_plant = document.getElementById('plant');
	current_plant.value = plant;

	/* *** */
	/* show current plant sub type (select)*/
	let current_plant_sub_type = document.getElementById('plant_sub_type');
	current_plant_sub_type.value = plant_sub_type;

	/* *** */
	/* show current planting date (date input)*/
	let current_planting_date = document.getElementById('planting_date');
	current_planting_date.value = planting_date;

	/* **** */
	/* show current weather parameters (select)*/
	let current_region = document.getElementById('global_region');
	current_region.value = global_region;

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

// function that submits form data to IIWA REST API
async function make_AddConfiguration_HttpPOSTRequest(){
	var posted_sensor_type = document.getElementsByName('sensor_type')[0].value;
	var posted_sensor_age = document.getElementsByName('sensor_age')[0].value;
	var posted_sensor_max_value = document.getElementsByName('sensor_max_value')[0].value;
	var posted_soil_type = document.getElementsByName('soil_type')[0].value;
	var posted_soil_irrigation_type = document.getElementsByName('soil_irrigation_type')[0].value;
	var posted_soil_temperature_value = document.getElementsByName('soil_temperature_value')[0].value;
	var posted_soil_temperature_device_id = document.getElementsByName('soil_temperature_device_id')[0].value;
	var posted_soil_temperature_sensor_id = document.getElementsByName('soil_temperature_sensor_id')[0].value;
	var posted_plant = document.getElementsByName('plant')[0].value;
	var posted_plant_sub_type = document.getElementsByName('plant_sub_type')[0].value;
	var posted_planting_date = document.getElementsByName('planting_date')[0].value;
	var posted_global_region = document.getElementsByName('global_region')[0].value;
	var posted_global_soil_salinity = document.getElementsByName('global_soil_salinity')[0].value;
	var posted_global_soil_bulk_density = document.getElementsByName('global_soil_bulk_density')[0].value;

	let new_sensor_configuration_body = {
		"sensor_type" : posted_sensor_type,
		"sensor_age" : posted_sensor_age,
		"sensor_max_value" : posted_sensor_max_value,
		"soil_type" : posted_soil_type,
		"soil_irrigation_type" : posted_soil_irrigation_type,
		"soil_temperature_value" : posted_soil_temperature_value,
		"soil_temperature_device_id" : posted_soil_temperature_device_id,
		"soil_temperature_sensor_id" : posted_soil_temperature_sensor_id,
		"plant" : posted_plant,
		"plant_sub_type" : posted_plant_sub_type,
		"planting_date" : posted_planting_date,
		"global_soil_salinity" : posted_global_soil_salinity,
		"global_soil_bulk_density" : posted_global_soil_bulk_density,
		"global_region" : posted_global_region
	}

	try {
        const RequestResponse = await fetch(sensorConfigurationHttpPOSTRequest_Baseurl + deviceID + '/sensors/' + sensorID, {
            method: "POST",
            headers: iiwa_headers,
            body: JSON.stringify(new_sensor_configuration_body)
        });
        const ResponseContent = await RequestResponse.json();
        return ResponseContent;
    }
    catch(err) {
        console.error(`Error at makeHttpPOSTRequest : ${err}`);
        throw err;
    }
}