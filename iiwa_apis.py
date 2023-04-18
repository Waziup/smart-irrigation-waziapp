# this script handles all the REST API requests made by IIWA
from app import *
from __main__ import app

# --------------------------------------------------------------------------
# REST APIs for IIWA device/sensor management
# --------------------------------------------------------------------------

# adds a device to IIWA by writing to 'intel_irris_devices.json' a device_id, device_name, and sensors_structure
@app.route('/devices/<deviceID>', methods=['POST'])
def iiwa_add_device(deviceID):
	if (request.is_json):
		print("IIWA : Requested to add DeviceID: %s" % deviceID)
		device_id = deviceID 
		device_name = request.json['device_name']
		sensors_structure = request.json['sensors_structure']
	
		new_device_configuration = {
			'device_id': device_id,
			'device_name': device_name,
			'sensors_structure': sensors_structure
		}

		# 1. Read IIWA devices
		with open(iiwa_devices_filename, "r") as file:
			iiwa_devices = json.load(file)

		# check if submitted device/sensor already exist in IIWA
		add_deviceID_exists = False
		for x in range(0, len(iiwa_devices)):
			if (iiwa_devices[x]['device_id'] == device_id):
				add_deviceID_exists = True
				break

		if (add_deviceID_exists):
				print("IIWA add new device : submitted DeviceID exists in IIWA!")
				return jsonify({"code" : 409,
					"message" :  "IIWA add new device : submitted DeviceID exists in IIWA!"})

		elif(not add_deviceID_exists):
			# 2. Update json object
			iiwa_devices.append(new_device_configuration)
			# 3. Write to json file
			with open(iiwa_devices_filename, "w") as file:
				json.dump(iiwa_devices, file)
			print("IIWA : Successfully updated IIWA device list!")
			return jsonify(new_device_configuration)

	else:
		print("IIWA add new device : Invalid JSON body received!")
		return jsonify({"code" : 400,
			"message" :  "IIWA add new device : Invalid JSON body received!"})
# ---------------------#

# removes a device from IIWA 
@app.route('/devices/<deviceID>', methods=['DELETE'])
def iiwa_remove_device(deviceID):
	remove_device_id = deviceID
	print("IIWA : Requested to remove DeviceID : %s" % remove_device_id)
	removed_from_devices_filename = False
	removed_from_sensorconfig_filename = False
	requested_removal_exists = False

	# ** first remove DeviceID from intel_irris_devices.json **
	if (not removed_from_devices_filename):

		# 1. Read file contents
		with open(iiwa_devices_filename, "r") as file:
			iiwa_devices = json.load(file)
		number_of_iiwa_devices = len(iiwa_devices)

		# 2. Check index of sumbitted DeviceID
		for x in range(0, number_of_iiwa_devices):
			if iiwa_devices[x]['device_id'] == remove_device_id:
				requested_removal_exists = True
				print("IIWA : Requested DeviceID to remove exists in IIWA")
				# remove device id and name
				iiwa_devices.pop(x)
				print("IIWA : New device(s) data to be saved in JSON = %s" %iiwa_devices)

				# 3. Write json file
				with open(iiwa_devices_filename, "w") as file:
					json.dump(iiwa_devices, file)
				print("IIWA : Successfully updated IIWA device list!")
				removed_from_devices_filename = True
				break
		
		if (not requested_removal_exists):
			print("IIWA remove device : submitted DeviceID does not exist in IIWA!")
			return jsonify({"code" : 409,
				"message" :  "IIWA remove device : submitted DeviceID does not exist in IIWA!"})

	# ** lastly remove device id from sensors configurations **
	if (requested_removal_exists and (not removed_from_sensorconfig_filename)):

		with open(iiwa_sensors_config_filename, "r") as file:
			iiwa_sensors_config_data = json.load(file)

		iiwa_sensors_configurations = iiwa_sensors_config_data['sensors']
		# print("iiwa_sensors_configurations.json : %s"%iiwa_sensors_configurations)
		globals_soil_salinity = iiwa_sensors_config_data['globals']['soil_salinity']
		globals_soil_bulk_density = iiwa_sensors_config_data['globals']['soil_bulk_density']
		global_soil_field_capacity = iiwa_sensors_config_data['globals']['soil_field_capacity']
		global_weather_region = iiwa_sensors_config_data['globals']['weather_region']
		global_weather_weekly_evaporation = iiwa_sensors_config_data['globals']['weather_weekly_evaporation']
		global_weather_weekly_pluviometry = iiwa_sensors_config_data['globals']['weather_weekly_pluviometry']

		iiwa_configured_sensors_count = len(iiwa_sensors_configurations)
		pop_indices = []
		for x in range(0, iiwa_configured_sensors_count):
			if (iiwa_sensors_configurations[x]['device_id'] == remove_device_id):
				pop_indices.append(x)

		pop_indices=pop_indices[::-1]
		for b in range(0, len(pop_indices)):
			iiwa_sensors_configurations.pop(pop_indices[b])

		# save new data to config file
		new_iiwa_sensors_configurations = {
			"globals": {
				"soil_salinity": globals_soil_salinity,
				"soil_bulk_density": globals_soil_bulk_density,
				"soil_field_capacity": global_soil_field_capacity,
				"weather_region" : global_weather_region,
				"weather_weekly_evaporation": global_weather_weekly_evaporation,
				"weather_weekly_pluviometry": global_weather_weekly_pluviometry
			},
			"sensors": iiwa_sensors_configurations
		}
		print("IIWA : New data data to be saved in JSON: %s" % new_iiwa_sensors_configurations)
		# update with the sensor config
		jsString = json.dumps(new_iiwa_sensors_configurations)
		jsFile = open(iiwa_sensors_config_filename, "w")
		jsFile.write(jsString)
		jsFile.close()

		return jsonify({"code" : 200,
				"message" :  "IIWA remove device : successfully removed the device and it's sensor(s) configuration(s)!"})
