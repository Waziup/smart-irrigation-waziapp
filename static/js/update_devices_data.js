/* Functions to generate devices table */
request_gateway_devices_url = '/request-gateway-devices';
intel_irris_added_devices_url = '/intel-irris-added-devices';
request_device_sensors_url = '/request-device-sensors';

var gateway_devices;
var gateway_devices_IDs = []
var gateway_devices_names = []
var selected_value;
var selected_index;

var data;

/* functions that get gateway devices and show in dropdown */
async function getGatewayDevices(){
		const response = await fetch(request_gateway_devices_url);
		//console.log(response);
		var gateway_devices = await response.json();
		//console.log("Gateway devices : " + gateway_devices);
		//remove 'Gateway' device
		//gateway_devices = gateway_devices.slice(1); 
		length = Object.keys(gateway_devices).length;

		console.log("Number of devices in gateway = "+length);

		// push device IDs and names to list
		for (i=0; i<length; i++) {
				var device_name=gateway_devices[i]['name']
				
				if (!device_name.match(/gateway/i)) {
						gateway_devices_IDs.push(gateway_devices[i]['id'])
						gateway_devices_names.push(gateway_devices[i]['name'])
				}
		}
		console.log("Gateway Device IDs : " + gateway_devices_IDs);
		console.log("Gateway Device names : " + gateway_devices_names);
		update_newDeviceSelect_byName();		
}

function update_newDeviceSelect_byName(){
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

function update_newDeviceIDSelect(){
		//console.log("selected device : " + selected_value);
		//console.log("selected index :" + selected_index);
		let set_deviceID = document.getElementById('new_deviceID_select');
		set_deviceID.innerHTML = "";
																																				//option text														//option value
		set_deviceID.options[set_deviceID.options.length] = new Option(gateway_devices_IDs[selected_index -1], gateway_devices_IDs[selected_index -1]);
}

/* *** */

/* functions that get list of added devices and update the table */
async function getTableData() {
		const response = await fetch(intel_irris_added_devices_url);
		//console.log(response);
		data = await response.json();
		// remove 'defaults'
		data = data.slice(1);	 

		populateTable();
		update_device_select();
}

function populateTable() {

		// first clear table
		clearTable() 
		var table = document.getElementById('devices')

		for (var i = 0; i < data.length; i++) {
				// remove _ in sensor_structure names
				if (data[i]['sensors_structure'] == '1_capacitive'){
						data[i]['sensors_structure'] = '1 capacitive'
				}
				else if (data[i]['sensors_structure'] == '1_watermark'){
						data[i]['sensors_structure'] = '1 watermark'
				}
				else if (data[i]['sensors_structure'] == '2_watermark'){
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

/* functions that generates select option for active device (active & remove dropdowns)*/
function update_device_select() {

		var remove_select = document.getElementById("remove-device-id-select")
		remove_select.innerHTML = "";
		var select = document.getElementById("device-id-select")
		select.innerHTML = "";

		for (var x = 0; x < data.length; x++) {
				select.options[select.options.length] = new Option(data[x]['device_id']);
				remove_select.options[remove_select.options.length] = new Option(data[x]['device_id']);
		}
}
/* *** */

/* functions that GET sensor IDs of active device and display in sensor SELECT */
intel_irris_active_device_sensor_url = 'intel-irris-active-device-sensor'
request_device_data_url = 'request-device-data'
request_sensor_data_url = 'request-sensor-data'

var deviceID;
var sensorID;
var device_sensors;
var no_sensors;
var sensor_ids;

async function getActiveID() {		
		const response = await fetch(intel_irris_active_device_sensor_url);
		console.log(response);
		var active_device_sensor_id = await response.json();		 
			
		deviceID = active_device_sensor_id[0]['device_id'];
		sensorID = active_device_sensor_id[0]['sensor_id'];
		
		request_device_sensors(deviceID);
		
    const response1 = await fetch(request_device_data_url + '?deviceID=' + deviceID);
    console.log(response1);
    var device_data = await response1.json();
    
    var deviceName = device_data['name']

		if (sensorID != null) {
    		const response2 = await fetch(request_sensor_data_url + '?deviceID=' + deviceID + '&sensorID=' + sensorID);
    		console.log(response2);
    		var sensor_data = await response2.json();
    
    		var sensorName = sensor_data['name']
    		var sensorKind = sensor_data['meta']['kind']		
		}
		
		var deviceid = document.getElementById("deviceid")
		var deviceid_id = document.getElementById("deviceid_id")
		var sensorid = document.getElementById("sensorid")
		var sensorid_id = document.getElementById("sensorid_id")

		deviceid.style.display = "block";
		sensorid.style.display = "block";
		
		if (deviceID == null) {
				deviceid_id.innerHTML = "none";
				sensorid_id.innerHTML = "none";
		}
		else {
				//deviceid_id.innerHTML = deviceID;
				deviceid_id.innerHTML = deviceName + ' (' + deviceID + ')';
				sensorid_id.innerHTML = "none";
		}			

		if (sensorID == null) {
				sensorid_id.innerHTML = "none";
		}
		else {
				//sensorid_id.innerHTML = sensorID;
				sensorid_id.innerHTML = sensorName + '/' + sensorKind + ' (' + sensorID + ')';
		}
}

async function request_device_sensors(deviceID) {
		const response = await fetch(request_device_sensors_url + '?deviceID=' + deviceID);
		var device_sensors_response = await response.json();
		device_sensors = device_sensors_response
		device_sensors_response = JSON.stringify(device_sensors_response)
		//console.log('device data : ' + device_sensors_response);

		if (device_sensors_response != '[{"status":"404"}]') { 
				// show sensor ids if device ID exist
				update_sensor_select();
		}
}

function update_sensor_select() {
		if (typeof (device_sensors) != undefined || device_sensors != null) {
				no_sensors = device_sensors.length;
				//console.log("number of sensors = " + no_sensors)

				var select = document.getElementById("sensor-id-select")
				select.innerHTML = "";

				device_sensors.forEach(function (item, index) {
					select.options[select.options.length] = new Option(device_sensors[index]['name']+'/'+device_sensors[index]['meta']['kind'], device_sensors[index]['id'])
				})
		}
}
/* *** */
var dropdowns_updated = false

function foo() {
		if (dropdowns_updated != true){
				getGatewayDevices();
				//update devices table
				getTableData();
				//update sensor select options based on active device 
				getActiveID(); 
		}
		// prevent refreshing dropdowns when an option is selected
		dropdowns_updated = true 
		setTimeout(foo, 5000);
}

foo();
