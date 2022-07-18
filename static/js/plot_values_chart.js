active_url = 'intel-irris-active-device-sensor'
check_valid_DeviceSensor_id_url = 'check-device-sensor-id'
get_sensor_values_url = 'request-sensor-values'

var deviceID;
var sensorID;

var four_04 = false;

var deviceid = document.getElementById("deviceid")
var deviceid_id = document.getElementById("deviceid_id")
var sensorid = document.getElementById("sensorid")
var sensorid_id = document.getElementById("sensorid_id")
var lastvalue = document.getElementById("lastvalue")
var lastvalue_value = document.getElementById("lastvalue_value")
var semi_circle = document.getElementById("semi-circle")
var last_value_insight = document.getElementById("last_value_insight")
var insight = document.getElementById("insight");
var no_sensor_found = document.getElementById("no_sensor_error")
var chart = document.getElementById("values_chart")
var sensor_id_error = document.getElementById("sensor_id_error")
var sensor_id_error_p2 = document.getElementById("sensor_id_error_p2")
var sensor_id_error_id = document.getElementById("sensor_id")

var data;
var timestamps = []; // stores timestamps from the sensor values
var values = [];     // stores sensor values
var x_y_values = {}; // stores both timestamps and sensor values for plotting
var datapoints = 0;  // used by set marker on last value
var values_min;
var values_max;

//let TIME_length = 0;
async function getActiveIDs() {
    const response = await fetch(active_url);
    //console.log(response);
    var active_ids = await response.json();

    deviceID = active_ids[0]['device_id'];
    sensorID = active_ids[0]['sensor_id'];

    //console.log("Device id " + deviceID);
    //console.log("Sensor id " + sensorID);

    if (sensorID == null) {
        deviceid.style.display = "none";
        sensorid.style.display = "none";
        lastvalue.style.display = "none";
        semi_circle.style.display = "none";
        last_value_insight.style.display = "none";
        no_sensor_found.style.display = "block";
        sensor_id_error.style.display = "none";
        sensor_id_error_p2.style.display = "none";
        chart.style.display = "none";
    }
    else {
        deviceid_id.innerHTML = deviceID;
        deviceid.style.display = "block";
        sensorid_id.innerHTML = sensorID;
        sensorid.style.display = "block";        
        no_sensor_found.style.display = "none";
        check_DeviceSensorIDs();
    }
}

