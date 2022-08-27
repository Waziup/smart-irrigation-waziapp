from flask import Flask, render_template, request, jsonify
import requests, json, os
from os import path
from datetime import datetime

app = Flask(__name__)

#--- config filepaths ---#
added_devices_filename = 'config/intel-irris-devices.json'
active_device_filename = 'config/intel-irris-active-device.json'
sensor_config_filename = 'config/intel-irris-conf.json'
#-----------------------#

#only for soil condition, 'fr' or 'en'
iiwa_lang='en'

#BASE_URL="https://api.waziup.io/api/v2/" # uncomment for WaziCloud
#avoid to change manually the next line as a script will do this task
BASE_URL="http://localhost/"

headers = {
		'accept': 'application/json',
}

#common header for requests
WaziGate_headers = {
		'accept': 'application/json',
		'content-type': 'application/json'
}
WaziGate_headers_auth = {
		'accept': 'application/json',
		'content-type': 'application/json',
		'Authorization': 'Bearer **'
}

#---------------------#

sensor_max_capacitive = "800"

capacitive_default_sensor_config = {
		"value": {
				"sensor_type": "capacitive",
				"sensor_age": "0",
				"sensor_max": sensor_max_capacitive,
				"sensor_min": "0",
				"soil_type": "sandy",
				"soil_irrigation_type": "furrow",
				"soil_salinity": "0",
				"soil_bulk_density": "0",
				"plant_crop": "wheat",
				"plant_sub_type": "sub_type_A",
				"plant_planting_date": "undefined",
				"weather_region": "semi-arid",										
				"last_value": 0.0
		},
		"soil_temperature_source": {
				"soil_temperature_device_id": "undefined",
				"soil_temperature_sensor_id": "undefined",
				"soil_temperature_value": 28.0
		}
}

sensor_max_tensiometer_cbar = "124"
sensor_max_tensiometer_raw = "18000"

tensiometer_default_sensor_config = {
		"value": {
				"sensor_type": "tensiometer_raw",
				"sensor_age": "0",
				"sensor_max": sensor_max_tensiometer_raw,
				"sensor_min": "0",
				"soil_type": "sandy",
				"soil_irrigation_type": "furrow",
				"soil_salinity": "0",
				"soil_bulk_density": "0",
				"plant_crop": "wheat",
				"plant_sub_type": "sub_type_A",
				"plant_planting_date": "undefined",
				"weather_region": "semi-arid",										
				"last_value": 0.0
		},
		"soil_temperature_source": {
				"soil_temperature_device_id": "undefined",
				"soil_temperature_sensor_id": "undefined",
				"soil_temperature_value": 28.0
		}
}					

active_device_id = "undefined" 
active_sensor_id = "undefined"
active_device_soil_condition = "undefined"
active_device_value_index = 0
active_device_configuration = {}

@app.route("/")
def dashboard():

		# check if there are devices in devices JSON
		if path.isfile(added_devices_filename) is False:	# Check if data.json file exists
				added_devices = "Config file for active device ID not found!"
				no_devices = True
		else:
				print("Config file for active device ID is found!")
				
				f = open(added_devices_filename, 'r')
				read_devices = json.loads(f.read())
				f.close()
		
				length = len(read_devices)

				added_devices = ""

				# check if the json list is updated
				if (length == 1):
						# instruct user to add a device
						no_devices = True
						added_devices = "No devices added to IIWA. Go to the Device Manager to add one."
				else:
						no_devices = False
						monitor_all_configured_sensors()
						
				#---------------------#

		if (no_devices == True):
				return render_template("intel-irris-dashboard.html",
															 added_devices=added_devices,
															 no_devices=no_devices)
		elif (no_devices == False):
		
				if active_device_id == "undefined" or active_device_configuration=={}: 
						active_sensor_type = "undefined"
						active_soil_type = "undefined"
				else:
						active_sensor_type = active_device_configuration['value']['sensor_type']
						active_soil_type = active_device_configuration['value']['soil_type']
				
				active_level_file='images/level'+str(active_device_value_index)+'.png'
						
				return render_template("intel-irris-dashboard.html",
															 no_devices=no_devices,
															 sensor_type=active_sensor_type,
															 soil_type=active_soil_type,
															 soil_condition=active_device_soil_condition,
															 level_file=active_level_file)
#---------------------#


