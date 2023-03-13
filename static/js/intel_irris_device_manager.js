const request_gateway_devices_url = '/wazigate_devices';
const get_iiwa_devices = '/devices';

const deviceHttpPOSTRequest_url = '/devices/'
const deviceHttpDELETERequest_url = '/devices/'

var gateway_devices;
var gateway_devices_IDs = []
var gateway_devices_names = []
var selected_value;
var selected_index;

var data;

const iiwa_headers = {
	'Content-Type': 'application/json'
};

/* functions that get gateway devices and show in dropdown */
async function getGatewayDevices() {
	const response = await fetch(request_gateway_devices_url);
	//console.log(response);
	var gateway_devices = await response.json();

	length = Object.keys(gateway_devices).length;

	console.log("WaziGate device(s) available to be added to IIWA = " + length);

	// push device IDs and names to list
	for (i = 0; i < length; i++) {
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
	var select = document.getElementById("new_deviceName_select")
	select.innerHTML = "";

	select.options[select.options.length] = new Option('Select a device by name');
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