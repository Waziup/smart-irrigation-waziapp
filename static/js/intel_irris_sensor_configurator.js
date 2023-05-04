window.onload = function(){
	// check if the device/sensor IDs exist on WaziGate
	check_if_WaziGate_device_sensor();
};

const exists_on_WaziGate_devicesensor_ID_url = 'exists_on_WaziGate_DeviceSensor_ID'
const sensors_configurations_url = 'sensors_configurations'
const sensorConfigurationHttpPOSTRequest_Base_url = '/devices/';

const iiwa_headers = {
	'Content-Type': 'application/json'
};

/* Basic/Advanced view mode variables */
var view_mode_text;
var toggleCheckbox;
var view_mode = 'basic'; // show basic parameters by default/onload

/* sensor configuration parameters variables */
var sensor_type;
var sensor_age = '0';
var sensor_max_value = '';
var sensor_min_value = '';
var soil_type = 'undefined';
var soil_irrigation_type = 'furrow';
var soil_salinity = '';
var soil_bulk_density = '';
var soil_field_capacity = '';
var soil_temperature_value = '';
var soil_temperature_device_id = '';
var soil_temperature_sensor_id = '';
var plant_category = 'undefined';
var plant_type = 'undefined';
var plant_variety = 'undefined';
var plant_planting_date;
var weather_region = 'undefined';
var weather_weekly_evaporation = '';
var weather_weekly_pluviometry = '';

var sensors_configurations_response_asJSON; // stores the current IIWA sensor config file content

var selected_temperature_source; // for HTML content 