@app.route("/intel-irris-devices", methods=['POST', 'GET'])
def intel_irris_device_manager():

		f = open(added_devices_filename, 'r')
		read_devices = json.loads(f.read())
		length = len(read_devices)
		f.close()

		#---------------------#
		#-- Manage selecting an active device from list and update active device --#
		if request.method == 'POST':	# get selected device name
				active_device = request.form.get('device-id-select')
				active_sensor_id = request.form.get('sensor-id-select')
				
				# write device_id to json
				if (active_device is not None):	 
						print("Selected active device: %s" % active_device)

						active_device_dict = [{'device_id': active_device}]
						# convert python dic to JSON string
						jsString = json.dumps(active_device_dict)	 
						jsFile = open(active_device_filename, "w")
						jsFile.write(jsString)
						jsFile.close()
						print("Successfully updated active device!")

				if (active_sensor_id is not None):
						print("Selected active sensor: %s" % active_sensor_id)

						jsFile = open(active_device_filename, 'r')
						active_device_id = json.loads(jsFile.read())
						jsFile.close()

						active_device_id = active_device_id[0]['device_id']

						active_device_sensor_dict = [{
								'device_id': active_device_id,
								'sensor_id': active_sensor_id
						}]

						# convert python dict to JSON 
						jsString = json.dumps(active_device_sensor_dict)
						jsFile = open(active_device_filename, "w")
						jsFile.write(jsString)
						jsFile.close()
						print("Successfully updated active sensor id!")

		#---------------------#

		#-- Handle adding/removing a device_id from IIWA ---#
		
		# get form input and add to json
		if request.method == 'POST':	
				add_device_id = request.form.get('device_id')
				add_device_name = request.form.get('device_name')
				sensors_structure = request.form.get('sensors_structure')
				remove_device_id = request.form.get('device_id_remove')

				#-- Add a new device_id and device_name to json using html form ---#
				if (add_device_id is not None) and (add_device_name is not None) and (sensors_structure is not None):
						# check if devices list has been updates

						# device list not updated
						if (length == 1): 
								print("Added device list not updated! Updating..")

								# write device_id as active one in json
								active_device_Dict = [{'device_id': add_device_id}]
								# convert python dic to JSON string
								jsString = json.dumps(active_device_Dict)	 
								jsFile = open(active_device_filename, "w")
								jsFile.write(jsString)
								jsFile.close()
								print("Added device set as active device")

						# add new devices in JSON file

						add_device_dict = {
								'device_id': add_device_id,
								'device_name': add_device_name,
								'sensors_structure': sensors_structure
						}

						# 1. Read file contents
						with open(added_devices_filename, "r") as file:
								read_data = json.load(file)
						# 2. Update json object
						read_data.append(add_device_dict)
						# 3. Write json file
						with open(added_devices_filename, "w") as file:
								json.dump(read_data, file)
						print("Device list updated!")

				#-- Remove a device id from devices, active-device reset to another, remove also sensor data ---#
				elif (remove_device_id is not None):
						print("Requested to remove device id : %s" % remove_device_id)
						request_removed_from_devices = False
						request_removed_from_active = False
						request_removed_from_sensors = False

						# ** first remove id from devices **
						if (not request_removed_from_devices):

								# 1. Read file contents
								with open(added_devices_filename, "r") as file:
										read_data = json.load(file)
								no_devices = len(read_data)

								# 2. Check index of sumbitted device id
								for x in range(0, no_devices):
										if read_data[x]['device_id'] == remove_device_id:
												requested_removal_exists = True
												print("requested device_id to remove is valid....")
												# remove device id and name
												read_data.pop(x)
												print("new devices data to be saved in config = %s" %
															read_data)

												# 3. Write json file
												with open(added_devices_filename, "w") as file:
														json.dump(read_data, file)
												print("Device list updated!")
												request_removed_from_devices = True
												break

						# ** next remove id from active-device if it exists **
						if (requested_removal_exists and (not request_removed_from_active)):
								# open active device config
								active = open(active_device_filename, 'r')
								active_device = json.loads(active.read())
								# print(active_device)
								active.close()
								deviceID = active_device[0]['device_id']

								# check if active device matches requested removal and update active
								if (deviceID == remove_device_id):
										print("Device id to remove was active id..resolving this..")
										# check if only one index is in list and empty active list
										if (len(read_data) == 1):	 
												# empty json file
												open(active_device_filename, 'w').close()	 
												print("Found no other device id to use! No devices in IIWA :(")
												request_removed_from_active = True
										
										# if there are added device IDs, pick first and set as active
										elif (len(read_data) > 1):	
												active_device_Dict = [{
														'device_id':
														read_data[1]['device_id']
												}]
												
												# convert python dic to JSON string
												jsString = json.dumps(active_device_Dict)	 
												jsFile = open(active_device_filename, "w")
												jsFile.write(jsString)
												jsFile.close()
												print("Updated active device!")
												request_removed_from_active = True

						# ** lastly remove id from sensor config **
						if (requested_removal_exists and (not request_removed_from_sensors)):

								# obtain all sensor ids of the device
								response_obtained = False
								deviceID_exists = False
								while (not response_obtained):
										url = BASE_URL+"devices/%s" % remove_device_id
										response = requests.get(url, headers=WaziGate_headers)

										if response.status_code == 200:
												device_data = response.json()
												deviceID_exists = True
												response_obtained = True
										
										elif response.status_code == 404:
												print("The requested device ID to remove does not exist. Failed to request its sensors")
												deviceID_exists = False
												response_obtained = True

								# if the device id exists, get its sensor and remove in sensor config file
								if deviceID_exists: 
										device_sensors_num = len(device_data['sensors'])
										# print("The device has %s sensor(s)"%no_sensors)

										sensor_ids = []
										# store sensor IDs
										for x in range(0, device_sensors_num):
												sensor_ids.append(device_data['sensors'][x]['id'])
										#print("Sensors ids for the device are : %s"%sensor_ids)

										with open(sensor_config_filename, "r") as file:
												read_globals = json.load(file)

										read_sensors = read_globals['sensors']
										#print("read_sensors config : %s"%read_sensors)
										globals_s_salinity = read_globals['globals']['soil_salinity']
										globals_s_bulk_density = read_globals['globals']['soil_bulk_density']

										config_sensors_count = len(read_sensors)
										device_sensors_count = len(sensor_ids)
										pop_indices = []
										for x in range(0, config_sensors_count):
												for y in range(0, device_sensors_count):
														if (read_sensors[x]['sensor_id'] == sensor_ids[y]):
																pop_indices.append(x)

										for b in range(0, len(pop_indices)):
												read_sensors.pop(pop_indices[b])

										print("New sensor config data : %s" % read_sensors)

										# save new data to config file
										update_config = {
												"globals": {
														"soil_salinity": globals_s_salinity,
														"soil_bulk_density": globals_s_bulk_density
												},
												"sensors": read_sensors
										}
										# update with the sensor config
										jsString = json.dumps(update_config)
										jsFile = open(sensor_config_filename, "w")
										jsFile.write(jsString)
										jsFile.close()

		#---------------------#

		return render_template("intel-irris-device-manager.html",
													 read_devices=read_devices,
													 length=length)
