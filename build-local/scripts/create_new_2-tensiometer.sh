#!/bin/bash

# Ex: create_new_2-tensiometer.sh 4 B2

echo "--> calling create_full_tensiometer_device_with_dev_addr.sh $1 $2" >> ./intel-irris-auto-config.log
./create_full_2-tensiometer_device_with_dev_addr.sh $1 $2
DEVICE=`cat ./LAST_CREATED_DEVICE.txt`
echo "--> created device is $DEVICE" >> ./intel-irris-auto-config.log
#add the temperature sensor
echo "--> calling create_only_temperature_sensor.sh $DEVICE" >> ./intel-irris-auto-config.log
./create_only_temperature_sensor.sh $DEVICE
#add the voltage monitor sensor
echo "--> calling create_only_voltage_monitor_sensor.sh $DEVICE" >> ./intel-irris-auto-config.log
./create_only_voltage_monitor_sensor.sh $DEVICE

#IIWA, add tensiometer device id
echo "--> add $DEVICE to IIWA" >> ./intel-irris-auto-config.log
./add_to_iiwa_devices.sh $DEVICE $1 2tensiometers
echo "--> set default configuration for $DEVICE in IIWA" >> ./intel-irris-auto-config.log
./add_to_iiwa_config.sh $DEVICE 2tensiometers

#remove LAST_CREATED_DEVICE.txt
rm ./LAST_CREATED_DEVICE.txt

#IIWA, finally, copy IIWA config file into IIWA config folder
echo "--> copy new IIWA configuration files to IIWA config folder" >> ./intel-irris-auto-config.log
cp *.json ../../config