import threading
from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from os import path
from datetime import datetime
from werkzeug.serving import run_simple

app = Flask(__name__)

import iiwa_apis  # import script for making REST APIs

# --------------------------------------------------------------------------
# argument to define if continuous_computation() will run periodically in background 
# --------------------------------------------------------------------------
import argparse
iiwa_argumentparser = argparse.ArgumentParser()
iiwa_argumentparser.add_argument('--continuous-computation', dest='continuous_computation', type=str, help='Defines if monitor_all_configured_sensors will run periodically')
iiwa_argument = iiwa_argumentparser.parse_args()

"""
to disable continuous_computation() we pass the argument as false, ie
  python app.py --continuous-computation false
"""
# by default IIWA will periodically run the countinuous_computation() in background
iiwa_run_continuous_computation = True

# in seconds
continuous_computation_interval_sec = 10

if (iiwa_argument.continuous_computation == "false"):
	print("=== IIWA continuous index value computation has been disabled! ===")
	iiwa_run_continuous_computation = False
# ---------------------#

# --- IIWA configurations filepaths ---#
iiwa_devices_filename = 'config/intel_irris_devices.json'
iiwa_sensors_config_filename = 'config/intel_irris_sensors_configurations.json'
# -----------------------#

# only for soil condition, 'fr' or 'en'
iiwa_lang = 'en'

BASE_URL = "http://localhost/"

# common headers for requests
iiwa_headers = {
	'content-type': 'application/json'
}
WaziGate_headers = {
	'accept': 'application/json',
	'content-type': 'application/json'
}
WaziGate_headers_auth = {
	'accept': 'application/json',
	'content-type': 'application/json',
	'Authorization': 'Bearer **'
}
# ---------------------#

sensor_max_capacitive = "800"
sensor_max_tensiometer_cbar = "124"
sensor_max_tensiometer_raw = "18000"

# ---------------------#

# --------------------------------------------------------------------------
# route methods for returning the HTML pages
# --------------------------------------------------------------------------

# returns the homepage (Dashboard) of IIWA
@app.route("/")
def dashboard():
	# check if there are added devices in devices JSON
	if path.isfile(iiwa_devices_filename) is False:  # Check if data.json file exists
		added_devices = "Cannot find intel_irris_devices.json!"
		no_iiwa_devices = True
	else:
		print("Found list of added IIWA devices!")

		f = open(iiwa_devices_filename, 'r')
		iiwa_devices = json.loads(f.read())
		f.close()

		iiwa_devices_count = len(iiwa_devices)

		added_devices = ""

		# check if the json list is updated
		if (iiwa_devices_count == 0):
			# instruct user to add a device
			no_iiwa_devices = True
			added_devices = "No Wazigate devices have been added to IIWA! Use the Device Manager to add some."
		else:
			no_iiwa_devices = False

	if (no_iiwa_devices == True):
		return render_template("intel_irris_dashboard.html",
			added_devices=added_devices,
			no_iiwa_devices=no_iiwa_devices
			)
			
	elif (no_iiwa_devices == False):
		return render_template("intel_irris_dashboard.html",
			no_iiwa_devices=no_iiwa_devices)
# ---------------------#

# returns Device Manager HTML page
# allow POST method for the html form actions on this page
@app.route("/intel_irris_device_manager", methods=['POST','GET'])
def intel_irris_device_manager():
	f = open(iiwa_devices_filename, 'r')
	iiwa_devices = json.loads(f.read())
	iiwa_devices_length = len(iiwa_devices)
	f.close()

	return render_template("intel_irris_device_manager.html")
# ---------------------#

# returns Sensor Configurator HTML page
# allow POST method for the html form actions on this page
@app.route("/intel_irris_sensor_configurator", methods=['POST', 'GET'])
def intel_irris_sensor_configurator():
	deviceID = request.args.get('deviceID')
	deviceName = get_deviceName(deviceID)
	sensorID = 'temperatureSensor_0'
	
	return render_template("intel_irris_sensor_configurator.html",
		deviceID = deviceID,
		deviceName = deviceName,
		sensorID = sensorID)
