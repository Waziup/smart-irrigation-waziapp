const iiwa_devices_data_url = '/devices/data'

var iiwa_devices_data; // stores device and sensor data:
var iiwa_devices_data_count = 0;
//device ID, sensor ID, device name, sensor type, last sensor value, soil type, soil condition

var iiwa_devices_data_soilCondition ='';
var html_soilCondition = '';
var iiwa_devices_valueIndex = '';
var html_valueIndex = '';
var html_valueIndex_isSet = false;
var html_sensorGraph_link = '';
var html_sensorConfigurator_link = '';

const iiwa_headers = {
	'Content-Type': 'application/json'
}

// fetches the device and sensor data for the page
async function get_iiwa_devices_data(){
    try {
        const RequestResponse = await fetch(iiwa_devices_data_url, {
            method: "GET",
            headers: iiwa_headers,
        });
        iiwa_devices_data = await RequestResponse.json();
        console.log(iiwa_devices_data);

        if (iiwa_devices_data != null){
            generate_dashboard_cards();
        }
    }
    catch(err) {
        console.error(`Error at Http GET Request : ${err}`);
        throw err;
    }
}

// this function generates the HTML content for each received device/sensor data
function generate_dashboard_cards(){
    iiwa_devices_data_count = iiwa_devices_data.length;
    
    // only generate cards when at least one data is present
    if (iiwa_devices_data_count > 0 ){ 
        // first clear the current list items before appending
        document.getElementById('dashboard_cards_ul').innerHTML = '';

        // itertate over the device data and generate new HTML card items
        // using ES 6 Back-ticks method to generate the HTML content
        for (let x = 0; x< iiwa_devices_data_count; x++){
            
            iiwa_devices_data_soilCondition = iiwa_devices_data[x]['soil_condition']
            iiwa_devices_valueIndex = iiwa_devices_data[x]['value_index']

            /* create html content for the soil condition */
            if (iiwa_devices_data_soilCondition == 'no sensor'){
                html_soilCondition = `
                    <p class="dashboard_card_text">Found no sensor!</p>
                `;

                html_valueIndex = `
                    <img src="./static/images/no_sensor.svg" alt="No sensor">
                `;
                html_valueIndex_isSet = true;
            }
            if (iiwa_devices_data_soilCondition == 'Unconfigured'){
                html_soilCondition = `
                    <p class="dashboard_card_text">Please configure!</p>
                `;

                html_valueIndex = `
                    <img src="./static/images/unconfigured_device.svg" alt="Unconfigured">
                `;
                html_valueIndex_isSet = true;
            }
            if (iiwa_devices_data_soilCondition != 'no sensor' && iiwa_devices_data_soilCondition != 'Unconfigured'){
                html_soilCondition = `
                    <p class="dashboard_card_text">Soil condition : <span id="dashboard_card_text_sensor_value">${iiwa_devices_data[x]['soil_condition']}</span></p>
                `;
            }
            /* *** */

            /* create html content for value index svg icons */
            if (iiwa_devices_valueIndex != 'undefined' && !html_valueIndex_isSet){
                // we adopt the following rule: 
                // 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-very wet/saturated

                if (iiwa_devices_valueIndex <= 0){
                    html_valueIndex = `
                        <img src="./static/images/level0.svg" alt="Level 0">
                    `;
                }
                else if (iiwa_devices_valueIndex == 1){
                    html_valueIndex = `
                        <img src="./static/images/level1.svg" alt="Level 1">
                    `;
                }
                else if (iiwa_devices_valueIndex == 2){
                    html_valueIndex = `
                        <img src="./static/images/level2.svg" alt="Level 2">
                    `;
                }
                else if (iiwa_devices_valueIndex == 3){
                    html_valueIndex = `
                        <img src="./static/images/level3.svg" alt="Level 3">
                    `;
                }
                else if (iiwa_devices_valueIndex == 4){
                    html_valueIndex = `
                        <img src="./static/images/level4.svg" alt="Level 4">
                    `;
                }
                else if (iiwa_devices_valueIndex == 5){
                    html_valueIndex = `
                        <img src="./static/images/level5.svg" alt="Level 5">
                    `;
                }
            }

            // generate Wazigate Dashboard link for sensor graph
            html_sensorGraph_link = `
                <a href="http://wazigate.local/#/devices/${iiwa_devices_data[x]['device_id']}/sensors/${iiwa_devices_data[x]['sensor_id']}" target="_blank"><img src="./static/images/graph.svg" alt="View sensor graph"></a>
            `;

            // generate link for sensor configurator page
            html_sensorConfigurator_link = `
                <a href="intel_irris_sensor_configurator?deviceID=${iiwa_devices_data[x]['device_id']}&sensorID=${iiwa_devices_data[x]['sensor_id']}"><img src="./static/images/sensor_configurator.png" alt="Configure this sensor"></a>
            `;

            // append new card items to card ul
            $('ul').append(
                `
                    <li class="dashboard_cards_item">
                        <div class="dashboard_card">
                            <div class="dashboard_card_content">
                                <h2 class="dashboard_card_title">${iiwa_devices_data[x]['device_name']}</h2>
                                <p></p>
                                <div class="dashboard_card_sensor_value">
                                    ${html_soilCondition}
                                    ${html_valueIndex}
                                </div>
                                <p></p>
                                <div class="dashboard_card_footer_graph">
                                    ${html_sensorGraph_link}
                                </div>
                                <div class="dashboard_card_footer_sensor_configurator">
                                    ${html_sensorConfigurator_link}
                                </div>
                            </div>
                        </div>
                    </li>  
                `
            )

            // reset variables
            iiwa_devices_data_soilCondition ='';
            html_soilCondition = '';
            iiwa_devices_valueIndex = '';
            html_valueIndex = '';
            html_valueIndex_isSet = false;
            html_sensorGraph_link = '';
        }    
    }
}

// this function runs periodically to fetch data for the page
function continuous_update_Dashboard_data() {
    get_iiwa_devices_data(); // obtain new devices data
    setTimeout(continuous_update_Dashboard_data, 1000);
}
continuous_update_Dashboard_data();