#---------------------#


@app.route("/intel-irris-sensor-config", methods=['POST', 'GET'])
def intel_irris_sensor_config():
		# check if an active device is set
		no_active = True
		
		get_ActiveDeviceSensorID()
		
		#check if there is an active device for IIWA
		if active_device_id != "undefined":
				no_active = False	
				deviceID = active_device_id
				print("Active device_id: %s" % deviceID)
				sensorID = active_sensor_id
				
				#-- GET device data --#
				url=BASE_URL+"devices/%s" % deviceID
				response = requests.get(url, headers=WaziGate_headers)
				device_data = response.json()
				deviceName = device_data['name']

				#-- GET sensor data --#
				url=BASE_URL+"devices/%s/sensors/%s" % (deviceID, sensorID)
				response = requests.get(url, headers=WaziGate_headers)
				sensor_data = response.json()
				sensorName = sensor_data['name']
				sensorKind = sensor_data['meta']['kind']
				
				#---------------------#
				#-- Manage notifying user to add new config --#
				current_config_file = open(sensor_config_filename, 'r')
				current_config = json.loads(current_config_file.read())

				# check if sensor config list empty
				if (len(current_config['sensors']) == 0):	 
						print("No sensor configurations made!")
						no_sensor_config = True
				else:
						no_sensor_config = False

				#---------------------#
				#-- Get submitted form data and add to config --#
				if request.method == 'POST':	# get selected device name
						sensor_id = request.form.get('sensor_id')
						sensor_type = request.form.get('sensor_type')
						sensor_age = request.form.get('sensor_age')
						sensor_max = request.form.get('sensor_max')
						sensor_min = request.form.get('sensor_min')

						soil_type = request.form.get('soil_type')
						soil_irrigation_type = request.form.get('soil_irrigation_type')
						soil_salinity = request.form.get('soil_salinity')
						soil_bulk_density = request.form.get('soil_bulk_density')						
						global_soil_salinity = request.form.get('soil_salinity')
						global_soil_bulk_density = request.form.get('soil_bulk_density')

						soil_temperature_value = request.form.get('soil_temperature_value')
						soil_temperature_device_id = request.form.get('soil_temperature_device_id')
						soil_temperature_sensor_id = request.form.get('soil_temperature_sensor_id')
												
						plant_crop = request.form.get('plant_crop')
						plant_sub_type = request.form.get('plant_sub_type')
						plant_planting_date = request.form.get('plant_planting_date')

						weather_region = request.form.get('weather_region')
						
						#-- GET last sensor data of the device --#
						url=BASE_URL+"devices/%s" % deviceID
						response = requests.get(url, headers=WaziGate_headers)
						sensors_data = response.json()

						#print(data) # uncomment to see the JSON data

						# obtain values for each sensor
						sensor_len = len(sensors_data['sensors'])

						for x in range(0, sensor_len):
								Id = sensors_data['sensors'][x]['id']
								# print("Sensor id: %s"%Id)
						for i in range(0, sensor_len):
								if (sensors_data['sensors'][i]['id'] == sensor_id):
										last_value = sensors_data['sensors'][i]['value']

						#-- Check for empty values in submitted data --#
						if (sensor_max == ""): # prefill max sensor value based on sensor type
							if (sensor_type == "capacitive"):
								sensor_max = sensor_max_capacitive
							elif (sensor_type == "tensiometer_cbar"):
								sensor_max = sensor_max_tensiometer_cbar
							elif (sensor_type == "tensiometer_raw"):
								sensor_max = sensor_max_tensiometer_raw

						if (soil_type == "hide"):
								soil_type = "undefined"
						if (soil_irrigation_type == "None"):
								soil_irrigation_type = "undefined"
						if (soil_salinity == "" or soil_salinity == '-1'):
								soil_salinity = "disabled"	 
						if (soil_bulk_density == "" or soil_bulk_density == '-1'):
								soil_bulk_density = "disabled"
						if (soil_temperature_value == ""):
								soil_temperature_value = "undefined"
						if (soil_temperature_sensor_id == ""):
								soil_temperature_device_id = "undefined"
						if (soil_temperature_sensor_id == ""):
								soil_temperature_sensor_id = "undefined"
						if (plant_crop == "hide"):
								plant_crop = "undefined"
						if (plant_sub_type == "hide"):
								plant_sub_type = "undefined"
						if (plant_planting_date == ""):
								plant_planting_date = "undefined"								
						if (weather_region == "hide"):
								weather_region = "undefined"
								
						if (global_soil_salinity != "" and global_soil_salinity != '-1'):
								global_soil_salinity = global_soil_salinity
						if (global_soil_bulk_density != "" and global_soil_bulk_density != '-1'):
								global_soil_bulk_density = global_soil_bulk_density

						print("Sensor ID : %s" % sensor_id)
						print("Sensor Type : %s" % sensor_type)
						print("Sensor Age : %s" % sensor_age)
						print("Sensor Max Value : %s" % sensor_max)
						print("Sensor Min Value : %s" % sensor_min)
						print("Soil Type : %s" % soil_type)
						print("Soil Irrigation Type : %s" % soil_irrigation_type)
						print("Soil Salinity : %s" % soil_salinity)
						print("Soil Bulk Density : %s" % soil_bulk_density) 
						print("Soil temperature value : %s" % soil_temperature_value)
						print("Soil temperature source device id : %s" % soil_temperature_device_id)
						print("Soil temperature source sensor id : %s" % soil_temperature_sensor_id)											
						print("Plant Crop : %s" % plant_crop)
						print("Plant Sub-Type : %s" % plant_sub_type)
						print("Plant Planting Date : %s" % plant_planting_date)
						print("Weather Region : %s" % weather_region)
						print("Last Value : %s" % last_value)

						#---------------------#
						#-- add new config to the sensor-config.json --#

						sensor_config_record = {
								"value": {
										"sensor_type": sensor_type,
										"sensor_age": sensor_age,
										"sensor_max": sensor_max,
										"sensor_min": sensor_min,
										"soil_type": soil_type,
										"soil_irrigation_type": soil_irrigation_type,
										"soil_salinity": soil_salinity,
										"soil_bulk_density": soil_bulk_density,
										"plant_crop": plant_crop,
										"plant_sub_type": plant_sub_type,
										"plant_planting_date": plant_planting_date,
										"weather_region": weather_region,										
										"last_value": last_value
								},
								"soil_temperature_source": {
										"soil_temperature_device_id": soil_temperature_device_id,
										"soil_temperature_sensor_id": soil_temperature_sensor_id,
										"soil_temperature_value": soil_temperature_value
								},
								"device_id": deviceID,
								"sensor_id": sensor_id
						}
						# read sensors values
						with open(sensor_config_filename, "r") as file:
								read_sensors = json.load(file)['sensors']
								print("read_sensors : %s" % read_sensors)

						#---------------------#
						#-- check if selected sensor id has an existing configuration and update it --#

						updated = False
						lenght_read_sensors = len(read_sensors)
						
						for x in range(0, lenght_read_sensors):
								if (read_sensors[x]['device_id'] == deviceID and read_sensors[x]['sensor_id'] == sensor_id):
										read_sensors[x] = sensor_config_record
										updated = True

						if (updated == False):
								read_sensors.append(sensor_config_record)

						update_config = {
								"globals": {
										"soil_salinity": global_soil_salinity,
										"soil_bulk_density": global_soil_bulk_density
								},
								"sensors": read_sensors
						}
						# update config file with new values
						jsString = json.dumps(update_config)
						jsFile = open(sensor_config_filename, "w")
						jsFile.write(jsString)
						jsFile.close()
						
						#we start value_index computation as parameters may have changed
						monitor_all_configured_sensors()
						#---------------------#

		if (no_active):
				no_device = "No Devices added to IIWA. Go to the Device Manager to add one."
				return render_template("intel-irris-sensor-config.html",
															 no_active=no_active,
															 no_device=no_device)
		else:
				deviceID_str=deviceName + ' (' + deviceID + ')'
				sensorID_str=sensorName + '/' + sensorKind
				return render_template("intel-irris-sensor-config.html",
															 no_active=no_active,
															 deviceID=deviceID_str,
															 sensorID=sensorID_str)