# ---------------------#

# returns all data in 'intel_irris_devices.json'
@app.route("/devices", methods=['GET'])
def get_iiwa_devices():
	f = open(iiwa_devices_filename, 'r')
	iiwa_devices = json.loads(f.read())
	f.close()

	return jsonify(iiwa_devices)
# ---------------------#

# returns Intel-Irris device data: device ID, sensor ID, device name, sensor type, last sensor value, soil type, soil condition
# this is used by the Dashboard's JS file to populate the cards
@app.route("/devices/data", methods=['GET'])
def devices_data():

	iiwa_devices_data = []
	iiwa_devices_data =  monitor_all_configured_sensors()
	#print("iiwa_devices_data : %s" %iiwa_devices_data)

	if (iiwa_devices_data == None):
		iiwa_devices_data = []

	# read the IIWA devices list
	f = open(iiwa_devices_filename, 'r')
	iiwa_devices = json.loads(f.read())
	f.close()

	number_of_iiwa_devices = len(iiwa_devices)
	
	# read the configured sensors
	with open(iiwa_sensors_config_filename, "r") as file:
		read_iiwa_sensor_configurations = json.load(file)['sensors']
	read_iiwa_sensor_configurations_count = len(read_iiwa_sensor_configurations)

	configured_iiwa_devices = []

	# check if each IIWA deviceID has a configured sensor
	for x in range(0,number_of_iiwa_devices):
		for y in range(0, read_iiwa_sensor_configurations_count):
			if iiwa_devices[x]['device_id'] == read_iiwa_sensor_configurations[y]['device_id']:
				configured_iiwa_devices.append(iiwa_devices[x]['device_id'])
				
	configured_iiwa_devices_count = len(configured_iiwa_devices)

	# iterate IIWA device list and check the deviceIDs that were not found in sensor configuration data
	for i in range(0, number_of_iiwa_devices):
		if iiwa_devices[i]['device_id'] not in configured_iiwa_devices:
			# if a deviceID is not found to have a sensor, we append this data to iiwa_devices_data
			# soil_condition value, 'Unconfigured', is important as it is used on the Dashboard to indicate no configuration
			iiwa_devices_data.append({
						"device_id": iiwa_devices[i]['device_id'],
						"device_name" : iiwa_devices[i]['device_name'],
						"sensor_id" : 'undefined',
						"sensor_type" : 'undefined',
						"value_index" : 'undefined',
						"soil_condition" : 'Unconfigured'
					})
				
	#print("iiwa_devices_data : %s"%iiwa_devices_data)  
	
	return jsonify(iiwa_devices_data)
# ---------------------#

