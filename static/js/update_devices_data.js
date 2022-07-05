/* Functions to generate devices table */
devices_url = '/intel-irris-added-devices';
request_sensors = '/request-device-sensors';

var data;

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
        var row = `<tr>
                <td>${data[i].device_id}</td>
                <td>${data[i].device_name}</td>
          </tr>`
        table.innerHTML += row
    }
}
function clearTable() {
    var Table = document.getElementById("devices");
    Table.innerHTML = "";
}
/* *** */

/* function that generates select option for active device */
function update_device_select() {

    var select = document.getElementById("device-id-select")
    select.innerHTML = "";

    for (var x = 0; x < data.length; x++) {
        select.options[select.options.length] = new Option(data[x]['device_id']);
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

    const response = await fetch(request_sensors + '?deviceID=' + active_device_id);
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

function foo() {
    getTableData(); //update devices table
    getActiveID(); //update sensor select options based on active device
    setTimeout(foo, 5000);
}
foo();