# ---------------------#

# --------------------------------------------------------------------------
# determine the soil condition string indication for capacitive
# --------------------------------------------------------------------------

default_capacitive_sensor_dry_max = 800
capacitive_sensor_dry_max = default_capacitive_sensor_dry_max
capacitive_sensor_wet_max = 0
capacitive_sensor_n_interval = 6
capacitive_sensor_soil_condition = []
# we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-saturated

if iiwa_lang == "fr":
	capacitive_sensor_soil_condition.append('très sec')
	capacitive_sensor_soil_condition.append('sec')
	capacitive_sensor_soil_condition.append('sec')
	capacitive_sensor_soil_condition.append('hum')
	capacitive_sensor_soil_condition.append('hum')
	capacitive_sensor_soil_condition.append('saturé')
else:
	capacitive_sensor_soil_condition.append('very dry')
	capacitive_sensor_soil_condition.append('dry')
	capacitive_sensor_soil_condition.append('dry')
	capacitive_sensor_soil_condition.append('wet')
	capacitive_sensor_soil_condition.append('wet')
	capacitive_sensor_soil_condition.append('saturated')

# --------------------------------------------------------------------------
# determine the soil condition string indication for watermark tensiometer
# --------------------------------------------------------------------------

default_tensiometer_sensor_dry_max = 120
tensiometer_sensor_dry_max = default_tensiometer_sensor_dry_max
tensiometer_sensor_wet_max = 0
tensiometer_sensor_n_interval = 6
tensiometer_sensor_soil_condition = []
# we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-saturated

use_irrometer_interval_for_tensiometer = True

if iiwa_lang == "fr":
	tensiometer_sensor_soil_condition.append('très sec')
	tensiometer_sensor_soil_condition.append('sec')
	tensiometer_sensor_soil_condition.append('sec')
	tensiometer_sensor_soil_condition.append('hum')
	tensiometer_sensor_soil_condition.append('hum')
	tensiometer_sensor_soil_condition.append('saturé')
else:
	tensiometer_sensor_soil_condition.append('very dry')
	tensiometer_sensor_soil_condition.append('dry')
	tensiometer_sensor_soil_condition.append('dry')
	tensiometer_sensor_soil_condition.append('wet')
	tensiometer_sensor_soil_condition.append('wet')
	tensiometer_sensor_soil_condition.append('saturated')

# --------------------------------------------------------------------------
# parameters for periodic monitor_sensor_value()
# --------------------------------------------------------------------------

# here we read from meta.value_index
get_value_index_from_local_database = True
# here we set in meta.value_index_iiwa
set_value_index_in_local_database = True
# set to True to compute value_index_iiwa for all configured device/sensor pairs, otherwise only the active one
iterate_over_all_configured_devices = True
# ---------------------#