# adds a sensor configuration to IIWA by writing to 'intel_irris_sensors_configurations.json'
@app.route("/devices/<deviceID>/sensors/<sensorID>", methods=['POST'])
def update_sensor_configuration(deviceID,sensorID ):
	if (request.is_json):

		# check if the required keys values have been sumbitted
		try:
			deviceID = deviceID
			sensorID = sensorID
			sensor_type = request.json['sensor_type']
			sensor_age = request.json['sensor_age']
			sensor_max_value = request.json['sensor_max_value']
			sensor_min_value = request.json['sensor_min_value']
			soil_type = request.json['soil_type']
			soil_irrigation_type = request.json['soil_irrigation_type']
			soil_salinity = request.json['soil_salinity']
			soil_bulk_density = request.json['soil_bulk_density']
			soil_field_capacity = request.json['soil_field_capacity']
			soil_temperature_value = request.json['soil_temperature_value']
			soil_temperature_device_id = request.json['soil_temperature_device_id']
			soil_temperature_sensor_id = request.json['soil_temperature_sensor_id']
			plant_category = request.json['plant_category']
			plant_type = request.json['plant_type']
			plant_variety = request.json['plant_variety']
			plant_planting_date = request.json['plant_planting_date']
			weather_region = request.json['weather_region']
			weather_weekly_evaporation = request.json['weather_weekly_evaporation']
			weather_weekly_pluviometry = request.json['weather_weekly_pluviometry']

		# raise an error when any required key is not found in submitted JSON
		except KeyError:
			print("IIWA add sensor configuration : a missing key has been identified in the submitted JSON!")
			return jsonify({"code" : 409,
					"message" :  "IIWA add sensor configuration : a missing key has been identified in the submitted JSON!"})

		# -- Check for empty values in submitted data --#
		if (sensor_max_value == ""):  # prefill max sensor value based on sensor type
			if (sensor_type == "capacitive"):
				sensor_max_value = sensor_max_capacitive
			elif (sensor_type == "tensiometer_cbar"):
				sensor_max_value = sensor_max_tensiometer_cbar
			elif (sensor_type == "tensiometer_raw"):
				sensor_max_value = sensor_max_tensiometer_raw
		if (sensor_min_value == ""):
			sensor_min_value = 0
		if (soil_type == "hide"):
			soil_type = "undefined"
		if (soil_irrigation_type == "None"):
			soil_irrigation_type = "undefined"
		if (soil_temperature_value == ""):
			soil_temperature_value = "undefined"
		if (soil_temperature_sensor_id == ""):
			soil_temperature_device_id = "undefined"
		if (soil_temperature_sensor_id == ""):
			soil_temperature_sensor_id = "undefined"
		if (plant_category == "hide"):
			plant_category = "undefined"
		if (plant_type == "hide"):
			plant_type = "undefined"
		if (plant_variety == "hide"):
			plant_variety = "undefined"
		if (plant_planting_date == ""):
			plant_planting_date = "undefined"
		if (weather_region == "hide"):
			weather_region = "undefined"
		if (weather_weekly_evaporation != "" and weather_weekly_evaporation != '-1'):
			weather_weekly_evaporation = weather_weekly_evaporation
		else:
			weather_weekly_evaporation = "undefined"
		if (weather_weekly_pluviometry != "" and weather_weekly_pluviometry != '-1'):
			weather_weekly_pluviometry = weather_weekly_pluviometry
		else:
			weather_weekly_pluviometry = "undefined"
		if (soil_salinity != "" and soil_salinity != '-1'):
			soil_salinity = soil_salinity
		else:
			soil_salinity = "undefined"
		if (soil_bulk_density != "" and soil_bulk_density != '-1'):
			soil_bulk_density = soil_bulk_density
		else:
			soil_bulk_density = "undefined"
		if (soil_field_capacity != "" and soil_field_capacity != '-1'):
			soil_field_capacity = soil_field_capacity
		else:
			soil_field_capacity = "undefined"

		# -- GET last sensor value --#
		url = BASE_URL+"devices/" + deviceID + '/sensors/' + sensorID
		response = requests.get(url, headers=WaziGate_headers)
		sensor_DataResponse = response.json()
		last_PostedSensorValue = sensor_DataResponse["value"]

		print("Device ID : %s" %deviceID)
		print("Sensor ID : %s" % sensorID)
		print("Sensor Type : %s" % sensor_type)
		print("Sensor Age : %s" % sensor_age)
		print("Sensor Max Value : %s" % sensor_max_value)
		print("Sensor Min Value : %s" % sensor_min_value)
		print("Soil Type : %s" % soil_type)
		print("Soil Irrigation Type : %s" % soil_irrigation_type)
		print("Soil Salinity : %s" % soil_salinity)
		print("Soil Bulk Density : %s" % soil_bulk_density)
		print("Soil Field Capacity : %s" % soil_field_capacity)
		print("Soil temperature value : %s" % soil_temperature_value)
		print("Soil temperature source WaziGate DeviceID : %s" %soil_temperature_device_id)
		print("Soil temperature source WaziGate SensorID : %s" %soil_temperature_sensor_id)
		print("Plant Category : %s" % plant_category)
		print("Plant Type: %s" % plant_type)
		print("Plant Variety : %s" % plant_variety)
		print("Planting Date : %s" % plant_planting_date)
		print("Weather Region : %s" % weather_region)
		print("Weather weekly evaporation (in mm) : %s" % weather_weekly_evaporation)
		print("Weather weekly pluviometry (in mm) : %s" % weather_weekly_pluviometry)
		print("Last posted sensor value : %s" % last_PostedSensorValue)

		# ---------------------#
		# -- add new config to the sensor-config.json --#

		new_sensor_configuration_record = {
			"value": {
				"sensor_type": sensor_type,
				"sensor_age": sensor_age,
				"sensor_max_value": sensor_max_value,
				"sensor_min_value": sensor_min_value,
				"soil_type": soil_type,
				"soil_irrigation_type": soil_irrigation_type,
				"soil_salinity": soil_salinity,
				"soil_bulk_density": soil_bulk_density,
				"soil_field_capacity" : soil_field_capacity,
				"plant_category" : plant_category,
				"plant_type": plant_type,
				"plant_variety": plant_variety,
				"plant_planting_date": plant_planting_date,
				"weather_region" : weather_region,
				"weather_weekly_evaporation" : weather_weekly_evaporation,
				"weather_weekly_pluviometry" : weather_weekly_pluviometry,
				"last_sensor_value": last_PostedSensorValue
			},
			"soil_temperature_source": {
				"soil_temperature_device_id": soil_temperature_device_id,
				"soil_temperature_sensor_id": soil_temperature_sensor_id,
				"soil_temperature_value": soil_temperature_value
			},
			"device_id": deviceID,
			"sensor_id": sensorID
		}

		# read sensors configurations
		with open(iiwa_sensors_config_filename, "r") as file:
			read_iiwa_sensor_configurations = json.load(file)['sensors']
		print("read_iiwa_sensor_configurations : %s" % read_iiwa_sensor_configurations)

		# ---------------------#
		# -- check if selected sensor id has an existing configuration and update it --#

		updated_new_sensorConfiguration = False
		read_iiwa_sensor_configurations_count = len(read_iiwa_sensor_configurations)

		# check if current sensor has an existing configuration and update it
		for x in range(0, read_iiwa_sensor_configurations_count):
			if (read_iiwa_sensor_configurations[x]['device_id'] == deviceID and read_iiwa_sensor_configurations[x]['sensor_id'] == sensorID):
				read_iiwa_sensor_configurations[x] = new_sensor_configuration_record
				updated_new_sensorConfiguration = True

		# if a sensor configuration as not been found then append new configuration
		if (updated_new_sensorConfiguration == False):
			read_iiwa_sensor_configurations.append(new_sensor_configuration_record)

		# update the global parameters, *** how will this be updated in future? ***
		new_iiwa_sensor_configuration = {
			"globals": {
				"soil_salinity": "undefined",
				"soil_bulk_density": "undefined",
				"soil_field_capacity" : "undefined",
				"weather_region" : "undefined",
				"weather_weekly_evaporation" : "undefined",
				"weather_weekly_pluviometry" : "undefined"
			},
			"sensors": read_iiwa_sensor_configurations
		}
			
		# update the configuration file with new values
		jsString = json.dumps(new_iiwa_sensor_configuration)
		jsFile = open(iiwa_sensors_config_filename, "w")
		jsFile.write(jsString)
		jsFile.close()

		return jsonify(new_iiwa_sensor_configuration)
	
	else:
		print("IIWA add sensor configuration : Invalid JSON body received!")
		return jsonify({"code" : 400,
			"message" :  "IIWA add sensor configuration : Invalid JSON body received!"})
