/* Functions to generate devices table */
request_gateway_devices_url = '/request-gateway-devices';
devices_url = '/intel-irris-added-devices';
request_sensors_url = '/request-device-sensors';

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
    gateway_devices = gateway_devices.slice(1); // remove 'Gateway' device
    length = Object.keys(gateway_devices).length;

    console.log("Number of devices in gateway = "+length);

    // push device IDs and names to list
    for (i=0; i<length; i++){
        gateway_devices_IDs.push(gateway_devices[i]['id'])
        gateway_devices_names.push(gateway_devices[i]['name'])
    }
    console.log("Gateway Device IDs : " + gateway_devices_IDs);
    console.log("Gateway Device names : " + gateway_devices_names);
    update_newDeviceSelect();
}
function update_newDeviceSelect(){
    var select = document.getElementById("new_deviceID_select")
    select.innerHTML = "";

    select.options[select.options.length] = new Option('Select a Device ID');
    for (var x = 0; x < gateway_devices_IDs.length; x++) {
                                                        //option text               //option value
        select.options[select.options.length] = new Option(gateway_devices_IDs[x], gateway_devices_IDs[x]);
    
    }
}
function showName(evt) {
    selected_value = evt.target.value;
    selected_index = evt.target.selectedIndex
    
    update_newDeviceNameSelect(); // update device name select with name of selected device id
}
function update_newDeviceNameSelect(){
    //console.log("selected device : " + selected_value);
    //console.log("selected index :" + selected_index);
    let set_deviceName = document.getElementById('new_deviceName_select');
    set_deviceName.innerHTML = "";
                                                                        //option text                           //option value
    set_deviceName.options[set_deviceName.options.length] = new Option(gateway_devices_names[selected_index -1], gateway_devices_names[selected_index -1]);
}
/* *** */

/* functions that get list of added devices and update the table */
async function getTableData() {
    const response = await fetch(devices_url);
    //console.log(response);
    data = await response.json();
    data = data.slice(1);  // remove 'defaults'

    populateTable();
    update_device_select();
}

function populateTable() {

    clearTable() // first clear table
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
active_url = 'intel-irris-active-device'
var active_device_id;
var device_sensors;
var no_sensors;
var sensor_ids;
async function getActiveID() {
    const response = await fetch(active_url);
    //console.log(response);
    active_device_id = await response.json();

    request_device_sensors(active_device_id);
}
async function request_device_sensors() {

    const response = await fetch(request_sensors_url + '?deviceID=' + active_device_id);
    var device_sensors_response = await response.json();
    device_sensors = device_sensors_response
    device_sensors_response = JSON.stringify(device_sensors_response)
    //console.log('device data : ' + device_sensors_response);

    if (device_sensors_response != '[{"status":"404"}]') { // show sensor ids if device ID exist
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
            select.options[select.options.length] = new Option(device_sensors[index]['id'])
        })
    }
}
/* *** */
var dropdowns_updated = false
function foo() {
    if (dropdowns_updated != true){
        getGatewayDevices();
        getTableData(); //update devices table
        getActiveID(); //update sensor select options based on active device
    }
    dropdowns_updated = true // prevent refreshing dropdowns when an option is selected
    setTimeout(foo, 5000);
}
foo();
