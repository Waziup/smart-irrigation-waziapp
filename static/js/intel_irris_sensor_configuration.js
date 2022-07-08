var sensor_config_url = 'intel-irris-sensor-configurations';
var active_url = 'intel-irris-active-device'
var request_DeviceSensors_url = 'request-device-sensors'

var active_device = document.getAnimations("active_device");
var active_device_id = document.getElementById("active_device_id");

var sensor_case;
var configs;
var number_of_configurations;
var sensor_config_data;
var selected_sensor_id;
var selected_temperature_source;

/* sensor configuration parameters */
var global_soil_salinity;
var global_soil_bulk_density;
var sensor_id;
var sensor_type;
var sensor_age;
var sensor_max;
var sensor_min;
var region;
var soil_type;
var irrigation_type;
var crop;
var plant_sub_type;
var planting_date;
var soil_temperature_value;
var soil_temperature_device_id;
var soil_temperature_sensor_id;
/* *** */

async function inform_on_configurations() {
    const response = await fetch(sensor_config_url);
    //console.log(response);
    sensor_config_data = await response.json();
    configs = sensor_config_data['sensors']

    number_of_configurations = Object.keys(configs).length;
    //console.log('number_of_configurations made = ' + number_of_configurations);

    var no_config_made = document.getElementById("no_config_made");
    if (number_of_configurations == 0) {
        no_config_made.style.display = "block"
    }
    else if (number_of_configurations != 0) {
        no_config_made.style.display = "none";
    }
}

/* function gets the sensor case of the active device_id */
function getDevice_SensorCase() {

    fetch('intel-irris-added-devices')
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            added_devices = data;

            added_devices = added_devices.slice(1);  // remove 'defaults'
            number_of_added = Object.keys(added_devices).length; // number of added devices

            for (i = 0; i <= number_of_added; i++) {
                if (added_devices[i]['device_id'] == deviceID) {
                    sensor_case = added_devices[i]['sensors_structure']
                }
            }
        })
}
/* *** */

/* functions that GET sensor IDs of active device and display in radio */
var active_device_id;
var sensors_configs;
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
    //device_url = `http://localhost/devices/${active_device_id}/sensors`;

    const response = await fetch(request_DeviceSensors_url + '?deviceID=' +active_device_id);
    //console.log(response);
    sensors_configs_response = await response.json();
    sensors_configs = sensors_configs_response
    sensors_configs_response = JSON.stringify(sensors_configs_response)
    //console.log('device data : '+device_sensors);

    if (sensors_configs_response != '[{"status":"404"}]') { // show sensor ids if device ID exist
        update_sensor_select();
    }
}
function update_sensor_select() {
    if (typeof (sensors_configs) != undefined) {

        no_sensors = sensors_configs.length;
        //console.log("number of sensors = " + no_sensors)

        var sensor_radio = document.getElementById('select_sensor_radio');
        sensor_radio.innerHTML = "";

        for (j = 0; j <= no_sensors; j++) {
            var sensor_id = sensors_configs[j]['id'];
            var newRadio = document.createElement('input');
            newRadio.type = 'radio';
            newRadio.id = sensor_id;
            newRadio.name = "select_sensor_radio";
            newRadio.value = sensor_id;
            var newLabel = document.createElement('label');
            var t = document.createTextNode(sensor_id);
            newLabel.setAttribute("for", sensor_id);
            sensor_radio.appendChild(newRadio);
            sensor_radio.appendChild(t)
            sensor_radio.appendChild(document.createElement('br'));

            newRadio.addEventListener('click', function () {
                document.getElementById('soil_temperatureForm').style.display = 'block';
                check_selected_sensor_id();
            })
        }
    }
}

function check_selected_sensor_id() {
    const radioButtons = document.querySelectorAll('input[name="select_sensor_radio"]');
    for (const radioButton of radioButtons) {
        radioButton.addEventListener('change', showSelected);
    }
    function showSelected(e) {
        //console.log(e);
        if (this.checked) {
            //console.log("you have checked "+ `${this.value}`)
            selected_sensor_id = this.value;
            get_configuration_data();

        }
    }
}

