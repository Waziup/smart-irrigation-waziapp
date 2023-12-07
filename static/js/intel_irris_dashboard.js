import {load_html_texts_for_current_language, webui_texts} from './util_load_Dashboard_html_texts.js';

window.addEventListener('onload', load_html_texts_for_current_language("dashboard_page"));

const iiwa_devices_data_url = '/devices/data';

const sensorID = 'temperatureSensor_0';

var thisPage_webui_texts = {};
const thisPage_webui_texts_list = 'dashboard_page';
var thisPage_webui_textsFor_please_configure = '';
var thisPage_webui_textsFor_found_no_sensor = '';
var thisPage_webui_textsFor_soil_condition = '';
var thisPage_webui_textsFor_soil_condition_very_dry = '';
var thisPage_webui_textsFor_soil_condition_dry = '';
var thisPage_webui_textsFor_soil_condition_wet = '';
var item_soil_condition = '';
var thisPage_webui_textsFor_capacitive = '';
var thisPage_webui_textsFor_tensiometer_cbar = '';
var thisPage_webui_textsFor_tensiometer_raw = '';
var item_sensor_type = '';
var thisPage_webui_textsFor_value = '';
var item_sensor_value = '';

var iiwa_devices_data; // stores device and sensor data:
var iiwa_devices_data_count = 0;
//device ID, sensor ID, device name, sensor type, last sensor value, soil type, soil condition

var iiwa_devices_data_soilCondition ='';
var html_soilCondition = '';
var iiwa_devices_valueIndex = '';
var html_valueIndex = '';
var html_valueIndex_isSet = false;
var html_sensorGraph_link = '';
var html_sensorType_image = '';
var html_sensorConfigurator_link = '';

const iiwa_headers = {
	'Content-Type': 'application/json'
}

/* ****  Function(s) for Web UI language setting **** */
export function load_other_dashboard_text_contents(){
	thisPage_webui_texts = webui_texts;
	//console.log(thisPage_webui_texts)

    thisPage_webui_textsFor_please_configure = thisPage_webui_texts[thisPage_webui_texts_list]['please_configure'];		
    thisPage_webui_textsFor_found_no_sensor = thisPage_webui_texts[thisPage_webui_texts_list]['found_no_sensor'];
    thisPage_webui_textsFor_soil_condition = thisPage_webui_texts[thisPage_webui_texts_list]['soil_condition'];
    thisPage_webui_textsFor_soil_condition_very_dry = thisPage_webui_texts[thisPage_webui_texts_list]['very_dry'];
    thisPage_webui_textsFor_soil_condition_dry = thisPage_webui_texts[thisPage_webui_texts_list]['dry'];
    thisPage_webui_textsFor_soil_condition_wet = thisPage_webui_texts[thisPage_webui_texts_list]['wet'];
    thisPage_webui_textsFor_capacitive = thisPage_webui_texts[thisPage_webui_texts_list]['capacitive'];
    thisPage_webui_textsFor_tensiometer_cbar = thisPage_webui_texts[thisPage_webui_texts_list]['tensiometer_cbar'];
    thisPage_webui_textsFor_tensiometer_raw = thisPage_webui_texts[thisPage_webui_texts_list]['tensiometer_raw'];
    thisPage_webui_textsFor_value = thisPage_webui_texts[thisPage_webui_texts_list]['value'];
}

function convertToArabic(westernNumber) {
    const westernDigits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    const arabicDigits = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  
    let arabicNumber = '';
  
    for (let i = 0; i < westernNumber.length; i++) {
      const digit = westernNumber[i];
      const digitIndex = westernDigits.indexOf(digit);
  
      if (digitIndex !== -1) {
        arabicNumber += arabicDigits[digitIndex];
      } else {
        // if the character is not a digit, keep it unchanged
        arabicNumber += digit;
      }
    }
  
    return arabicNumber;
}