async function check_if_WaziGate_device_sensor(){
	const exists_on_WaziGate_devicesensor_ID_response = await fetch(exists_on_WaziGate_devicesensor_ID_url + '?deviceID=' + deviceID + '&sensorID=' + sensorID);
	var exists_on_WaziGate_devicesensor_ID_response_asJSON = await exists_on_WaziGate_devicesensor_ID_response.json();
	exists_on_WaziGate_devicesensor_ID_response_asJSON = JSON.stringify(exists_on_WaziGate_devicesensor_ID_response_asJSON);
	console.log('exists_on_WaziGate_devicesensor_ID Response : ' + exists_on_WaziGate_devicesensor_ID_response_asJSON);

	// if the device/sensor ID exists, obtain it's current configuration
	if (exists_on_WaziGate_devicesensor_ID_response_asJSON == '[{"status":"200"}]'){
		// obtain all current configurations
		fetch_sensors_configurations();
	}
	// if the device/sensor ID doesn't exits on WaziGate or IIWA, inform user
	if (deviceName == 'not_iiwa_device' || exists_on_WaziGate_devicesensor_ID_response_asJSON == '[{"status":"404"}]'){
		console.log("Invalid deviceID " + deviceID + " or sensorID " + sensorID + " has been provided!");
		alert("Oops! The provided device/sensor ID doesn't seem to exist on WaziGate or IIWA!");
		// return the user back to the Dashboard page automatically
		window.location.href = "/";
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

	number_of_configurations = sensors_configurations_response_asJSON['sensors'].length;
	//console.log("number_of_configurations = " + number_of_configurations);

	if (number_of_configurations != 0) { // can only display config data if config exists
		for (x = 0; x < number_of_configurations; x++) {
			if (sensors_configurations_response_asJSON['sensors'][x]['device_id'] == deviceID && sensors_configurations_response_asJSON['sensors'][x]['sensor_id'] == sensorID) {
				sensor_type = sensors_configurations_response_asJSON['sensors'][x]['value']['sensor_type'];
				sensor_age = sensors_configurations_response_asJSON['sensors'][x]['value']['sensor_age'];
				sensor_max_value = sensors_configurations_response_asJSON['sensors'][x]['value']['sensor_max_value'];
				sensor_min_value = sensors_configurations_response_asJSON['sensors'][x]['value']['sensor_min_value'];
				soil_type = sensors_configurations_response_asJSON['sensors'][x]['value']['soil_type'];
				soil_irrigation_type = sensors_configurations_response_asJSON['sensors'][x]['value']['soil_irrigation_type'];
				soil_salinity = sensors_configurations_response_asJSON['sensors'][x]['value']['soil_salinity'];
				soil_bulk_density = sensors_configurations_response_asJSON['sensors'][x]['value']['soil_bulk_density'];
				soil_field_capacity = sensors_configurations_response_asJSON['sensors'][x]['value']['soil_field_capacity'];
				soil_temperature_value = sensors_configurations_response_asJSON['sensors'][x]['soil_temperature_source']['soil_temperature_value'];
				soil_temperature_device_id = sensors_configurations_response_asJSON['sensors'][x]['soil_temperature_source']['soil_temperature_device_id'];
				soil_temperature_sensor_id = sensors_configurations_response_asJSON['sensors'][x]['soil_temperature_source']['soil_temperature_sensor_id'];
				plant_category = sensors_configurations_response_asJSON['sensors'][x]['value']['plant_category'];
				plant_type = sensors_configurations_response_asJSON['sensors'][x]['value']['plant_type'];
				plant_variety = sensors_configurations_response_asJSON['sensors'][x]['value']['plant_variety'];
				plant_planting_date = sensors_configurations_response_asJSON['sensors'][x]['value']['plant_planting_date'];
				weather_region = sensors_configurations_response_asJSON['sensors'][x]['value']['weather_region'];
				weather_weekly_evaporation = sensors_configurations_response_asJSON['sensors'][x]['value']['weather_weekly_evaporation'];
				weather_weekly_pluviometry = sensors_configurations_response_asJSON['sensors'][x]['value']['weather_weekly_pluviometry'];
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
	if (typeof (sensor_min_value) == "undefined" || sensor_min_value == "undefined") {
		sensor_min_value = '';
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
	if (soil_salinity == 'undefined' || typeof (soil_salinity) == "undefined") {
		soil_salinity = '';
	}
	if (soil_bulk_density == 'undefined' || typeof (soil_bulk_density) == "undefined") {
		soil_bulk_density = '';
	}
	if (soil_field_capacity == 'undefined' || typeof (soil_field_capacity) == "undefined") {
		soil_field_capacity = '';
	}
	if (plant_type == 'undefined' || typeof (plant_type) == "undefined") {
		plant_type = 'undefined';
	}
	if (plant_variety == 'undefined' || typeof (plant_variety) == "undefined") {
		plant_variety = 'undefined';
	}	
	if (weather_region == 'undefined' || typeof (weather_region) == "undefined") {
		weather_region = 'undefined';
	}
	if (weather_weekly_evaporation == 'undefined' || typeof (weather_weekly_evaporation) == "undefined") {
		weather_weekly_evaporation = '';
	}
	if (weather_weekly_pluviometry == 'undefined' || typeof (weather_weekly_pluviometry) == "undefined") {
		weather_weekly_pluviometry = '';
	}

	console.log('=================================');
	console.log('device_id = ' + deviceID);
	console.log('sensor_id = ' + sensorID);
	console.log('sensor_type = ' + sensor_type);
	console.log('sensor_age = ' + sensor_age);
	console.log('sensor_max_value = ' + sensor_max_value);
	console.log('sensor_min_value = ' + sensor_min_value)
	console.log('soil_type = ' + soil_type);
	console.log('soil_irrigation_type = ' + soil_irrigation_type);
	console.log('soil_salinity = ' + soil_salinity);
	console.log('soil_bulk_density = ' + soil_bulk_density);
	console.log('soil_temperature_value = ' + soil_temperature_value);
	console.log('soil_temperature_device_id = ' + soil_temperature_device_id);
	console.log('soil_temperature_sensor_id = ' + soil_temperature_sensor_id);
	console.log('plant_category = ' + plant_category);
	console.log('plant_type = ' + plant_type);
	console.log('plant_variety = ' + plant_variety);
	console.log('plant_planting_date = ' + plant_planting_date);
	console.log('weather_region = ' + weather_region);
	console.log('weather_weekly_evaporation = ' + weather_weekly_evaporation);
	console.log('weather_weekly_pluviometry = ' + weather_weekly_pluviometry);
	console.log('=================================');

	update_accordion_parameters();
}

function update_accordion_parameters() {

	if (view_mode == 'basic'){
		//console.log("Showing basic parameters..");

		// show basic parameters only on UI
		document.getElementById('sensor_type_outer_div').style.display = 'block';
		document.getElementById('soil_type_p').style.display = 'block';
		document.getElementById('soil_irriation_type_outer_div').style.display = 'block';
		document.getElementById('soil_temperature_outer_div').style.display = 'block';
		document.getElementById('plant_type_p').style.display = 'block';
		document.getElementById('plant_planting_date_p').style.display = 'block';
		document.getElementById('weather_region_p').style.display = 'block';

		// hide advanced parameters on UI
		document.getElementById('sensor_age_p').style.display = 'none';
		document.getElementById('sensor_max_value_p').style.display = 'none';
		document.getElementById('sensor_min_value_p').style.display = 'none';
		document.getElementById('soil_salinity_p').style.display = 'none';
		document.getElementById('soil_bulk_density_p').style.display = 'none';
		document.getElementById('soil_field_capacity_p').style.display = 'none';
		document.getElementById('plant_category_p').style.display = 'none';
		document.getElementById('plant_variety_p').style.display = 'none';
		document.getElementById('weather_weekly_evaporation_p').style.display = 'none';
		document.getElementById('weather_weekly_pluviometry_p').style.display = 'none';
	}
	else if (view_mode == 'advanced'){
		//console.log("Showing advanced parameters..");

		// show advanced parameters only on UI
		document.getElementById('sensor_age_p').style.display = 'block';
		document.getElementById('sensor_max_value_p').style.display = 'block';
		document.getElementById('sensor_min_value_p').style.display = 'block';
		document.getElementById('soil_salinity_p').style.display = 'block';
		document.getElementById('soil_bulk_density_p').style.display = 'block';
		document.getElementById('soil_field_capacity_p').style.display = 'block';
		document.getElementById('plant_category_p').style.display = 'block';
		document.getElementById('plant_variety_p').style.display = 'block';
		document.getElementById('weather_weekly_evaporation_p').style.display = 'block';
		document.getElementById('weather_weekly_pluviometry_p').style.display = 'block';
		
		// hide basic parameters on UI
		document.getElementById('sensor_type_outer_div').style.display = 'none';
		document.getElementById('soil_type_p').style.display = 'none';
		document.getElementById('soil_irriation_type_outer_div').style.display = 'none';
		document.getElementById('soil_temperature_outer_div').style.display = 'none';
		document.getElementById('plant_type_p').style.display = 'none';
		document.getElementById('plant_planting_date_p').style.display = 'none';
		document.getElementById('weather_region_p').style.display = 'none';
	}

	/* show current sensor type (radio)*/
	let sensor_type_radios = document.getElementsByName('sensor_type');
	let current_sensor_type = sensor_type;

	for (let t = 0, length = sensor_type_radios.length; t < length; t++) {
		if (sensor_type_radios[t].value == current_sensor_type) {
			sensor_type_radios[t].checked = true;
			// only one radio can be logically checked, don't check the rest
			//break;
		}
		else{
			sensor_type_radios[t].checked = false;
		}
	}

	/* show current sensor age (input)*/
	document.querySelector('input[name="sensor_age"]').value = sensor_age;
	/* *** */

	/* show current max value (input)*/
	document.querySelector('input[name="sensor_max_value"]').value = sensor_max_value;
	/* *** */

	/* show current min value (input)*/
	document.querySelector('input[name="sensor_min_value"]').value = sensor_min_value;
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
	document.querySelector('input[name="soil_salinity"]').value = soil_salinity;
	/* *** */

	/* show current soil bulk density (input)*/
	document.querySelector('input[name="soil_bulk_density"]').value = soil_bulk_density;
	/* *** */

	/* show current soil field capacity (input)*/
	document.querySelector('input[name="soil_field_capacity"]').value = soil_field_capacity;
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
	if (soil_temperature_value == '' && soil_temperature_device_id == '' && soil_temperature_sensor_id == ''){
		document.getElementById('show_sensor_field').style.display = 'none';
	}
	// Handle selecting soil temperature source
	check_selected_temperature_source();
	/* *** */

	/* show current plant category (select)*/
	let current_plant_category = document.getElementById('plant_category');
	current_plant_category.value = plant_category;
	/* *** */

	/* show current plant type (select)*/
	let current_plant_type = document.getElementById('plant_type');
	current_plant_type.value = plant_type;
	/* *** */

	/* show current plant variety (select)*/
	let current_plant_variety = document.getElementById('plant_variety');
	current_plant_variety.value = plant_variety;

	/* *** */
	/* show current planting date (date input)*/
	let current_plant_planting_date = document.getElementById('plant_planting_date');
	current_plant_planting_date.value = plant_planting_date;

	/* **** */
	/* show current weather parameters (select)*/
	let current_weather_region = document.getElementById('weather_region');
	current_weather_region.value = weather_region;

	/* show current weather weekly evaporation (input)*/
	document.querySelector('input[name="weather_weekly_evaporation"]').value = weather_weekly_evaporation;
	/* *** */

	/* show current weather weekly pluviometry (input)*/
	document.querySelector('input[name="weather_weekly_pluviometry"]').value = weather_weekly_pluviometry;
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
	var posted_sensor_type = document.querySelector('input[name="sensor_type"]:checked').value;
	var posted_sensor_age = document.getElementsByName('sensor_age')[0].value;
	var posted_sensor_max_value = document.getElementsByName('sensor_max_value')[0].value;
	var posted_sensor_min_value = document.getElementsByName('sensor_min_value')[0].value;
	var posted_soil_type = document.getElementsByName('soil_type')[0].value;
	var posted_soil_irrigation_type = document.querySelector('input[name="soil_irrigation_type"]:checked').value;
	var posted_soil_salinity = document.getElementsByName('soil_salinity')[0].value;
	var posted_soil_bulk_density = document.getElementsByName('soil_bulk_density')[0].value;
	var posted_soil_field_capacity = document.getElementsByName('soil_field_capacity')[0].value;
	var posted_soil_temperature_value = document.getElementsByName('soil_temperature_value')[0].value;
	var posted_soil_temperature_device_id = document.getElementsByName('soil_temperature_device_id')[0].value;
	var posted_soil_temperature_sensor_id = document.getElementsByName('soil_temperature_sensor_id')[0].value;
	var posted_plant_category = document.getElementsByName('plant_category')[0].value;
	var posted_plant_type = document.getElementsByName('plant_type')[0].value;
	var posted_plant_variety = document.getElementsByName('plant_variety')[0].value;
	var posted_plant_planting_date = document.getElementsByName('plant_planting_date')[0].value;
	var posted_weather_region = document.getElementsByName('weather_region')[0].value;
	var posted_weather_weekly_evaporation = document.getElementsByName('weather_weekly_evaporation')[0].value;
	var posted_weather_weekly_pluviometry = document.getElementsByName('weather_weekly_pluviometry')[0].value;

	let new_sensor_configuration_body = {
		"sensor_type" : posted_sensor_type,
		"sensor_age" : posted_sensor_age,
		"sensor_max_value" : posted_sensor_max_value,
		"sensor_min_value" : posted_sensor_min_value,
		"soil_type" : posted_soil_type,
		"soil_irrigation_type" : posted_soil_irrigation_type,
		"soil_salinity" : posted_soil_salinity,
		"soil_bulk_density" : posted_soil_bulk_density,
		"soil_field_capacity" : posted_soil_field_capacity,
		"soil_temperature_value" : posted_soil_temperature_value,
		"soil_temperature_device_id" : posted_soil_temperature_device_id,
		"soil_temperature_sensor_id" : posted_soil_temperature_sensor_id,
		"plant_category" : posted_plant_category,
		"plant_type" : posted_plant_type,
		"plant_variety" : posted_plant_variety,
		"plant_planting_date" : posted_plant_planting_date,
		"weather_region" : posted_weather_region,
		"weather_weekly_evaporation" : posted_weather_weekly_evaporation,
		"weather_weekly_pluviometry" : posted_weather_weekly_pluviometry,
	}
	
	try {
        const RequestResponse = await fetch(sensorConfigurationHttpPOSTRequest_Base_url + deviceID + '/sensors/' + sensorID, {
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

// function handles basic/advanced toggle
function toggle_Basic_Advanced_view() {
	
	toggleCheckbox = document.getElementById("toggleCheckbox");
	view_mode_text = document.getElementById("view_mode");

	if (toggleCheckbox.checked == true) {
		view_mode_text.innerHTML = "advanced";
		view_mode = 'advanced';
		update_accordion_parameters();
	}
	else {
		view_mode_text.innerHTML = "basic";
		view_mode = 'basic';
		update_accordion_parameters();
	}
}

// monitor and handle fields the user changes and upate the parameter variables accordingly,
// this ensures that variables are not reset to the received configurations when hidding them

/* handle sensor_type radio click */
$(document).on('change', '#sensor_type_ul li input', function() {
	sensor_type = document.querySelector('input[name="sensor_type"]:checked').value;
});
/* *** */

/* handle sensor_age input change */
function sensor_age_updated() {
    sensor_age = document.getElementsByName('sensor_age')[0].value;
}
/* *** */

/* handle sensor_max_value input change */
function sensor_max_value_updated() {
    sensor_max_value = document.getElementsByName('sensor_max_value')[0].value;
}
/* *** */

/* handle sensor_min_value input change */
function sensor_min_value_updated() {
    sensor_min_value = document.getElementsByName('sensor_min_value')[0].value;
}
/* *** */

/* handle soil_type select change */
function soil_type_updated() {
    soil_type = document.getElementsByName('soil_type')[0].value;
}
/* *** */

/* handle soil_irrigation_type radio click */
$(document).on('change', '#soil_irrigation_type_ul li input', function() {
	soil_irrigation_type = document.querySelector('input[name="soil_irrigation_type"]:checked').value;
});
/* *** */

/* handle soil_salinity input change */
function soil_salinity_updated() {
    soil_salinity = document.getElementsByName('soil_salinity')[0].value;
}
/* *** */

/* handle soil_bulk_density input change */
function soil_bulk_density_updated() {
    soil_bulk_density = document.getElementsByName('soil_bulk_density')[0].value;
}
/* *** */

/* handle soil_field_capacity input change */
function soil_field_capacity_updated() {
    soil_field_capacity = document.getElementsByName('soil_field_capacity')[0].value;
}
/* *** */

/* handle soil_temp_source radio click */
$(document).on('change', '#soil_temperature_source_ul li input', function() {
	selected_temperature_source = document.querySelector('input[name="soil_temp_source"]:checked').value;
});
/* *** */

/* handle soil_temperature_value select change */
function soil_temperature_value_updated() {
    soil_temperature_value = document.getElementsByName('soil_temperature_value')[0].value;
}
/* *** */

/* handle soil_temperature_device_id select change */
function soil_temperature_device_id_updated() {
    soil_temperature_device_id = document.getElementsByName('soil_temperature_device_id')[0].value;
}
/* *** */

/* handle soil_temperature_sensor_id select change */
function soil_temperature_sensor_id_updated() {
    soil_temperature_sensor_id = document.getElementsByName('soil_temperature_sensor_id')[0].value;
}
/* *** */

/* handle plant_category select change */
function plant_category_updated() {
    plant_category = document.getElementsByName('plant_category')[0].value;
}
/* *** */

/* handle plant_type select change */
function plant_type_updated() {
    plant_type = document.getElementsByName('plant_type')[0].value;
    
    if (plant_type=='tomatoes' || plant_type=='potatoes' || plant_type=='watermelon' || plant_type=='artichoke')
    	{plant_category = 'vegetable';}
    if (plant_type=='maize' || plant_type=='wheat')
    	{plant_category = 'cereal';}
    if (plant_type=='citrus' || plant_type=='apple')
    	{plant_category = 'fruit_tree';}
}
/* *** */

/* handle plant_variety select change */
function plant_variety_updated() {
    plant_variety = document.getElementsByName('plant_variety')[0].value;
}
/* *** */

/* handle plant_planting_data date change */
function plant_planting_date_updated(){
	plant_planting_date = document.getElementsByName('plant_planting_date')[0].value;
}
/* *** */

/* handle weather_region input change */
function weather_region_updated() {
    weather_region = document.getElementsByName('weather_region')[0].value;
}
/* *** */

/* handle weather_weekly_evaporation input change */
function weather_weekly_evaporation_updated() {
    weather_weekly_evaporation = document.getElementsByName('weather_weekly_evaporation')[0].value;
}
/* *** */

/* handle weather_weekly_pluviometry input change */
function weather_weekly_pluviometry_updated() {
    weather_weekly_pluviometry = document.getElementsByName('weather_weekly_pluviometry')[0].value;
}
/* *** */