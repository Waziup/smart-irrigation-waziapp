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
		global_region = iiwa_sensors_config_data['globals']['region']

		iiwa_configured_sensors_count = len(iiwa_sensors_configurations)
		pop_indices = []
		for x in range(0, iiwa_configured_sensors_count):
			if (iiwa_sensors_configurations[x]['device_id'] == remove_device_id):
				pop_indices.append(x)

		for b in range(0, len(pop_indices)):
			iiwa_sensors_configurations.pop(pop_indices[b])

		print("IIWA : New sensor(s) configuration(s) data to be saved in JSON: %s" % iiwa_sensors_configurations)

		# save new data to config file
		new_iiwa_sensors_configurations = {
			"globals": {
				"soil_salinity": globals_soil_salinity,
				"soil_bulk_density": globals_soil_bulk_density,
				"region" : global_region
			},
			"sensors": iiwa_sensors_configurations
		}
		# update with the sensor config
		jsString = json.dumps(new_iiwa_sensors_configurations)
		jsFile = open(iiwa_sensors_config_filename, "w")
		jsFile.write(jsString)
		jsFile.close()

		return jsonify({"code" : 200,
				"message" :  "IIWA remove device : successfully removed the device and it's sensor(s) configuration(s)!"})
# ---------------------#

# returns list of IIWA devices
@app.route("/devices", methods=['GET'])
def get_iiwa_devices():
	f = open(iiwa_devices_filename, 'r')
	iiwa_devices = json.loads(f.read())
	f.close()

	return jsonify(iiwa_devices)
# ---------------------#

# returns Intel-Irris device data: device ID, sensor ID, device name, sensor type, last sensor value, soil type, soil condition
@app.route("/devices/data", methods=['GET'])
def devices_data():
	return jsonify(monitor_all_configured_sensors())

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
			soil_type = request.json['soil_type']
			soil_irrigation_type = request.json['soil_irrigation_type']
			soil_temperature_value = request.json['soil_temperature_value']
			soil_temperature_device_id = request.json['soil_temperature_device_id']
			soil_temperature_sensor_id = request.json['soil_temperature_sensor_id']
			plant = request.json['plant']
			plant_sub_type = request.json['plant_sub_type']
			planting_date = request.json['planting_date']
			global_soil_salinity = request.json['global_soil_salinity']
			global_soil_bulk_density = request.json['global_soil_bulk_density']
			global_region = request.json['global_region']

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
		if (plant == "hide"):
			plant = "undefined"
		if (plant_sub_type == "hide"):
			plant_sub_type = "undefined"
		if (planting_date == ""):
			planting_date = "undefined"
		if (global_region == "hide"):
			global_region = "undefined"

		if (global_soil_salinity != "" and global_soil_salinity != '-1'):
			global_soil_salinity = global_soil_salinity
		else:
			global_soil_salinity = "undefined"
		if (global_soil_bulk_density != "" and global_soil_bulk_density != '-1'):
			global_soil_bulk_density = global_soil_bulk_density
		else:
			global_soil_bulk_density = "undefined"

		# -- GET last sensor value --#
		url = BASE_URL+"devices/" + deviceID + '/sensors/' + sensorID
		response = requests.get(url, headers=WaziGate_headers)
		sensor_DataResponse = response.json()
		last_PostedSensorValue = sensor_DataResponse["value"]

		print("Sensor ID : %s" % sensorID)
		print("Sensor Type : %s" % sensor_type)
		print("Sensor Age : %s" % sensor_age)
		print("Sensor Max Value : %s" % sensor_max_value)
		print("Soil Type : %s" % soil_type)
		print("Soil Irrigation Type : %s" % soil_irrigation_type)
		print("Soil Salinity : %s" % global_soil_bulk_density)
		print("Soil Bulk Density : %s" % global_soil_bulk_density)
		print("Soil temperature value : %s" % soil_temperature_value)
		print("Soil temperature source device id : %s" %soil_temperature_device_id)
		print("Soil temperature source sensor id : %s" %soil_temperature_sensor_id)
		print("Plant : %s" % plant)
		print("Plant Sub-Type : %s" % plant_sub_type)
		print("Planting Date : %s" % planting_date)
		print("Region : %s" % global_region)
		print("Last sensor value : %s" % last_PostedSensorValue)

		# ---------------------#
		# -- add new config to the sensor-config.json --#

		new_sensor_configuration_record = {
			"value": {
				"sensor_type": sensor_type,
				"sensor_age": sensor_age,
				"sensor_max_value": sensor_max_value,
				"soil_type": soil_type,
				"soil_irrigation_type": soil_irrigation_type,
				"plant": plant,
				"plant_sub_type": plant_sub_type,
				"planting_date": planting_date,
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

		# update the global parameters
		new_iiwa_sensor_configuration = {
			"globals": {
				"soil_salinity": global_soil_salinity,
				"soil_bulk_density": global_soil_bulk_density,
				"region" : global_region
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

# returns data in sensor configuration file
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
@app.route("/exists_on_WaziGate_devicesensor_ID", methods=['GET'])
def exists_on_WaziGate_devicesensor_ID():
	if request.method == 'GET':
		device_id = request.args.get('deviceID')
		sensor_id = request.args.get('sensorID')

		url = BASE_URL+"devices/" + device_id + '/sensors/' + sensor_id

		response = requests.get(url, headers=WaziGate_headers)
		print("request_ifValid_devicesensor_ID Response status : %s"%response.status_code)
		if (response.status_code == 404):
			# make a DELETE request to IIWA API to remove the device ID from Intel-Irris
			print("monitor_all_configured_sensors :  Removing %s Device ID from IIWA"%deviceID)
			iiwa_remove_device_function(deviceID)
			return jsonify([{"status": "404"}])
		elif (response.status_code == 200):
			return jsonify([{"status": "200"}])

# returns sensors data of a device ID
@app.route("/device_sensors", methods=['GET'])
def iiwa_request_device_sensors():
	if request.method == 'GET':
		device_id = request.args.get('deviceID')

		if device_id[0] != '[':
			device_url = BASE_URL+"devices/" + device_id + '/sensors'

			response = requests.get(device_url, headers=WaziGate_headers)

			if response.status_code == 200:
				data = response.json()
				print("request-device-sensors : Device ID exists")
				return jsonify(data)
			elif response.status_code == 404:
				print("request-device-sensors : Device ID does not exist")
				return jsonify([{'status': '404'}])

		# handle when empty device id
		elif device_id[0] == '[':
			print("no device id has been provided")
			return jsonify([{'status': '409'}])