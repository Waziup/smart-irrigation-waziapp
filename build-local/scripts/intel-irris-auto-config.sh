#!/bin/bash

echo "create-starter-kit-demo-capacitive-watermark-st-iiwa" >> ./intel-irris-auto-config.log

if [ $# -eq 0 ]
then
#delete all devices, except gateway devices
echo "--> delete all devices" >> ./intel-irris-auto-config.log
./delete_all_devices.sh
fi

#create capacitive SOIL-AREA-1 and device with address 26011DAA
echo "--> calling create_full_capacitive_device.sh" >> ./intel-irris-auto-config.log
./create_full_capacitive_device_with_dev_addr.sh 1 AA
DEVICE=`cat ./LAST_CREATED_DEVICE.txt`
echo "--> created device is $DEVICE" >> ./intel-irris-auto-config.log
#add the temperature sensor
echo "--> calling create_only_temperature_sensor.sh $DEVICE" >> ./intel-irris-auto-config.log
./create_only_temperature_sensor.sh $DEVICE
#add the voltage monitor sensor
echo "--> calling create_only_voltage_monitor_sensor.sh $DEVICE" >> ./intel-irris-auto-config.log 
./create_only_voltage_monitor_sensor.sh $DEVICE

#IIWA, first, duplicate the template files
echo "--> copy empty IIWA configuration files from /home/pi/intel-irris-waziapp/config/empty" >> ./intel-irris-auto-config.log
cp ../../config/empty/*.json .

#IIWA, add first capacitive device
echo "--> add $DEVICE to IIWA" >> ./intel-irris-auto-config.log
./add_to_iiwa_devices.sh $DEVICE 1 capacitive
echo "--> set default configuration for $DEVICE in IIWA" >> ./intel-irris-auto-config.log
./add_to_iiwa_config.sh $DEVICE capacitive

#create tensiometer SOIL-AREA-2 and device with address 26011DB2
echo "--> calling create_full_tensiometer_device_with_dev_addr.sh 2 B1" >> ./intel-irris-auto-config.log
./create_full_tensiometer_device_with_dev_addr.sh 2 B1
DEVICE=`cat ./LAST_CREATED_DEVICE.txt`
echo "--> created device is $DEVICE" >> ./intel-irris-auto-config.log
#add the temperature sensor
echo "--> calling create_only_temperature_sensor.sh $DEVICE" >> ./intel-irris-auto-config.log
./create_only_temperature_sensor.sh $DEVICE
#add the voltage monitor sensor
echo "--> calling create_only_voltage_monitor_sensor.sh $DEVICE" >> ./intel-irris-auto-config.log
./create_only_voltage_monitor_sensor.sh $DEVICE

#IIWA, then add second tensiometer device id
echo "--> add $DEVICE to IIWA" >> ./intel-irris-auto-config.log
./add_to_iiwa_devices.sh $DEVICE 2 tensiometer
echo "--> set default configuration for $DEVICE in IIWA" >> ./intel-irris-auto-config.log
./add_to_iiwa_config.sh $DEVICE tensiometer

#remove LAST_CREATED_DEVICE.txt
rm ./LAST_CREATED_DEVICE.txt

#IIWA, finally, copy IIWA config file into IIWA config folder
echo "--> copy new IIWA configuration files to IIWA config folder" >> ./intel-irris-auto-config.log
cp *.json ../../config

  