#---------------------#

#--------------------------------------------------------------------------
#determine the soil condition string indication for capacitive
#--------------------------------------------------------------------------

default_capacitive_sensor_dry_max = 800
capacitive_sensor_dry_max = default_capacitive_sensor_dry_max
capacitive_sensor_wet_max = 0
capacitive_sensor_n_interval = 6
capacitive_sensor_soil_condition = []
#we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-saturated

if iiwa_lang=="fr":
	capacitive_sensor_soil_condition.append('très sec')
	capacitive_sensor_soil_condition.append('sec')
	capacitive_sensor_soil_condition.append('sec-hum')
	capacitive_sensor_soil_condition.append('hum-sec')
	capacitive_sensor_soil_condition.append('hum')
	capacitive_sensor_soil_condition.append('saturé')
else:
	capacitive_sensor_soil_condition.append('very dry')
	capacitive_sensor_soil_condition.append('dry')
	capacitive_sensor_soil_condition.append('dry-wet')
	capacitive_sensor_soil_condition.append('wet-dry')
	capacitive_sensor_soil_condition.append('wet')
	capacitive_sensor_soil_condition.append('saturated')	
	
#--------------------------------------------------------------------------
#determine the soil condition string indication for watermark tensiometer
#--------------------------------------------------------------------------

default_tensiometer_sensor_dry_max = 120
tensiometer_sensor_dry_max = default_tensiometer_sensor_dry_max
tensiometer_sensor_wet_max = 0
tensiometer_sensor_n_interval = 6
tensiometer_sensor_soil_condition = []
#we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-saturated

use_irrometer_interval_for_tensiometer = True

if iiwa_lang=="fr":
	tensiometer_sensor_soil_condition.append('très sec')
	tensiometer_sensor_soil_condition.append('sec')
	tensiometer_sensor_soil_condition.append('sec-hum')
	tensiometer_sensor_soil_condition.append('hum-sec')
	tensiometer_sensor_soil_condition.append('hum')
	tensiometer_sensor_soil_condition.append('saturé')
else:
	tensiometer_sensor_soil_condition.append('very dry')
	tensiometer_sensor_soil_condition.append('dry')
	tensiometer_sensor_soil_condition.append('dry-wet')
	tensiometer_sensor_soil_condition.append('wet-dry')
	tensiometer_sensor_soil_condition.append('wet')
	tensiometer_sensor_soil_condition.append('saturated') 

#--------------------------------------------------------------------------
#parameters for periodic monitor_sensor_value()
#--------------------------------------------------------------------------

