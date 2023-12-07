import {load_html_texts_for_current_language, webui_texts} from './util_load_DeviceManager_html_texts.js';

window.addEventListener('onload', load_html_texts_for_current_language("intel_irris_device_manager_page"));
document.getElementById('new_deviceName_select').addEventListener('change', showID);
document.getElementById('iiwa_add_device').addEventListener('submit', make_AddDevice_HttpPOSTRequest);
document.getElementById('iiwa_remove_device').addEventListener('submit', make_DeleteDevice_HttpDELETERequest);

const request_gateway_devices_url = '/wazigate_devices';
const get_iiwa_devices = '/devices';

const deviceHttpPOSTRequest_url = '/devices/';
const deviceHttpDELETERequest_url = '/devices/';

var thisPage_webui_texts = {};
const thisPage_webui_texts_list = 'intel_irris_device_manager_page';

var gateway_devices;
var gateway_devices_IDs = [];
var gateway_devices_names = [];
var selected_value;
var selected_index;

var data;

const iiwa_headers = {
	'Content-Type': 'application/json'
};

/* ****  Function(s) for Web UI language setting **** */
export function load_other_device_manager_text_contents(){
	thisPage_webui_texts = webui_texts;
	//console.log(thisPage_webui_texts)
	
	load_table_texts();
	load_new_device_form();
	load_remove_a_device_form();	
}

function load_table_texts(){
	document.getElementById('table_heading').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['table_heading'];
	document.getElementById('table_header_deviceID').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['table_header_deviceID'];
	document.getElementById('table_header_deviceName').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['table_header_deviceName'];
	document.getElementById('table_header_sensors').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['table_header_sensors'];
}

function load_new_device_form(){
	document.getElementById('add_a_device').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['add_a_device'];

	// generate the dropdown for selecting sensor(s) structure
	var select = document.getElementById("sensors_structure");
	select.innerHTML = "";
	const select_options_value_and_id = ['1_capacitive', '1_watermark', '2_watermark'];
	const select_options = [thisPage_webui_texts[thisPage_webui_texts_list]['1_capacitive'], thisPage_webui_texts[thisPage_webui_texts_list]['1_watermark'], thisPage_webui_texts[thisPage_webui_texts_list]['2_watermark']];
	const number_of_select_options = 2;
	select.options[select.options.length] = new Option(thisPage_webui_texts[thisPage_webui_texts_list]['sensors_structure']);
	
	for (var x = 0; x <= number_of_select_options; x++) {
		//option text								//option value
		select.options[select.options.length] = new Option(select_options[x], select_options[x]);
	}

	// put the "Add" text
	document.getElementById('add').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['add'];

}

function load_remove_a_device_form(){
	document.getElementById('remove_a_device').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['remove_a_device'];

	// put the "Remove" text
	document.getElementById('remove').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['remove'];
}
/* ***************************** */

// periodically call the get requests to automatically load new data on the page
var dropdowns_updated = false
function update_Device_Manager_data() {
	if (dropdowns_updated != true) {
		getGatewayDevices();
		//update devices table
		getTableData();
	}
	// prevent refreshing dropdowns when an option is selected
	dropdowns_updated = true
	setTimeout(update_Device_Manager_data, 10);
}
update_Device_Manager_data();


/* **** Function(s) for device/sensor data processing/visualization **** */

/* functions that get gateway devices and show in dropdown */
async function getGatewayDevices() {
	const response = await fetch(request_gateway_devices_url);
	//console.log(response);
	var gateway_devices = await response.json();

	length = Object.keys(gateway_devices).length;

	console.log("WaziGate device(s) available to be added to IIWA = " + length);

	// push device IDs and names to list
	for (let i = 0; i < length; i++) {
		var device_name = gateway_devices[i]['name']

		if (!device_name.match(/gateway/i)) {
			gateway_devices_IDs.push(gateway_devices[i]['id'])
			gateway_devices_names.push(gateway_devices[i]['name'])
		}
	}
	console.log("Gateway Device ID(s) : " + gateway_devices_IDs);
	console.log("Gateway Device name(s) : " + gateway_devices_names);
	update_newDeviceSelect_byName();
}