# --------------------------------------------------------------------------
# function to compute the index value for all sensors taking into consideration the sensor type
# --------------------------------------------------------------------------
# the computed data is returned by the function and it is used for the Dashboard
def monitor_all_configured_sensors():

	# store the device and sensor data in JSON and return it
	"""
	iiwa_devices_data structure:
	{
		"device_id": deviceID,
		"device_name" : deviceName,
		"sensor_id" : sensorID,
		"sensor_type" : sensor_type,
		"value_index" : value_index,
		"soil_condition" : soil_condition,
		"sensor_value" : sensor_value
	}
	"""
	iiwa_devices_data = []

	sensor_type = 'undefined'
	soil_type = 'undefined'
	value_index = 'undefined'
	soil_condition = ''
	sensor_value = ''

	number_of_iiwa_configurations = 0
	
	if os.path.getsize(iiwa_sensors_config_filename) != 0:
		f = open(iiwa_sensors_config_filename)
		read_iiwa_configurations = json.loads(f.read())
		f.close()

		number_of_iiwa_configurations = len(read_iiwa_configurations['sensors'])

		if (number_of_iiwa_configurations > 0):
			for x in range(0, number_of_iiwa_configurations):
				deviceID = read_iiwa_configurations['sensors'][x]['device_id']
				sensorID = read_iiwa_configurations['sensors'][x]['sensor_id']
				deviceName = get_deviceName(deviceID)

				# check if device and sensor IDs exist in Wazigate-Edge
				url = BASE_URL+"devices/" + deviceID + '/sensors/' + sensorID

				print('monitor_all_configured_sensors : checking for', deviceID, sensorID)

				response = requests.get(url, headers=WaziGate_headers)

				if (response.status_code == 404 or deviceName == 'not_iiwa_device'):
					print("monitor_all_configured_sensors : Error 404! Check IDs of device and sensor of configured device")

					# make a DELETE request to IIWA API to remove the device ID from Intel-Irris
					print("monitor_all_configured_sensors :  Removing %s Device ID from IIWA"%deviceID)
					iiwa_remove_device_function(deviceID)

				elif (response.status_code == 200 and deviceName != 'not_iiwa_device'):
					sensor_DataResponse = response.json()
					last_PostedSensorValue = sensor_DataResponse["value"]

					print("monitor_all_configured_sensors : last posted sensor value was %s"%last_PostedSensorValue)

					sensor_type = read_iiwa_configurations['sensors'][x]['value']['sensor_type']
					soil_type = read_iiwa_configurations['sensors'][x]['value']['soil_type']
					sensor_value = str(last_PostedSensorValue)

					if sensor_type == 'capacitive':
						capacitive_soil_index_and_condition = get_capacitive_soil_condition(
							last_PostedSensorValue, deviceID, sensorID, read_iiwa_configurations['sensors'][x])
						value_index = capacitive_soil_index_and_condition[0]
						soil_condition = capacitive_soil_index_and_condition[1]

					if 'tensiometer' in sensor_type:
						tensiometer_soil_index_and_condition = get_tensiometer_soil_condition(
							last_PostedSensorValue, deviceID, sensorID, read_iiwa_configurations['sensors'][x])		
						value_index = tensiometer_soil_index_and_condition[0]
						soil_condition = tensiometer_soil_index_and_condition[1]
					
					iiwa_devices_data.append({
						"device_id": deviceID,
						"device_name" : deviceName,
						"sensor_id" : sensorID,
						"sensor_type" : sensor_type,
						"value_index" : value_index,
						"soil_condition" : soil_condition,
						"sensor_value" : sensor_value					
					})
				
				# reset variables
				sensor_type = 'undefined'
				soil_type = 'undefined'
				value_index = 'undefined'
				soil_condition = ''
				sensor_value = ''

			return iiwa_devices_data

	else:
		print("monitor_all_configured_sensors : No sensor configuration has been made")
		# return None if no sensor configuration is available
		return(0)
# ---------------------#

# --------------------------------------------------------------------------
# determine the soil condition string indication for capacitive
# --------------------------------------------------------------------------

clay_capacitive_sensor_dry_max = 400
sandy_capacitive_sensor_dry_max = 700
silty_capacitive_sensor_dry_max = 500
peaty_capacitive_sensor_dry_max = 500
chalky_capacitive_sensor_dry_max = 500
loamy_capacitive_sensor_dry_max = 500