#here we read from meta.value_index
get_value_index_from_local_database = True
#here we set in meta.value_index_iiwa
set_value_index_in_local_database = True
#set to True to compute value_index_iiwa for all configured device/sensor pairs, otherwise only the active one
iterate_over_all_configured_devices = True

#---------------------#

def monitor_all_configured_sensors():
	
		sensor_type='undefined'
		number_of_configurations = 0
		
		get_ActiveDeviceSensorID()
		
		global active_device_soil_condition
		active_device_soil_condition = "undefined"
		
		global active_device_configuration
		active_device_configuration = {}
		
		global active_device_value_index
		
		if os.path.getsize(sensor_config_filename) != 0:
				f = open(sensor_config_filename)
				read_config = json.loads(f.read())
				f.close()
				
				number_of_configurations = len(read_config['sensors'])
				
				if (number_of_configurations > 0):
						for x in range(0, number_of_configurations):
								deviceID = read_config['sensors'][x]['device_id']
								sensorID = read_config['sensors'][x]['sensor_id']
								
								url = BASE_URL+"devices/" + deviceID + '/sensors/' + sensorID
								
								print('monitor_all_configured_sensors : checking for', deviceID, sensorID)
								
								response = requests.get(url, headers=WaziGate_headers)
								
								if (response.status_code == 404):
										print("monitor_all_configured_sensors : Error 404! Check IDs of device and sensor of configured device")
								elif (response.status_code == 200):
										sensor_DataResponse = response.json()
										last_PostedSensorValue = sensor_DataResponse["value"]

										print("monitor_all_configured_sensors : last posted sensor value was %s" % last_PostedSensorValue)
										
										sensor_type=read_config['sensors'][x]['value']['sensor_type']
									
										if sensor_type == 'capacitive':
												value_index=get_capacitive_soil_condition(last_PostedSensorValue, deviceID, sensorID, read_config['sensors'][x])
												if deviceID == active_device_id and sensorID == active_sensor_id:
														active_device_soil_condition = capacitive_soil_condition
														active_device_configuration = read_config['sensors'][x] 
														active_device_value_index = value_index
														
										if 'tensiometer' in sensor_type:	
												value_index=get_tensiometer_soil_condition(last_PostedSensorValue, deviceID, sensorID, read_config['sensors'][x])
												if deviceID == active_device_id and sensorID == active_sensor_id:
														active_device_soil_condition = tensiometer_soil_condition
														active_device_configuration = read_config['sensors'][x]
														active_device_value_index = value_index
																								
		else:
				print("monitor_all_configured_sensors : No sensor configuration has been made")				

def monitor_only_active_sensor():
		
		found_sensor_config={}		
		sensor_type='undefined'
		number_of_configurations = 0
		fetch_last_value = False
		
		get_ActiveDeviceSensorID()
		
		#check if there is an active device for IIWA
		if active_device_id == "undefined":
				print("monitor_only_active_sensor : No devices added to IIWA, go to the Device Manager to add one")
		else:		
				#in all cases we will get the last value from the active sensor
				fetch_last_value = True
				
				f = open(sensor_config_filename)
				read_config = json.loads(f.read())
				f.close()

				number_of_configurations = len(read_config['sensors'])

				if (number_of_configurations > 0):
						for x in range(0, number_of_configurations):
								if (read_config['sensors'][x]['device_id'] == deviceID and read_config['sensors'][x]['sensor_id'] == sensorID):
										print("monitor_only_active_sensor : current device/sensor id found in configuration")
										#not needed, to be removed
										#sensor_lastValue = read_config['sensors'][x]['value']['last_value']
										#print("compute-index-service : last sensor value in config is : %s" %sensor_lastValue)
										sensor_type=read_config['sensors'][x]['value']['sensor_type']
										found_sensor_config=read_config['sensors'][x]
										print (found_sensor_config)
										break
								elif (read_config['sensors'][x]['device_id'] != deviceID):
										print("monitor_only_active_sensor : no match, continue searching")
								
						if found_sensor_config == {}:					
								print("monitor_only_active_sensor : Current sensor id has not been found in sensors configuration")

				elif number_of_configurations == 0:
						print("monitor_only_active_sensor : No sensor configuration has been made")

		if (fetch_last_value):
				url = BASE_URL+"devices/" + deviceID + '/sensors/' + sensorID

				response = requests.get(url, headers=WaziGate_headers)

				if (response.status_code == 404):
						print("monitor_only_active_sensor : Error 404! Check IDs of device and sensor of active device")
				elif (response.status_code == 200):
						sensor_DataResponse = response.json()
						last_PostedSensorValue = sensor_DataResponse["value"]
						print("monitor_only_active_sensor : last posted sensor value was : %s" % last_PostedSensorValue)
						
						#if sensor type was not found in configuration file, try sensor's meta data
						if sensor_type == 'undefined':
							if 'capacitive' in response.text:
								sensor_type = 'capacitive'
								
							if 'tensiometer' in response.text:
								sensor_type = 'tensiometer'
						
						#still undefined?
						if sensor_type == 'undefined':
							print("monitor_only_active_sensor : Error! Sensor type is undefined, not computing humidity index value") 
						else:
							print ('sensor_type =', sensor_type)
							
							if found_sensor_config == {}:
							
									print("monitor_only_active_sensor : Index computation will use default configuration")
									
									if sensor_type == 'capacitive':
											sensor_config = capacitive_default_sensor_config
											
									if 'tensiometer' in sensor_type:
											sensor_config = tensiometer_default_sensor_config											
							else:
									print("monitor_only_active_sensor : Computing humidity index value with sensor's configuration")
									sensor_config = found_sensor_config				
									
							if sensor_type == 'capacitive':
									get_capacitive_soil_condition(last_PostedSensorValue, deviceID, sensorID, sensor_config)
			
							if 'tensiometer' in sensor_type:	
									get_tensiometer_soil_condition(last_PostedSensorValue, deviceID, sensorID, sensor_config)