/* **** Function(s) for device/sensor data processing/visualization **** */

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
    var wazigate_current_host = window.location.host.split(':')[0];
    
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
                    <p class="dashboard_card_text">${thisPage_webui_textsFor_found_no_sensor}</p>
                `;
								
                html_valueIndex = `
                    <img src="./static/images/no_sensor.svg" alt="No sensor">
                `;
                html_valueIndex_isSet = true;
            }
            if (iiwa_devices_data_soilCondition == 'Unconfigured'){
                html_soilCondition = `
                    <p class="dashboard_card_text">${thisPage_webui_textsFor_please_configure}</p>
                `;
                
                html_valueIndex = `
                    <img src="./static/images/unconfigured_device.svg" alt="Unconfigured">
                `;
                html_valueIndex_isSet = true;
            }
            if (iiwa_devices_data_soilCondition != 'no sensor' && iiwa_devices_data_soilCondition != 'Unconfigured'){
                
                switch (iiwa_devices_data_soilCondition){
                    case "dry":
                        item_soil_condition = thisPage_webui_textsFor_soil_condition_dry;
                        break;
                    case "very dry":
                        item_soil_condition = thisPage_webui_textsFor_soil_condition_very_dry;
                        break;
                    case "wet":
                        item_soil_condition = thisPage_webui_textsFor_soil_condition_wet;
                        break;
                    default:
                        break;
                }

                switch (iiwa_devices_data[x]['sensor_type']){
                    case 'capacitive':
                        item_sensor_type = thisPage_webui_textsFor_capacitive;
                        break;
                    case 'tensiometer_cbar':
                        item_sensor_type = thisPage_webui_textsFor_tensiometer_cbar;
                        break;
                    case 'tensiometer_raw':
                        item_sensor_type = thisPage_webui_textsFor_tensiometer_raw;
                        break;
                    default:
                        break;
                }

                if (thisPage_webui_texts['current_language'] == 'arabic'){ 
                    item_sensor_value = convertToArabic(iiwa_devices_data[x]['sensor_value']);
                }
                else if (thisPage_webui_texts['current_language'] != 'arabic'){ 
                    item_sensor_value = iiwa_devices_data[x]['sensor_value'];
                }
                
                html_soilCondition = `
                    <table>
                        <tr>
                            <td class="dashboard_card_text">${thisPage_webui_textsFor_soil_condition} <span id="dashboard_card_text_sensor_value">${item_soil_condition}</span></td>
                        </tr>		
                        <tr>																					
                            <td class="dashboard_card_text">${item_sensor_type}</td>
                        </tr>			
                        <tr>																				
                            <td class="dashboard_card_text">${thisPage_webui_textsFor_value} <span id="dashboard_card_text_sensor_value">${item_sensor_value}</span></td>								
                        </tr>
                    </table>                                        
                `;              
            }
            /* *** */

            /* create html content for value index svg icons */
            if (iiwa_devices_valueIndex != 'undefined' && !html_valueIndex_isSet){
                // we adopt the following rule: 
                // 0:very dry; 1:dry; 2:dry; 3:wet; 4:wet; 5:saturated

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
                <a href="http://${wazigate_current_host}/#/devices/${iiwa_devices_data[x]['device_id']}/sensors/${sensorID}" target="_blank"><img src="./static/images/graph.svg" alt="View sensor graph"></a>
            `;

            // generate sensor type image
            if (iiwa_devices_data[x]['sensor_type']=='capacitive') {
            	html_sensorType_image = `
                	<img src="./static/images/capacitive.png" alt="capacitive">
            	`;
            }
            else if (iiwa_devices_data[x]['sensor_type']=='tensiometer_cbar') {	
            	html_sensorType_image = `
                	<img src="./static/images/tensiometer.png" alt="tensiometer">
            	`;
            }
                        
            // generate link for sensor configurator page
            html_sensorConfigurator_link = `
                <a href="intel_irris_sensor_configurator?deviceID=${iiwa_devices_data[x]['device_id']}&sensorID=${sensorID}"><img src="./static/images/sensor_configurator.png" alt="Configure this sensor"></a>
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
                                <div class="dashboard_card_footer">
                                    <div class="dashboard_card_footer_sensor_image"> 
                                        ${html_sensorType_image}
                                    </div>
                                    <div class="dashboard_card_footer_graph">
                                        ${html_sensorGraph_link}                   
                                    </div>
                                    <div class="dashboard_card_footer_sensor_configurator">
                                        ${html_sensorConfigurator_link}
                                    </div>
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
            html_sensorType_image = '';
            item_soil_condition = '';
            item_sensor_type = '';
            item_sensor_value = '';
        }    
    }
}
/* ***************************** */

// this function runs periodically to fetch data for the page
function continuous_update_Dashboard_data() {
    get_iiwa_devices_data(); // obtain new devices data
    setTimeout(continuous_update_Dashboard_data, 5000);
}
continuous_update_Dashboard_data();