def get_capacitive_sensor_dry_max(sensor_config):

	print("soil type is", sensor_config["value"]["soil_type"])

	if sensor_config["value"]["soil_type"] == "clay":
		return clay_capacitive_sensor_dry_max

	if sensor_config["value"]["soil_type"] == "sandy":
		return sandy_capacitive_sensor_dry_max

	if sensor_config["value"]["soil_type"] == "silty":
		return silty_capacitive_sensor_dry_max

	if sensor_config["value"]["soil_type"] == "peaty":
		return peaty_capacitive_sensor_dry_max

	if sensor_config["value"]["soil_type"] == "chalky":
		return chalky_capacitive_sensor_dry_max

	if sensor_config["value"]["soil_type"] == "loamy":
		return loamy_capacitive_sensor_dry_max

	return default_capacitive_sensor_dry_max

# TODO use BASE_URL

def get_capacitive_soil_condition(raw_value, device_id, sensor_id, sensor_config):

	capacitive_soil_condition = ''
	if get_value_index_from_local_database:
		WaziGate_url = 'http://localhost/devices/' + device_id + '/sensors/' + sensor_id
		try:
			response = requests.get(
				WaziGate_url, headers=WaziGate_headers, timeout=30)
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

	# now we compute
	if raw_value == -1:
		value_index_capacitive = -1
	else:
		value_interval = int(get_capacitive_sensor_dry_max(
			sensor_config) / capacitive_sensor_n_interval)
		value_index_capacitive = int(raw_value / value_interval)
		# in case the sensed value is greater than the maximum value defined
		if value_index_capacitive >= capacitive_sensor_n_interval:
			value_index_capacitive = capacitive_sensor_n_interval - 1

		# we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-saturated
		# so for capacitive we need to invert the index
		value_index_capacitive = capacitive_sensor_n_interval - 1 - value_index_capacitive

	print('computed value_index (capacitive) =', value_index_capacitive)

	if value_index_capacitive == -1:
		capacitive_soil_condition = 'no sensor'
	else:
		capacitive_soil_condition = capacitive_sensor_soil_condition[value_index_capacitive]

	print('soil condition =', capacitive_soil_condition)
	print('=========================================')

	if set_value_index_in_local_database:
		my_token = "hello"
		# get the token first
		WaziGate_url = 'http://localhost/auth/token'
		try:
			pload = '{"username":"admin","password":"loragateway"}'
			response = requests.post(
				WaziGate_url, headers=WaziGate_headers, data=pload, timeout=30)
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

		WaziGate_url = 'http://localhost/devices/' + \
			device_id + '/sensors/' + sensor_id + '/meta'
		try:
			timestr = datetime.utcnow().isoformat()[:-3]+'Z'
			pload = '{"value_index_iiwa":' + str(
				value_index_capacitive) + ', "value_index_iiwa_time":"' + timestr + '"' + '}'
			WaziGate_headers_auth['Authorization'] = 'Bearer' + my_token[1:-2]
			response = requests.post(
				WaziGate_url, headers=WaziGate_headers_auth, data=pload, timeout=30)
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

	# return a tuple
	return value_index_capacitive, capacitive_soil_condition
# ---------------------#

# --------------------------------------------------------------------------
# determine the soil condition string indication for tensiometer
# --------------------------------------------------------------------------

def get_tensiometer_sensor_dry_max(sensor_config):

	print("soil type is", sensor_config["value"]["soil_type"])

	return default_tensiometer_sensor_dry_max

# TODO use BASE_URL
# TODO use raw resistor value to compute centibar and link with soil temperature