def get_ActiveDeviceSensorID():

		global active_device_id 
		global active_sensor_id

		active_device_id = "undefined" 
		active_sensor_id = "undefined"

		deviceID_key = 'device_id'
		sensorID_key = 'sensor_id'						

		#check if there is an active device for IIWA
		if os.path.getsize(active_device_filename) != 0:					
				f = open(active_device_filename, 'r')
				
				try:
						read_devices = json.loads(f.read())
						if deviceID_key in read_devices[0] and sensorID_key in read_devices[0]:
								#get active device and active sensor id
								active_device_id = read_devices[0]['device_id']
								active_sensor_id = read_devices[0]['sensor_id']
						elif deviceID_key not in read_devices[0] or sensorID_key not in read_devices[0]:
								print("get_ActiveDeviceSensorID : Error in configuration file!")
								print("get_ActiveDeviceSensorID : Go to the Device Manager to add a device or sensor id")					
				except ValueError as e:
						print("get_ActiveDeviceSensorID : Error in configuration file!")
					
				f.close()				
				
#--------------------------------------------------------------------------
#determine the soil condition string indication for capacitive
#--------------------------------------------------------------------------

clay_capacitive_sensor_dry_max = 400
sandy_capacitive_sensor_dry_max = 700
silty_capacitive_sensor_dry_max = 500
peaty_capacitive_sensor_dry_max = 500
chalky_capacitive_sensor_dry_max = 500
loamy_capacitive_sensor_dry_max = 500

def get_capacitive_sensor_dry_max(sensor_config):

	print("soil type is", sensor_config["value"]["soil_type"])
	
	if sensor_config["value"]["soil_type"]=="clay":
		return clay_capacitive_sensor_dry_max
		
	if sensor_config["value"]["soil_type"]=="sandy":
		return sandy_capacitive_sensor_dry_max
		
	if sensor_config["value"]["soil_type"]=="silty":
		return silty_capacitive_sensor_dry_max

	if sensor_config["value"]["soil_type"]=="peaty":
		return peaty_capacitive_sensor_dry_max
		
	if sensor_config["value"]["soil_type"]=="chalky":
		return chalky_capacitive_sensor_dry_max
		
	if sensor_config["value"]["soil_type"]=="loamy":
		return loamy_capacitive_sensor_dry_max		
				
	return default_capacitive_sensor_dry_max

##TODO use BASE_URL
def get_capacitive_soil_condition(raw_value, device_id, sensor_id, sensor_config):
		
		if get_value_index_from_local_database:
				WaziGate_url = 'http://localhost/devices/' + device_id + '/sensors/' + sensor_id
				try:
						response = requests.get(WaziGate_url, headers=WaziGate_headers, timeout=30)
						print('get-capacitive: returned msg from server is '),
						print(response.status_code)
						print(response.reason)

						if 200 <= response.status_code < 300:
								print('get-capacitive GET success')
								print(response.text)
								device_json = json.loads(response.text)
								value_index_capacitive = device_json["meta"]["value_index"]
								print(".meta.value_index=", value_index_capacitive)
						else:
								print('get-capacitive: bad request')
								print(response.text)

				except requests.exceptions.RequestException as e:
						print(e)
						print('get-capacitive: requests command failed')

				print('=========================================')

		#now we compute
		value_interval = int(get_capacitive_sensor_dry_max(sensor_config) / capacitive_sensor_n_interval)
		value_index_capacitive = int(raw_value / value_interval)
		#in case the sensed value is greater than the maximum value defined
		if value_index_capacitive >= capacitive_sensor_n_interval:
				value_index_capacitive = capacitive_sensor_n_interval - 1

		#we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-saturated
		#so for capacitive we need to invert the index
		value_index_capacitive = capacitive_sensor_n_interval - 1 - value_index_capacitive
		
		print('computed value_index (capacitive) =', value_index_capacitive)
		
		global capacitive_soil_condition
		capacitive_soil_condition=capacitive_sensor_soil_condition[value_index_capacitive]		
		
		print('soil condition =', capacitive_soil_condition)	
		print('=========================================')		

		if set_value_index_in_local_database:
				my_token = "hello"
				#get the token first
				WaziGate_url = 'http://localhost/auth/token'
				try:
						pload = '{"username":"admin","password":"loragateway"}'
						response = requests.post(WaziGate_url, headers=WaziGate_headers, data=pload, timeout=30)
						print('get-capacitive: returned msg from server is '),
						print(response.status_code)
						print(response.reason)

						if 200 <= response.status_code < 300:
								print('get-capacitive: POST success')
								print(response.text)
								my_token = response.text
						else:
								print('get-capacitive: bad request')
								print(response.text)

				except requests.exceptions.RequestException as e:
						print(e)
						print('get-capacitive: requests command failed')

				print('=========================================')

				WaziGate_url = 'http://localhost/devices/' + device_id + '/sensors/' + sensor_id + '/meta'
				try:
						timestr=datetime.utcnow().isoformat()[:-3]+'Z'
						pload = '{"value_index_iiwa":' + str(value_index_capacitive) +', "value_index_iiwa_time":"' + timestr + '"'+ '}'
						WaziGate_headers_auth['Authorization'] = 'Bearer' + my_token[1:-2]
						response = requests.post(WaziGate_url, headers=WaziGate_headers_auth, data=pload, timeout=30)
						print('get-capacitive: returned msg from server is '),
						print(response.status_code)
						print(response.reason)

						if 200 <= response.status_code < 300:
								print('get-capacitive: POST success')
								print(response.text)

						else:
								print('get-capacitive: bad request')
								print(response.text)

				except requests.exceptions.RequestException as e:
						print(e)
						print('get-capacitive: requests command failed')

				print('=========================================')
		
		return value_index_capacitive		
				
