#!/bin/bash

# this script creates a SEN0308 sensor as primary device, i.e. SOIL-AREA-1 and devAddr=26011DAA

echo "--> Get token"
TOK=`curl -X POST "http://localhost/auth/token" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"loragateway\"}" | tr -d '\"'`

DATE=`date +"%Y-%m-%dT06:00:00.001Z"`

echo "--> Use date of $DATE" 
echo "--> Create new device"

DEVICE=`curl -X POST "http://localhost/devices" -H "accept: application/json" -H "Authorization: Bearer $TOK" -H  "Content-Type: application/json" -d "{\"actuators\":[],\"name\":\"SOIL-AREA-1\",\"sensors\":[{\"id\":\"temperatureSensor_0\",\"kind\":\"\",\"meta\":{\"createdBy\":\"wazigate-lora\",\"kind\":\"Raw value from SEN0308\",\"model\":\"SEN0308\",\"type\":\"capacitive\",\"sensor_dry_max\":800,\"sensor_wet_max\":0,\"sensor_n_interval\":6,\"value_index\":0},\"name\":\"Soil Humidity Sensor\",\"quantity\":\"\",\"time\":\"$DATE\",\"unit\":\"\",\"value\":800}]}" | tr -d '\"'`

echo $DEVICE > ./LAST_CREATED_DEVICE.txt
echo "device $DEVICE"
echo "		name: SOIL-AREA-1"
echo "		with Soil Humidity Sensor displaying Raw value from SEN0308"
echo "		and initialized with 800 value"

echo "--> Make it LoRaWAN"
echo "		device id: 26011DAA"
curl -X POST "http://localhost/devices/${DEVICE}/meta" -H "accept: application/json" -H "Authorization: Bearer $TOK" -H  "Content-Type: application/json" -d  "{\"codec\":\"application/x-xlpp\",\"lorawan\":{\"appSKey\":\"23158D3BBC31E6AF670D195B5AED5525\",\"devAddr\":\"26011DAA\",\"devEUI\":\"AA555A0026011DAA\",\"nwkSEncKey\":\"23158D3BBC31E6AF670D195B5AED5525\",\"profile\":\"WaziDev\"}}"

echo "--> Add value -1"
curl -X POST "http://localhost/devices/${DEVICE}/sensors/temperatureSensor_0/value" -H "accept: application/json" -H "Authorization: Bearer $TOK" -H  "Content-Type: application/json" -d "{\"value\":-1, \"time\":\"$DATE\"}"

#we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-saturated
echo "--> Change humidity index to max value - 5:very wet"
curl -X POST "http://localhost/devices/${DEVICE}/sensors/temperatureSensor_0/meta" -H "accept: application/json" -H "Authorization: Bearer $TOK" -H  "Content-Type: application/json" -d "{\"value_index\":5}"