def get_tensiometer_soil_condition(raw_value, device_id, sensor_id, sensor_config):

	tensiometer_soil_condition = ''
	if get_value_index_from_local_database:
		WaziGate_url = 'http://localhost/devices/' + device_id + '/sensors/' + sensor_id
		try:
			response = requests.get(
				WaziGate_url, headers=WaziGate_headers, timeout=30)
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

	# now we compute
	if use_irrometer_interval_for_tensiometer:
		# from irrometer: https://www.irrometer.com/basics.html
		# 0-10 Centibars = Saturated soil
		# 10-30 Centibars = Soil is adequately wet (except coarse sands, which are drying)
		# 30-60 Centibars = Usual range for irrigation (most soils)
		# 60-100 Centibars = Usual range for irrigation in heavy clay
		# 100-200 Centibars = Soil is becoming dangerously dry- proceed with caution!
		#
		# we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-very wet/saturated

		print("soil type is", sensor_config["value"]["soil_type"])

		if raw_value == 255:
			value_index_tensiometer = -1
		elif raw_value == 240:
			value_index_tensiometer = -2
		elif raw_value > 100:
			value_index_tensiometer = 0
		elif raw_value > 60:
			value_index_tensiometer = 1
		elif raw_value > 30:
			value_index_tensiometer = 2
		elif raw_value > 10:
			value_index_tensiometer = 4
		else:
			value_index_tensiometer = 5
	else:
		value_interval = int(get_tensiometer_sensor_dry_max(
			sensor_config)/tensiometer_sensor_n_interval)
		value_index_tensiometer = int(raw_value/value_interval)
		# in case the sensed value is greater than the maximum value defined
		if value_index_tensiometer >= tensiometer_sensor_n_interval:
			value_index_tensiometer = tensiometer_sensor_n_interval-1

		# we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-very wet/saturated
		# so for tensiometer we need to invert the index
		value_index_tensiometer = tensiometer_sensor_n_interval-1-value_index_tensiometer

	print('computed value_index (tensiometer) =', value_index_tensiometer)

	if value_index_tensiometer == -1:
		tensiometer_soil_condition = 'no sensor'
	elif value_index_tensiometer == -2:
		tensiometer_soil_condition = 'err'
	else:
		tensiometer_soil_condition = tensiometer_sensor_soil_condition[value_index_tensiometer]

	print('soil condition =', tensiometer_soil_condition)
	print('=========================================')

	if set_value_index_in_local_database:
		my_token = "hello"
		# get the token first
		WaziGate_url = 'http://localhost/auth/token'
		try:
			pload = '{"username":"admin","password":"loragateway"}'
			response = requests.post(
				WaziGate_url, headers=WaziGate_headers, data=pload, timeout=30)
			print('get-tensiometer: returned msg from server is '),
			print(response.status_code)
			print(response.reason)

			if 200 <= response.status_code < 300:
				print('get-tensiometer: POST success')
				print(response.text)
				my_token = response.text
			else:
				print('get-tensiometer: bad request')
				print(response.text)

		except requests.exceptions.RequestException as e:
			print(e)
			print('get-tensiometer: requests command failed')

		print('=========================================')

		WaziGate_url = 'http://localhost/devices/' + \
			device_id + '/sensors/' + sensor_id + '/meta'
		try:
			timestr = datetime.utcnow().isoformat()[:-3]+'Z'
			pload = '{"value_index_iiwa":' + str(
				value_index_tensiometer) + ', "value_index_iiwa_time":"' + timestr + '"' + '}'
			WaziGate_headers_auth['Authorization'] = 'Bearer'+my_token[1:-2]
			response = requests.post(
				WaziGate_url, headers=WaziGate_headers_auth, data=pload, timeout=30)
			print('get-tensiometer: returned msg from server is '),
			print(response.status_code)
			print(response.reason)

			if 200 <= response.status_code < 300:
				print('get-tensiometer: POST success')
				print(response.text)
			else:
				print('get-tensiometer: bad request')
				print(response.text)

		except requests.exceptions.RequestException as e:
			print(e)
			print('get-tensiometer: requests command failed')

		print('=========================================')

	# return a tuple
	return value_index_tensiometer,tensiometer_soil_condition
# ---------------------#

