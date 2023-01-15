#!/bin/bash

tmpfile=$(mktemp)

if [ $2 == 'capacitive' ]
then
jq ".sensors += \
    [{\
      \"value\": {\
        \"sensor_type\": \"${2}\",\
        \"sensor_age\": \"0\",\
        \"sensor_max\": \"800\",\
        \"sensor_min\": \"0\",\
        \"soil_type\": \"silty\",\
        \"soil_irrigation_type\": \"undefined\",\
        \"soil_salinity\": \"disabled\",\
        \"soil_bulk_density\": \"disabled\",\
        \"plant_crop\": \"undefined\",\
        \"plant_sub_type\": \"undefined\",\
        \"plant_planting_date\": \"undefined\",\
        \"weather_region\": \"semi-arid\",\
        \"last_value\": 0\
      },\
      \"soil_temperature_source\": {\
        \"soil_temperature_device_id\": \"undefined\",\
        \"soil_temperature_sensor_id\": \"undefined\",\
        \"soil_temperature_value\": \"undefined\"\
      },\
      \"device_id\": \"${1}\",\
      \"sensor_id\": \"temperatureSensor_0\"\
    }]" intel-irris-conf.json > "$tmpfile" && mv -- "$tmpfile" intel-irris-conf.json 
fi

if [ $2 == 'tensiometer' ]
then  
jq ".sensors += \
    [{\
      \"value\": {\
        \"sensor_type\": \"${2}_cbar\",\
        \"sensor_age\": \"0\",\
        \"sensor_max\": \"124\",\
        \"sensor_min\": \"0\",\
        \"soil_type\": \"silty\",
        \"soil_irrigation_type\": \"undefined\",\
        \"soil_salinity\": \"disabled\",\
        \"soil_bulk_density\": \"disabled\",\
        \"plant_crop\": \"undefined\",\
        \"plant_sub_type\": \"undefined\",\
        \"plant_planting_date\": \"undefined\",\
        \"weather_region\": \"semi-arid\",\
        \"last_value\": 0\
      },\
      \"soil_temperature_source\": {\
        \"soil_temperature_device_id\": \"${1}\",\
        \"soil_temperature_sensor_id\": \"temperatureSensor_5\",\
        \"soil_temperature_value\": \"undefined\"\
      },\
      \"device_id\": \"${1}\",\
      \"sensor_id\": \"temperatureSensor_0\"\
    }]" intel-irris-conf.json > "$tmpfile" && mv -- "$tmpfile" intel-irris-conf.json 
fi