/* functions that update parameters accordion with configuration of checked sensor */
function get_configuration_data() { //obtain global variables and sensor configurations
    global_soil_salinity = sensor_config_data['globals']['global_soil_salinity']
    global_soil_bulk_density = sensor_config_data['globals']['global_soil_bulk_density']

    if (global_soil_salinity == 'disabled' || typeof(global_soil_salinity) == "undefined") {
        global_soil_salinity = '';
    }
    if (global_soil_bulk_density == 'disabled' || typeof(global_soil_salinity) == "undefined") {
        global_soil_bulk_density = '';
    }
    console.log('global_soil_salinity = ' + global_soil_salinity);
    console.log('global_soil_bulk_density = ' + global_soil_bulk_density);

    sensor_id = selected_sensor_id;
    console.log('sensor_id = ' + sensor_id);
    if (number_of_configurations != 0) { // can only display config data if config exists

        for (x = 0; x <= number_of_configurations; x++) {
            if (sensor_config_data['sensors'][x]['sensor_id'] == sensor_id) {
                //sensor_id = sensor_config_data['sensors'][x]['sensor_id'];
                sensor_type = sensor_config_data['sensors'][x]['value']['sensor_type'];
                sensor_age = sensor_config_data['sensors'][x]['value']['sensor_age'];
                sensor_max = sensor_config_data['sensors'][x]['value']['sensor_max'];
                sensor_min = sensor_config_data['sensors'][x]['value']['sensor_min'];
                region = sensor_config_data['sensors'][x]['value']['region'];
                soil_type = sensor_config_data['sensors'][x]['value']['soil_type'];
                irrigation_type = sensor_config_data['sensors'][x]['value']['irrigation_type'];
                crop = sensor_config_data['sensors'][x]['value']['crop'];
                plant_sub_type = sensor_config_data['sensors'][x]['value']['plant_sub_type'];
                planting_date = sensor_config_data['sensors'][x]['value']['planting_date'];

                soil_temperature_value = sensor_config_data['sensors'][x]['soil_temperature_source']['soil_temperature_value'];
                soil_temperature_device_id = sensor_config_data['sensors'][x]['soil_temperature_source']['soil_temperature_device_id'];
                soil_temperature_sensor_id = sensor_config_data['sensors'][x]['soil_temperature_source']['soil_temperature_sensor_id'];

                break;
            }
            else{ // set variables to empty when sensor ID config is not found
                break;
            }
        }
    }
    if (typeof(sensor_age) == "undefined" || sensor_age == "undefined") {
        sensor_age = '';
    }
    if (typeof(sensor_max) == "undefined" || sensor_max == "undefined") {
        sensor_max = '';
    }
    if (typeof(sensor_min) == "undefined" || sensor_min == "undefined") {
        sensor_min = '';
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
    console.log('sensor_type = ' + sensor_type);
    console.log('sensor_age = ' + sensor_age);
    console.log('sensor_max = ' + sensor_max);
    console.log('sensor_min = ' + sensor_min);
    console.log('region = ' + region);
    console.log('soil_type = ' + soil_type);
    console.log('irrigation_type = ' + irrigation_type);
    console.log('crop = ' + crop);
    console.log('plant_sub_type = ' + plant_sub_type);
    console.log('planting_date = ' + planting_date);
    console.log('soil_temperature_value = ' + soil_temperature_value);
    console.log('soil_temperature_device_id = ' + soil_temperature_device_id);
    console.log('soil_temperature_sensor_id = ' + soil_temperature_sensor_id);
    update_accordion_parameters();
}

function update_accordion_parameters() {
    /* update sensor id select with selected id (select)*/
    let sensor_id_select = document.getElementById("sensor_id_select");
    sensor_id_select.innerHTML = "";
    sensor_id_select.options[sensor_id_select.options.length] = new Option(sensor_id);
    /* *** */
    /* show current sensor type (radio)*/
    let sensor_type_radios = document.getElementsByName('sensor_type');
    let current_sensor_type = sensor_type;

    for (let k = 0, length = sensor_type_radios.length; k < length; k++) {
        if (sensor_type_radios[k].value == current_sensor_type) {
            sensor_type_radios[k].checked = true;
            // only one radio can be logically checked, don't check the rest
            break;
        }
        else if (sensor_type_radios[k].value == current_sensor_type){
            break;
        }
    }
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
    let irrigation_type_radios = document.getElementsByName('irrigation_type');
    let irrigationtype = irrigation_type;

    for (let k = 0, length = irrigation_type_radios.length; k < length; k++) {
        if (irrigation_type_radios[k].value == irrigationtype) {
            irrigation_type_radios[k].checked = true;
            // only one radio can be logically checked, don't check the rest
            break;
        }
    }
    /* *** */
    /* show current soil salinity (input)*/
    document.querySelector('input[name="soil_salinity"]').value = global_soil_salinity;
    /* *** */
    /* show current soil bulk density (input)*/
    document.querySelector('input[name="soil_bulk_density"]').value = global_soil_bulk_density;
    /* *** */
    /* show current plant/crop (select)*/
    let plant_crop = document.getElementById('crop');
    plant_crop.value = crop;
    /* *** */
    /* show current plant sub type (select)*/
    let sub_type = document.getElementById('plant_sub_type');
    sub_type.value = plant_sub_type;
    /* *** */
    /* show current planting date (date input)*/
    let date = document.getElementById('planting_date');
    date.value = planting_date;
    /* **** */
    /* show current weather parameters (select)*/
    let weather_region = document.getElementById('region');
    weather_region.value = region;
    /* *** */
    /* show current soil temperature value (radio)*/
    if (soil_temperature_value != '') {

        document.getElementById('p_currentSource').style.display = "block";
        document.getElementById('span_currentSource').innerHTML = "user input";

        selected_temperature_source = 'user';
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
function show_temperature_source_fields() {// shows an input for sensor value or device_id && sensor_id

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
        getDevice_SensorCase();
        getActiveID();
    }
    sensorIDRadio_updated = true; // prevent refreshing dropdowns when an option is selected

    setTimeout(foo, 6000);
}
foo();