async function check_DeviceSensorIDs() {
    const response = await fetch(check_valid_DeviceSensor_id_url + '?deviceID=' + deviceID + '&sensorID=' + sensorID);
    //console.log(response);
    active_device_id = await response.json();
    response_status = active_device_id[0]['status']

    if (response_status == '404') {
        four_04 = true;

        deviceid.style.display = "none";
        sensorid.style.display = "none";
        lastvalue.style.display = "none";
        semi_circle.style.display = "none";
        last_value_insight.style.display = "none";
        no_sensor_found.style.display = "none";
        sensor_id_error_id.innerHTML = sensorID;
        sensor_id_error.style.display = "block";
        sensor_id_error_p2.style.display = "block";
        chart.style.display = "none";
    }
    else if (response_status == '200') {
        sensor_id_error.style.display = "none";
        sensor_id_error_p2.style.display = "none";
        plotData();
    }

}
async function plotData() {
    if (!four_04) {
        const data_response = await fetch(get_sensor_values_url + '?deviceID=' + deviceID + '&sensorID=' + sensorID);

        const sensor_data = await data_response.json()

        data = sensor_data;
        console.log("data : " + JSON.stringify(data));
        // number of indices in the list
        length = Object.keys(data).length; 

				// used by set marker on last value
        datapoints = length; 
        console.log("datapoints : " + length);

				// reset variables
        timestamps = []; 
        values = [];
        x_y_values = {};
        values_min = 0;
        values_max = 0;


        // push time and sensor values to lists
        for (i = 0; i < length; i++) {
            //timestamps.push(data[i].timestamp);

            //formatted_timestamp = parse_ISO8601(data[i].timestamp); // convert ISO8601 to YY HH mm ss format
            //timestamps.push(formatted_timestamp);
            timestamps.push(data[i]["time"]);

            //values.push(data[i].value);
            values.push(data[i]["value"]);
        }
        if (length == 1) {
            lastvalue_value.innerHTML = values[0];
            lastvalue.style.display = "block";
            fill_circle(values[0])
        }
        else if (length > 1) {
            lastvalue_value.innerHTML = values[length - 1];
            lastvalue.style.display = "block";
            fill_circle(values[length - 1])
        }
        /* filling semi-circle with color based on last sensor value */
        function fill_circle(last_value) {
            soil_moisture = last_value
            if (soil_moisture >= 0 && soil_moisture <= 196) {
                semi_circle.style.borderColor = "lightblue";
                semi_circle.style.display = "block";

                insight.innerHTML = 'very wet';
                insight.style.display = "block";
            }
            else if (soil_moisture >= 196 && soil_moisture <= 390) {
                semi_circle.style.borderColor = "green";
                semi_circle.style.display = "block";

                insight.innerHTML = 'wet';
                insight.style.display = "block";
            }
            else if (soil_moisture >= 391 && soil_moisture <= 585) {
                semi_circle.style.borderColor = "orange";
                semi_circle.style.display = "block";

                insight.innerHTML = 'dry';
                insight.style.display = "block";
            }
            else if (soil_moisture >= 586 && soil_moisture <= 780) {
                semi_circle.style.borderColor = "red";
                semi_circle.style.display = "block";

                insight.innerHTML = 'very dry';
                insight.style.display = "block";
            }
        }

        /* *** */

        //console.log("timestamps " + timestamps);
        //console.log("values " + values);

        values_min = Math.min.apply(Math, values);
        values_max = Math.max.apply(Math, values);
        if (values_min == values_max) // if similar datapoints, reset min to 0
        {
            values_min = 0;
        }
        //console.log("values_min = "+values_min);
        //console.log("values_max = "+values_max);

        //TIME_length = Object.keys(timestamps).length; // get number of days in timestamp
        //console.log("TIME_length = " + TIME_length);

        x_y_values = timestamps.map((x, i) => ({ x, y: values[i] })); // convert the two lists [], into dict [{}]
        //console.log("x_y_values " + x_y_values);


        /* Render values in chart */
        var options = {
            annotations: {
                // display intervals with colors
                position: "back",
                yaxis: [
                    {
                        label: {
                        		// set to " " for removing text
                            text: "very wet" 
                        },
                        y: 0,
                        y2: 195,
                        fillColor: "#00E396"
                    },
                    {
                        label: {
                            text: "wet"
                        },
                        y: 196,
                        y2: 390,
                        fillColor: "#90EE7E"
                    },
                    {
                        label: {
                            text: "dry"
                        },
                        y: 391,
                        y2: 585,
                        fillColor: "#FF9800"
                    },
                    {
                        label: {
                            text: "very dry"
                        },
                        y: 586,
                        y2: 780,
                        fillColor: "#FF4560"
                    }
                ]
            },
            stroke: {
                width: 1,
                colors: ["#008FFB"],
                curve: 'smooth'
            },
            chart: {
                type: "line",
                foreColor: "#6D6D6D"
                // set color of axes labels
                //height: 200 // set the height of the chart
                //width: "100%" // set the width of the chart
            },
            toolbar: {
                show: true
            },
            title: {
                text: "Soil Moisture Values",
                align: "left"
            },
            series: [
                {
                    type: "line",
                    name: "value",
                    data: values.map((y, i) => ({ y, x: timestamps[i] }))
                }
            ],
            yaxis: {
                min: values_min,
                max: values_max >= 700 ? 780 : values_max,
                tickAmount: 5
            },
            xaxis: {
                type: "hour",
                labels: {
                    show: false,
                    hideOverlappingLabels: false,
                    format: "H m dd MM yyyy"
                }
            },
            tooltip: {
                x: {
                    formatter: function (value, { series, seriesIndex, dataPointIndex, w }) {

                        // add logic to compute how many days between hovered date and latest date. Consider month, year gap
                        //var latest_date = timestamps[TIME_length - 1].slice(8, 10);
                        //var hover_date = timestamps[value - 1].slice(8, 10);
                        //console.log("latest date = "+ latest_date);
                        //console.log("hover_date = "+ hover_date);
                        /*
                        return (latest_date - hover_date == 0) ? timestamps[value - 1] :
                            (latest_date - hover_date == 1) ? TIME_length - value + " day ago " + timestamps[value - 1] : TIME_length - value + " days ago " + timestamps[value - 1]; */

                        return timestamps[value - 1];
                    }
                }
            },
            markers: { // shows a marker at the latest value
                discrete: [
                    {
                        seriesIndex: 0,
                        dataPointIndex: datapoints - 1,

                        //fillColor: "#0A0", // green
                        fillColor: "#f4b548",
                        strokeColor: "#FFF",
                        size: 7
                    }
                ]
            }
        };

        var chart = new ApexCharts(document.querySelector("#values_chart"), options);
        chart.render();

        chart.updateSeries([{ 
        		// update the chart with the new values from response
            name: 'value',
            data: x_y_values
        }])
    }
}

function parse_ISO8601(iso8601) {
    isoStr = iso8601;
    const date = isoStr.slice(0, 10);
    //console.log("date = " + date);
    const time = isoStr.slice(11, 19);
    //console.log("time = " + time);
    const DateTime = date + " " + time;
    //console.log("DateTime = " + DateTime);

    return DateTime;
}

function foo() {
    getActiveIDs();
    setTimeout(foo, 6000);
}

foo();