# ---------------------#

# returns the sensor configuration data for a specific sensor given the deviceID and sensorID
@app.route("/devices/<deviceID>/sensors/<sensorID>", methods=['GET'])
def get_sensor_configuration(deviceID,sensorID ):
	deviceID = deviceID
	sensorID = sensorID

	# read sensors configurations
	with open(iiwa_sensors_config_filename, "r") as file:
		read_iiwa_sensor_configurations = json.load(file)['sensors']

	read_iiwa_sensor_configurations_count = len(read_iiwa_sensor_configurations)

	found_requested_sensor_configuration = False
	sensor_configuration = {}
	for x in range(0, read_iiwa_sensor_configurations_count):
		if (read_iiwa_sensor_configurations[x]['device_id'] == deviceID and read_iiwa_sensor_configurations[x]['sensor_id'] == sensorID):
			found_requested_sensor_configuration = True
			sensor_configuration = read_iiwa_sensor_configurations[x]
			print("IIWA get sensor configuration : Found configuration for the requested sensorID")
			print("IIWA get sensor configuration : %s" %read_iiwa_sensor_configurations[x])

			break

	if (found_requested_sensor_configuration):
		return jsonify(sensor_configuration)
	else:
		return jsonify({"code" : 409,
			"message" :  "IIWA get sensor configuration : submitted DeviceID/SensorID does not have a configuration"})