#--------------------------------------------------------------------------
#determine the soil condition string indication for tensiometer
#--------------------------------------------------------------------------

def get_tensiometer_sensor_dry_max(sensor_config):
	
	print("soil type is", sensor_config["value"]["soil_type"])
	
	return default_tensiometer_sensor_dry_max
	
##TODO use BASE_URL
##TODO use raw resistor value to compute centibar and link with soil temperature	
def get_tensiometer_soil_condition(raw_value, device_id, sensor_id, sensor_config): 
		
		if get_value_index_from_local_database:
				WaziGate_url = 'http://localhost/devices/' + device_id + '/sensors/' + sensor_id
				try:
						response = requests.get(WaziGate_url, headers=WaziGate_headers, timeout=30)
						print('get-tensiometer: returned msg from server is '),
						print(response.status_code)
						print(response.reason)

						if 200 <= response.status_code < 300:
								print('get-tensiometer: GET success')
								print(response.text)
								device_json = json.loads(response.text)
								value_index_tensiometer = device_json["meta"]["value_index"]
								print(".meta.value_index=", value_index_tensiometer)
						else:
								print('get-tensiometer: bad request')
								print(response.text)

				except requests.exceptions.RequestException as e:
						print(e)
						print('get-tensiometer: requests command failed')

				print('=========================================')

		#now we compute
		if use_irrometer_interval_for_tensiometer:
				#from irrometer: https://www.irrometer.com/basics.html
				#0-10 Centibars = Saturated soil
				#10-30 Centibars = Soil is adequately wet (except coarse sands, which are drying)
				#30-60 Centibars = Usual range for irrigation (most soils)
				#60-100 Centibars = Usual range for irrigation in heavy clay
				#100-200 Centibars = Soil is becoming dangerously dry- proceed with caution!
				# 
				#we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-very wet/saturated

				print("soil type is", sensor_config["value"]["soil_type"])
		
				if raw_value == 255:
					value_index_tensiometer=-1
				elif raw_value == 240:
					value_index_tensiometer=-2					
				elif raw_value > 100:
					value_index_tensiometer=0	 
				elif raw_value > 60:
					value_index_tensiometer=1 
				elif raw_value > 30:
					value_index_tensiometer=2 
				elif raw_value > 10:
					value_index_tensiometer=4 
				else:
					value_index_tensiometer=5												
		else:
				value_interval=int(get_tensiometer_sensor_dry_max(sensor_config)/tensiometer_sensor_n_interval)
				value_index_tensiometer=int(raw_value/value_interval)
				#in case the sensed value is greater than the maximum value defined
				if value_index_tensiometer >= tensiometer_sensor_n_interval:
					value_index_tensiometer = tensiometer_sensor_n_interval-1		
		
				#we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-very wet/saturated
				#so for tensiometer we need to invert the index
				value_index_tensiometer=tensiometer_sensor_n_interval-1-value_index_tensiometer 
		
		print('computed value_index (tensiometer) =', value_index_tensiometer)

		global tensiometer_soil_condition
		if value_index_tensiometer==-1:
				tensiometer_soil_condition='no sensor'
		elif value_index_tensiometer==-2:
				tensiometer_soil_condition='err'
		else:			
				tensiometer_soil_condition=tensiometer_sensor_soil_condition[value_index_tensiometer]		
			
		print('soil condition =', tensiometer_soil_condition) 
		print('=========================================')
		
		if set_value_index_in_local_database:
				my_token="hello"
				#get the token first
				WaziGate_url='http://localhost/auth/token'
				try:
					pload = '{"username":"admin","password":"loragateway"}'
					response = requests.post(WaziGate_url, headers=WaziGate_headers, data=pload, timeout=30)
					print ('get-tensiometer: returned msg from server is '),
					print (response.status_code)
					print (response.reason)
		
					if 200 <= response.status_code < 300:
						print ('get-tensiometer: POST success')
						print (response.text)
						my_token=response.text
					else:
						print ('get-tensiometer: bad request')
						print (response.text)			
			
				except requests.exceptions.RequestException as e:
					print (e)
					print ('get-tensiometer: requests command failed')
		
				print ('=========================================') 
				
				WaziGate_url='http://localhost/devices/' + device_id + '/sensors/' + sensor_id + '/meta'
				try:
					timestr=datetime.utcnow().isoformat()[:-3]+'Z'
					pload = '{"value_index_iiwa":' + str(value_index_tensiometer) +', "value_index_iiwa_time":"' + timestr + '"'+ '}'
					WaziGate_headers_auth['Authorization']='Bearer'+my_token[1:-2]
					response = requests.post(WaziGate_url, headers=WaziGate_headers_auth, data=pload, timeout=30)
					print ('get-tensiometer: returned msg from server is '),
					print (response.status_code)
					print (response.reason)
		
					if 200 <= response.status_code < 300:
						print ('get-tensiometer: POST success')
						print (response.text)
					else:
						print ('get-tensiometer: bad request')
						print (response.text)			
			
				except requests.exceptions.RequestException as e:
					print (e)
					print ('get-tensiometer: requests command failed')
			
				print ('=========================================') 
		return value_index_tensiometer
								