# --------------------------------------------------------------------------
# function that returns the soil temperature value based on the selected source
# --------------------------------------------------------------------------
def get_linked_soil_temperature(device_id, sensor_id):
	device_ID = device_id
	sensor_ID = sensor_id
	f = open(iiwa_sensors_config_filename)
	read_iiwa_configurations = json.loads(f.read())
	f.close()
	print("=========================================")
	print("getting linked temperature value :")

	number_of_sensor_configs = len(read_iiwa_configurations['sensors'])

	for x in range(0, number_of_sensor_configs):
		# first get the index of the target sensor
		if read_iiwa_configurations['sensors'][x]['device_id'] == device_ID and read_iiwa_configurations['sensors'][x]['sensor_id'] == sensor_ID:

			# get a defined soil temperature value
			if read_iiwa_configurations['sensors'][x]['soil_temperature_source']['soil_temperature_value'] != 'undefined':
				temperature_value = float(
					read_iiwa_configurations['sensors'][x]['soil_temperature_source']['soil_temperature_value'])
				print("OK! Read soil temperature value")
				print(temperature_value)
				print("=========================================")

				return temperature_value

			# get a defined soil temperature value from the active sensor
			elif read_iiwa_configurations['sensors'][x]['soil_temperature_source']['soil_temperature_device_id'] == device_ID and read_iiwa_configurations['sensors'][x]['soil_temperature_source']['soil_temperature_sensor_id'] == sensor_ID:
				sensorValue_url = BASE_URL+"devices/" + \
					device_ID + "/sensors/" + sensor_ID + "/value"
				response = requests.get(
					sensorValue_url, headers=WaziGate_headers)

				if response.status_code == 200:
					print("OK! Fetched soil temperature value from active sensor")
					temperature_value = float(response.json())
					print(temperature_value)
					print("=========================================")

					return temperature_value

				else:
					print("Unable to fetch soil temperature value! Check the device/sensor ID(s)")
					print("=========================================")

			else:
				print("Unable to find soil temperature source from sensor configuration")
				print("=========================================")
		else:
			print("sensor ID not found in the IIWA configuration!")
			print("=========================================")
# ---------------------#

# --------------------------------------------------------------------------
# function that returns IIWA device name given a deviceID
# --------------------------------------------------------------------------
def get_deviceName(deviceID):
	deviceID = deviceID
	device_name = ''
	# 1. Read IIWA devices
	with open(iiwa_devices_filename, "r") as file:
		iiwa_devices = json.load(file)
	
	deviceID_exists = False
	for x in range(0, len(iiwa_devices)):
		if (iiwa_devices[x]['device_id'] == deviceID):
			deviceID_exists = True
			device_name = iiwa_devices[x]['device_name']
			break
	
	if deviceID_exists:
		return device_name
	else:
		print("get_deviceName : DeviceID %s is not a Wazigate device!"%deviceID)
		return 'not_iiwa_device'
# ---------------------#

# --------------------------------------------------------------------------
# function that removes an device from IIWA given the deviceID
# --------------------------------------------------------------------------
def iiwa_remove_device_function(deviceID):
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
		print("IIWA : New sensor(s) configuration(s) data to be saved in JSON: %s" % iiwa_sensors_configurations)
		# update with the sensor config
		jsString = json.dumps(new_iiwa_sensors_configurations)
		jsFile = open(iiwa_sensors_config_filename, "w")
		jsFile.write(jsString)
		jsFile.close()

		return jsonify({"code" : 200,
				"message" :  "IIWA remove device : successfully removed the device and it's sensor(s) configuration(s)!"})
# ---------------------#

# --------------------------------------------------------------------------
# function to periodically compute humidity index value
# --------------------------------------------------------------------------
def continuous_computation():
	if iterate_over_all_configured_devices == True:
		monitor_all_configured_sensors()

	threading.Timer(continuous_computation_interval_sec, continuous_computation).start()

if (iiwa_run_continuous_computation):
	continuous_computation()
# ---------------------#

# --------------------------------------------------------------------------
# define IP address, port and debugging mode of Flask App
# --------------------------------------------------------------------------
if __name__ == "__main__":
	# Run on IP address of the host computer at Port 5000
	app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
# ---------------------#