# ---------------------#

# returns all data in 'intel_irris_sensors_configurations.json'
@app.route("/sensors_configurations", methods=['GET'])
def sensors_configurations():
	f = open(iiwa_sensors_config_filename, 'r')
	read_sensors_configurations = json.loads(f.read())
	f.close()

	return jsonify(read_sensors_configurations)
# ---------------------#

# --------------------------------------------------------------------------
# REST APIs for fetching data from Wazigate-Edge
# --------------------------------------------------------------------------

# returns data of gateway devices
@app.route("/wazigate_devices", methods=['GET'])
def iiwa_request_wazigate_devices():
	if request.method == 'GET':
		url = BASE_URL+"devices"

		response = requests.get(url, headers=WaziGate_headers)
		data = response.json()

		# iterate over the gateway devices and remove the ones that have been added to IIWA
		del data[0]  # remove the gateway data
		gateway_devices_count = len(data)

		f = open(iiwa_devices_filename, 'r')
		iiwa_devices = json.loads(f.read())
		f.close()
		#del read_devices[0]
		IIWA_devices_count = len(iiwa_devices)

		for name in data.copy():
			for x in range(0, IIWA_devices_count):
				if name.get('name') == iiwa_devices[x]["device_name"]:
					data.remove(name)
            
		return jsonify(data)

# returns 200 or 404 to indicate if sensor or device id exists on WaziGate
@app.route("/exists_on_WaziGate_DeviceSensor_ID", methods=['GET'])
def exists_on_WaziGate_devicesensor_ID():
	if request.method == 'GET':
		device_id = request.args.get('deviceID')
		sensor_id = request.args.get('sensorID')

		url = BASE_URL+"devices/" + device_id + '/sensors/' + sensor_id

		response = requests.get(url, headers=WaziGate_headers)
		print("exists_on_WaziGate_devicesensor_ID Response status : %s"%response.status_code)
		if (response.status_code == 404):
			# make a DELETE request to IIWA API to remove the device ID from Intel-Irris
			print("exists_on_WaziGate_devicesensor_ID :  Removing %s Device ID from IIWA"%device_id)
			iiwa_remove_device_function(device_id)
			return jsonify([{"status": "404"}])
		elif (response.status_code == 200):
			return jsonify([{"status": "200"}])

"""
# returns sensors data of a device ID
@app.route("/get_WaziGate_deviceID_sensors", methods=['GET'])
def iiwa_request_device_sensors():
	if request.method == 'GET':
		device_id = request.args.get('deviceID')

		if device_id != 'undefined' and device_id != '':
			device_url = BASE_URL+"devices/" + device_id + '/sensors'
			response = requests.get(device_url, headers=WaziGate_headers)

			# check if a response is obtained for the deviceID
			if response.status_code == 200:
				data = response.json()
				print("get_WaziGate_deviceID_sensors : Device ID exists")
				return jsonify(data)
			elif response.status_code == 404:
				print("get_WaziGate_deviceID_sensors : Device ID does not exist!")
				# if a deviceID is found to not exist it is removed automatically
				iiwa_remove_device_function(device_id)
				return jsonify([{'status': '404'}])

		# handle when empty device id
		else:
			print("get_WaziGate_deviceID_sensors : no Device ID has been provided")
			return jsonify([{'status': '404'}])
"""