#---------------------#
# periodically compute humidity index value

import threading

# in seconds
computing_interval_sec = 10

def foo():
		if iterate_over_all_configured_devices == True:
			monitor_all_configured_sensors()
		else:
			monitor_only_active_sensor()
			
		threading.Timer(computing_interval_sec, foo).start()
		
foo()

#---------------------#
#Route methods for accessing config data

@app.route("/intel-irris-added-devices", methods=['GET'])	 # returns list of added devices
def intel_irris_added_devices():
		if request.method == 'GET':
				f = open(added_devices_filename, 'r')
				read_devices = json.loads(f.read())
				f.close()

				return jsonify(read_devices)


@app.route("/intel-irris-active-device", methods=['GET'])	 # returns device id of active device
def intel_irris_active_device():
		if request.method == 'GET':
				if os.path.getsize(active_device_filename) != 0:
						f = open(active_device_filename, 'r')
						try:
								active_device_id = json.loads(f.read())
								f.close()
								active_device_id = active_device_id[0]['device_id']
								return jsonify(active_device_id)				
						except ValueError as e:
								f.close()
								return jsonify('[]')
						
@app.route("/intel-irris-active-device-sensor", methods=['GET'])	 # returns data in active device config
def intel_irris_active_device_sensor():
		if request.method == 'GET':
				if os.path.getsize(active_device_filename) != 0:
						f = open(active_device_filename, 'r')
						try:
								active_device_id = json.loads(f.read())
								f.close()
								return jsonify(active_device_id)
						except ValueError as e:
								f.close()
								return jsonify('[]')												

@app.route("/intel-irris-sensor-configurations", methods=['GET'])	 # returns data in sensor configurations
def intel_irris_sensor_configurations():
		if request.method == 'GET':
				f = open(sensor_config_filename, 'r')
				configurations = json.loads(f.read())
				f.close()

				return jsonify(configurations)

#---------------------#

#---------------------# Route methods for making GET requests (JS fix)

# returns data of gateway devices
@app.route("/request-gateway-devices", methods=['GET']) 
def request_gateway_devices():
		if request.method == 'GET':
				url = BASE_URL+"devices"

				response = requests.get(url, headers=WaziGate_headers)
				data = response.json()

				return jsonify(data)

# returns 200 or 404 to indicate if sensor or device id is valid/invalid
@app.route("/check-device-sensor-id", methods=['GET']) 
def check_sensor_id():
		if request.method == 'GET':
				device_id = request.args.get('deviceID')
				sensor_id = request.args.get('sensorID')
				
				url = BASE_URL+"devices/" + device_id + '/sensors/' + sensor_id

				response = requests.get(url, headers=WaziGate_headers)
				if (response.status_code == 404):
						return jsonify([{"status": "404"}])
				elif (response.status_code == 200):
						return jsonify([{"status": "200"}])

# returns all device data of a device ID
@app.route("/request-device-data", methods=['GET']) 
def request_device_data():
		if request.method == 'GET':
				device_id = request.args.get('deviceID')

				if device_id[0] != '[':
						device_url = BASE_URL+"devices/" + device_id

						response = requests.get(device_url, headers=WaziGate_headers)

						if response.status_code == 200:
								data = response.json()
								print("Device ID exists")
								return jsonify(data)
						elif response.status_code == 404:
								print("Device ID does not exist")
								return jsonify([{'status':'404'}])
								
				# handle when empty device id
				elif device_id[0] == '[': 
						print("no device id has been provided")
						return jsonify([{'status':'404'}])


# returns sensors data of a device ID
@app.route("/request-device-sensors", methods=['GET']) 
def request_device_sensors():
		if request.method == 'GET':
				device_id = request.args.get('deviceID')

				if device_id[0] != '[':
						device_url = BASE_URL+"devices/" + device_id + '/sensors'

						response = requests.get(device_url, headers=WaziGate_headers)

						if response.status_code == 200:
								data = response.json()
								print("Device ID exists")
								return jsonify(data)
						elif response.status_code == 404:
								print("Device ID does not exist")
								return jsonify([{'status':'404'}])
								
				# handle when empty device id
				elif device_id[0] == '[': 
						print("no device id has been provided")
						return jsonify([{'status':'404'}])

# returns sensor data
@app.route("/request-sensor-data", methods=['GET']) 
def request_sensor_data():
		if request.method == 'GET':
				device_id = request.args.get('deviceID')
				sensor_id = request.args.get('sensorID')

				sensorData_url = BASE_URL+"devices/" + device_id + "/sensors/" + sensor_id

				response = requests.get(sensorData_url, headers=WaziGate_headers)
				data = response.json()

				return jsonify(data)
				
# returns sensor values
@app.route("/request-sensor-values", methods=['GET']) 
def request_sensor_values():
		if request.method == 'GET':
				device_id = request.args.get('deviceID')
				sensor_id = request.args.get('sensorID')

				sensorValues_url = BASE_URL+"devices/" + device_id + "/sensors/" + sensor_id + "/values"

				response = requests.get(sensorValues_url, headers=WaziGate_headers)
				data = response.json()

				return jsonify(data)


#---------------------#

if __name__ == "__main__":
		app.run(host='0.0.0.0', debug=True, use_reloader=False)
		#app.run(host='unix:///app/intel-irris-waziapp/proxy.sock',use_reloader=False,debug=True)
			
