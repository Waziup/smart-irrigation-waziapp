/* Functions to generate devices table */
devices_url = '/intel-irris-added-devices';
var data;

async function getTableData() {
    const response = await fetch(devices_url);
    //console.log(response);
    data = await response.json();
    data = data.slice(1);  // remove 'defaults'

    populateTable(data);
    update_device_select();
}

function populateTable(data) {

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
    //device_url = `https://api.waziup.io/api/v2/devices/${active_device_id}/sensors`;
    device_url = `http://localhost/devices/${active_device_id}/sensors`;

    const response = await fetch(device_url);
    //console.log(response);
    device_sensors = await response.json();
    //device_sensors = JSON.stringify(device_sensors)
    //console.log('device data : '+device_sensors);

    update_sensor_select(device_sensors);
    
}
function update_sensor_select() {
    if (typeof(device_sensors) != undefined){
         
        no_sensors = device_sensors.length;
        //console.log("number of sensors = " + no_sensors)

        var select = document.getElementById("sensor-id-select")
        select.innerHTML = "";

        for (j = 0; j <= no_sensors; j++) {
            select.options[select.options.length] = new Option(device_sensors[j]['id'])       
        }   
    }
}
/* *** */

function foo() {
    getTableData();

    getActiveID();
    setTimeout(foo, 5000);
}
foo();