function update_newDeviceSelect_byName() {
	var select = document.getElementById('new_deviceName_select');
	select.innerHTML = "";

	select.options[select.options.length] = new Option(thisPage_webui_texts[thisPage_webui_texts_list]['select_a_device']);
	for (var x = 0; x < gateway_devices_names.length; x++) {
		//option text								//option value
		select.options[select.options.length] = new Option(gateway_devices_names[x], gateway_devices_names[x]);
	}
}

function showID(evt) {
	selected_value = evt.target.value;
	selected_index = evt.target.selectedIndex
	// update device name select with ID of selected device
	update_newDeviceIDSelect();
}

function update_newDeviceIDSelect() {
	//console.log("selected device : " + selected_value);
	//console.log("selected index :" + selected_index);
	let set_deviceID = document.getElementById('new_deviceID_select');
	set_deviceID.innerHTML = "";
	//option text														//option value
	set_deviceID.options[set_deviceID.options.length] = new Option(gateway_devices_IDs[selected_index - 1], gateway_devices_IDs[selected_index - 1]);
}

/* *** */

/* functions that get list of added devices and update the table */
async function getTableData() {
	const response = await fetch(get_iiwa_devices);
	//console.log(response);
	data = await response.json();

	populateTable();
	update_device_select();
}

function populateTable() {
	// first clear table
	clearTable()
	var table = document.getElementById('devices')

	for (var i = 0; i < data.length; i++) {
		// remove _ in sensor_structure names
		if (data[i]['sensors_structure'] == '1_capacitive') {
			data[i]['sensors_structure'] = '1 capacitive'
		}
		else if (data[i]['sensors_structure'] == '1_watermark') {
			data[i]['sensors_structure'] = '1 watermark'
		}
		else if (data[i]['sensors_structure'] == '2_watermark') {
			data[i]['sensors_structure'] = '2 watermark'
		}

		var row = `<tr>
						<td>${data[i].device_id}</td>
						<td>${data[i].device_name}</td>
						<td>${data[i].sensors_structure}</td>
			</tr>`
		table.innerHTML += row
	}
}

function clearTable() {
	var Table = document.getElementById("devices");
	Table.innerHTML = "";
}
/* *** */

/* functions that generates select option for selecting DeviceName to remove */
function update_device_select() {
	var remove_select = document.getElementById("remove_deviceName_select")
	remove_select.innerHTML = "";

	for (var x = 0; x < data.length; x++) {
		remove_select.options[remove_select.options.length] = new Option(data[x]['device_name']);

	}
}
/* *** */
/* ***************************** */


/* **** Functions that make HTTP requests **** */

// function that submits data from adding a new device form
async function make_AddDevice_HttpPOSTRequest() {
	var new_device_id = document.getElementsByName('device_id')[0].value;
	var new_device_name = document.getElementsByName('device_name')[0].value;
	var new_device_sensors_structure = document.getElementsByName('sensors_structure')[0].value;

	let new_device_configuration_body = {
		'device_name': new_device_name,
		'sensors_structure': new_device_sensors_structure
	};

	try {
		const RequestResponse = await fetch(deviceHttpPOSTRequest_url + new_device_id, {
			method: "POST",
			headers: iiwa_headers,
			body: JSON.stringify(new_device_configuration_body)
		});
		const ResponseContent = await RequestResponse.json();
		return ResponseContent;
	}
	catch (err) {
		console.error(`Error at makeHttpPOSTRequest : ${err}`);
		throw err;
	}
}

// function that submits data for removing a DeviceID
async function make_DeleteDevice_HttpDELETERequest() {
	let delete_device_name = document.getElementsByName('remove_deviceName_select')[0].value;

	// get the DeviceID of the selected DeviceName
	let delete_device_id;
	for (var x = 0; x <= data.length; x++) {
		if (data[x]['device_name'] == delete_device_name) {
			delete_device_id = data[x]['device_id'];
			break;
		}
	}
	let delete_device_body = {
		'device_id': delete_device_id
	};
	try {
		const RequestResponse = await fetch(deviceHttpDELETERequest_url + delete_device_id, {
			method: "DELETE",
			headers: iiwa_headers,
			body: JSON.stringify(delete_device_body)
		});
		const ResponseContent = await RequestResponse.json();
		return ResponseContent;
	}
	catch (err) {
		console.error(`Error at makeHttpDELETERequest : ${err}`);
		throw err;
	}
}