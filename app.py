from flask import Flask, render_template, request, jsonify
import requests, json, os
from os import path

app = Flask(__name__)

#--- config filepaths ---#
added_devices_filename = 'config/intel-irris-devices.json'
active_device_filename = 'config/intel-irris-active-device.json'
sensor_config_filename = 'config/intel-irris-conf.json'
#-----------------------#

#Waziup_URL="https://api.waziup.io/api/v2/" # uncomment for WaziCloud
Waziup_URL = "http://localhost/"           # uncomment for WaziGate

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

@app.route("/")
def dashboard():

    f = open(added_devices_filename, 'r')
    read_devices = json.loads(f.read())
    f.close()
    length = len(read_devices)

    no_devices = True
    added_devices = ""
    # check if there are devices in devices JSON
    if path.isfile(added_devices_filename) is False:  # Check if data.json file exists
        added_devices = "Config file for active device ID not found!"
    else:
        print("Config file for active device ID is found!")

        # check if the json list is updated
        if (length == 1):
            # instruct user to add a device
            no_devices = True
            added_devices = "No devices added to Intel-Irris. Go to the Device Manager to add one."
        else:
            no_devices = False
        #---------------------#

    if (no_devices == True):
        return render_template("intel-irris-dashboard.html",
                               added_devices=added_devices,
                               no_devices=no_devices)
    elif (no_devices == False):
        return render_template("intel-irris-dashboard.html",
                               no_devices=no_devices)
#---------------------#


@app.route("/intel-irris-devices", methods=['POST', 'GET'])
def intel_irris_device_manager():

    f = open(added_devices_filename, 'r')
    read_devices = json.loads(f.read())
    length = len(read_devices)
    f.close()

    #---------------------#
    #-- Manage selecting an active device from list and update active device --#
    if request.method == 'POST':  # get selected device name
        active_device = request.form.get('device-id-select')
        active_sensor_id = request.form.get('sensor-id-select')

        if (active_device is not None):  # write device_id to json
            print("Selected active device: %s" % active_device)

            active_device_dict = [{'device_id': active_device}]

            jsString = json.dumps(
                active_device_dict)  # convert python dic to JSON string
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

            jsString = json.dumps(active_device_sensor_dict)  # convert python dict to JSON 
            jsFile = open(active_device_filename, "w")
            jsFile.write(jsString)
            jsFile.close()
            print("Successfully updated active sensor id!")

    #---------------------#

    #-- Handle adding/removing a device_id from IIWA ---#
    if request.method == 'POST':  # get form input and add to json
        add_device_id = request.form.get('device_id')
        add_device_name = request.form.get('device_name')
        sensors_structure = request.form.get('sensors_structure')
        remove_device_id = request.form.get('device_id_remove')

        #-- Add a new device_id and device_name to json using html form ---#
        if (add_device_id is not None) and (add_device_name
                                            is not None) and (sensors_structure
                                                              is not None):
            # check if devices list has been updates

            if (length == 1):  # device list not updated
                print("Added device list not updated! Updating..")

                # write device_id as active one in json
                active_device_Dict = [{'device_id': add_device_id}]
                jsString = json.dumps(active_device_Dict)  # convert python dic to JSON string
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
            if (requested_removal_exists
                    and (not request_removed_from_active)):
                # open active device config
                active = open(active_device_filename, 'r')
                active_device = json.loads(active.read())
                # print(active_device)
                active.close()
                deviceID = active_device[0]['device_id']

                # check if active device matches requested removal and update active
                if (deviceID == remove_device_id):
                    print("Device id to remove was active id..resolving this..")
                    if (len(read_data) == 1):  # check if only one index is in list and empty active list
                        open(active_device_filename,
                             'w').close()  # empty json file
                        print("Found no other device id to use! No devices in IIWA :(")
                        request_removed_from_active = True

                    elif (len(read_data) > 1):  # if there are added device IDs, pick first and set as active
                        active_device_Dict = [{
                            'device_id':
                            read_data[1]['device_id']
                        }]

                        jsString = json.dumps(active_device_Dict)  # convert python dic to JSON string
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
                    #url = "http://localhost/devices/%s" % remove_device_id
                    #url = "https://api.waziup.io/api/v2/devices/%s" % remove_device_id
                    url = Waziup_URL + 'devices/' + remove_device_id
                    response = requests.get(url, headers=WaziGate_headers)

                    if response.status_code == 200:
                        device_data = response.json()
                        deviceID_exists = True
                        response_obtained = True
                    
                    elif response.status_code == 404:
                        print("The requested device ID to remove does not exist. Failed to request its sensors")
                        deviceID_exists = False
                        response_obtained = True

                if deviceID_exists: # if the device id exists, get its sensor and remove in sensor config file
                    device_sensors_num = len(device_data['sensors'])
                    # print("The device has %s sensor(s)"%no_sensors)

                    sensor_ids = []
                    for x in range(0, device_sensors_num):  # store sensor IDs
                        sensor_ids.append(device_data['sensors'][x]['id'])
                    #print("Sensors ids for the device are : %s"%sensor_ids)

                    with open(sensor_config_filename, "r") as file:
                        read_globals = json.load(file)

                    read_sensors = read_globals['sensors']
                    #print("read_sensors config : %s"%read_sensors)
                    globals_s_salinity = read_globals['globals']['global_soil_salinity']
                    globals_s_bulk_density = read_globals['globals']['global_soil_bulk_density']

                    config_sensors_count = len(read_sensors)
                    device_sensors_count = len(sensor_ids)
                    pop_indices = []
                    for x in range(0, config_sensors_count):
                        for y in range(0, device_sensors_count):
                            if (read_sensors[x]['sensor_id'] == sensor_ids[y] and read_sensors[x]['device_id'] == remove_device_id):
                                pop_indices.append(x)

                    if (len(pop_indices) != 0):
                        for b in range(0, len(pop_indices)):
                            read_sensors.pop(pop_indices[b])

                    print("New sensor config data : %s" % read_sensors)

                    # save new data to config file
                    update_config = {
                        "globals": {
                            "global_soil_salinity": globals_s_salinity,
                            "global_soil_bulk_density": globals_s_bulk_density
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
    no_active = True
    # check if an active device is set
    if (os.path.getsize(active_device_filename) == 0):  # no device added to Intel-Irris
        no_active = True
        no_sensor_config = True
    else:
        no_active = False

        #---------------------#
        # get the active device id
        active = open(active_device_filename, 'r')
        active_device = json.loads(active.read())
        print(active_device)
        deviceID = active_device[0]['device_id']
        print("Active device_id: %s" % deviceID)

        #---------------------#
        #-- Manage notifying user to add new config --#
        current_config_file = open(sensor_config_filename, 'r')
        current_config = json.loads(current_config_file.read())

        if (len(current_config['sensors']) == 0):  # check if sensor config list empty
            print("No sensor configurations made!")
            no_sensor_config = True
        else:
            no_sensor_config = False

        #---------------------#
        #-- Get submitted form data and add to config --#
        if request.method == 'POST':  # get selected device name
            sensor_id = request.form.get('sensor_id')
            sensor_type = request.form.get('sensor_type')
            sensor_age = request.form.get('sensor_age')
            sensor_max = request.form.get('sensor_max')
            sensor_min = request.form.get('sensor_min')
            region = request.form.get('region')
            soil_type = request.form.get('soil_type')
            irrigation_type = request.form.get('irrigation_type')
            crop = request.form.get('crop')
            plant_sub_type = request.form.get('plant_sub_type')
            planting_date = request.form.get('planting_date')
            global_soil_salinity = request.form.get('soil_salinity')
            global_soil_bulk_density = request.form.get('soil_bulk_density')

            soil_temperature_value = request.form.get('soil_temperature_value')
            soil_temperature_device_id = request.form.get('soil_temperature_device_id')
            soil_temperature_sensor_id = request.form.get('soil_temperature_sensor_id')

            #-- GET last sensor data of the device --#
            #url = "http://localhost/devices/%s" % deviceID
            #url = "https://api.waziup.io/api/v2/devices/%s" % deviceID
            url = Waziup_URL + 'devices/' + deviceID
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
                    #last_value = sensors_data['sensors'][i]['value']['value']
                    last_value = sensors_data['sensors'][i]['value']

            #-- Check for empty values in sumbitted data --#
            if (region == "hide"):
                region = "undefined"
            if (soil_type == "hide"):
                soil_type = "undefined"
            if (irrigation_type == "None"):
                irrigation_type = "undefined"
            if (crop == "hide"):
                crop = "undefined"
            if (plant_sub_type == "hide"):
                plant_sub_type = "undefined"
            if (planting_date == ""):
                planting_date = "undefined"
            if (global_soil_salinity == "" or global_soil_salinity == '-1'):
                global_soil_salinity = "disabled"  # means disabled
            if (global_soil_bulk_density == "" or global_soil_bulk_density == '-1'):
                global_soil_bulk_density = "disabled"  # means disabled
            if (soil_temperature_value == ""):
                soil_temperature_value = "undefined"
            if (soil_temperature_sensor_id == ""):
                soil_temperature_device_id = "undefined"
            if (soil_temperature_sensor_id == ""):
                soil_temperature_sensor_id = "undefined"

            if (global_soil_salinity != "" and global_soil_salinity != '-1'):
                global_soil_salinity = global_soil_salinity
            if (global_soil_bulk_density != "" and global_soil_bulk_density != '-1'):
                global_soil_bulk_density = global_soil_bulk_density

            print("Sensor ID : %s" % sensor_id)
            print("Sensor Type : %s" % sensor_type)
            print("Sensor Age : %s" % sensor_age)
            print("Sensor Max Value : %s" % sensor_max)
            print("Sensor Min Value : %s" % sensor_min)
            print("Region : %s" % region)
            print("Soil Type : %s" % soil_type)
            print("Irrigation Type : %s" % irrigation_type)
            print("Crop : %s" % crop)
            print("Plant Sub-Type : %s" % plant_sub_type)
            print("Planting Date : %s" % planting_date)
            print("Soil Salinity : %s" % global_soil_salinity)
            print("Soil Bulk Density : %s" % global_soil_bulk_density)
            print("Last Value : %s" % last_value)

            print("Soil temperature value : %s" % soil_temperature_value)
            print("Soil temperature source device id : %s" %
                  soil_temperature_device_id)
            print("Soil temperature source sensor id : %s" %
                  soil_temperature_sensor_id)

            #---------------------#
            #-- add new config to the sensor-config.json --#

            add_sensors = {
                "value": {
                    "sensor_type": sensor_type,
                    "sensor_age": sensor_age,
                    "sensor_max": sensor_max,
                    "sensor_min": sensor_min,
                    "region": region,
                    "soil_type": soil_type,
                    "irrigation_type": irrigation_type,
                    "crop": crop,
                    "plant_sub_type": plant_sub_type,
                    "planting_date": planting_date,
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
                if (read_sensors[x]['sensor_id'] == sensor_id and read_sensors[x]['device_id'] == deviceID):
                    read_sensors[x] = add_sensors

                    update_config = {
                        "globals": {
                            "global_soil_salinity": global_soil_salinity,
                            "global_soil_bulk_density":
                            global_soil_bulk_density
                        },
                        "sensors": read_sensors
                    }
                    # update with the sensor config
                    jsString = json.dumps(update_config)
                    jsFile = open(sensor_config_filename, "w")
                    jsFile.write(jsString)
                    jsFile.close()

                    updated = True
                    break

            if (updated == False):
                read_sensors.append(add_sensors)

                update_config = {
                    "globals": {
                        "global_soil_salinity": global_soil_salinity,
                        "global_soil_bulk_density": global_soil_bulk_density
                    },
                    "sensors": read_sensors
                }
                # update config file with new values
                jsString = json.dumps(update_config)
                jsFile = open(sensor_config_filename, "w")
                jsFile.write(jsString)
                jsFile.close()
            #---------------------#

        #---------------------#
    if (no_active):
        no_device = "No Devices added to Intel-Irris. Go to the Device Manager to add one."
        return render_template("intel-irris-sensor-config.html",
                               no_active=no_active,
                               no_device=no_device)
    else:
        return render_template("intel-irris-sensor-config.html",
                               no_active=no_active,
                               deviceID=deviceID)
#---------------------#

#--------------------------------------------------------------------------
#determine the soil condition string indication for capacitive
#--------------------------------------------------------------------------
capacitive_sensor_dry_max = 800
capacitive_sensor_wet_max = 0
capacitive_sensor_n_interval = 6
capacitive_sensor_soil_condition = []

capacitive_sensor_soil_condition.append('very dry')
capacitive_sensor_soil_condition.append('dry')
capacitive_sensor_soil_condition.append('dry-wet')
capacitive_sensor_soil_condition.append('wet-dry')
capacitive_sensor_soil_condition.append('wet')
capacitive_sensor_soil_condition.append('very wet')

get_value_index_from_local_database = False
obtained_value_index_from_local_database = False
set_value_index_in_local_database = True

global active_device_ID

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

#global BG_deviceID  # BG -> Back Ground
#global BG_sensorID
number_of_configurations = 0
fetch_last_value = False
four_04 = False
compute_humidityIndexValue = False


def monitor_sensor_value():

    if os.path.getsize(active_device_filename
                       ) != 0:  #check if there is a device added to IIWA
        f = open(active_device_filename, 'r')
        read_devices = json.loads(f.read())
        f.close()

        deviceID_key = 'device_id'
        sensorID_key = 'sensor_id'

        if deviceID_key in read_devices[0] and sensorID_key in read_devices[0]:
            BG_deviceID = read_devices[0]['device_id']
            BG_sensorID = read_devices[0]['sensor_id']

            f = open(sensor_config_filename)
            read_config = json.loads(f.read())
            f.close()

            number_of_configurations = len(read_config['sensors'])

            if (number_of_configurations > 0):
                for x in range(0, number_of_configurations):
                    if (read_config['sensors'][x]['sensor_id'] == BG_sensorID):
                        print("compute-index-service : current sensor id found in configuration")
                        sensor_lastValue = read_config['sensors'][x]['value']['last_value']['value']
                        print("compute-index-service : last sensor value in config is : %s" %sensor_lastValue)
                        fetch_last_value = True

                        break
                    elif (read_config['sensors'][x]['sensor_id'] != BG_sensorID):
                        fetch_last_value = False
                        compute_humidityIndexValue = False

                        print("compute-index-service : *** An error has occured!")
                        print("compute-index-service : Current sensor id has not been found in sensors configuration.")
                        print("compute-index-service : Goto Sensor Configuration Dashboard to configure the active sensor id ***")
                        break

            elif number_of_configurations == 0:
                print("compute-index-service : No sensor configuration has been made")
                print("compute-index-service : Sensor value will be requested for and index computation will be automatic")
                fetch_last_value = True

        elif deviceID_key not in read_devices[0] or sensorID_key not in read_devices[0]:
            print("compute-index-service : Error! Cannot proceed to compute humidity index value!")
            print("compute-index-service : Go to the Device Manager to add a device or sensor id.")
            fetch_last_value = False
            compute_humidityIndexValue = False

    elif os.path.getsize(active_device_filename) == 0:
        print("compute-index-service : No Devices added to Intel-Irris. Go to the Device Manager to add one.")
        fetch_last_value = False
        compute_humidityIndexValue = False

    if (fetch_last_value):
        #url = "https://api.waziup.io/api/v2/devices/" + BG_deviceID + '/sensors/' + BG_sensorID
        #url = "http://localhost/devices/" + BG_deviceID + '/sensors/' + BG_sensorID
        url = Waziup_URL + 'devices/' + BG_deviceID + '/sensors/' + BG_sensorID

        response = requests.get(url, headers=WaziGate_headers)

        if (response.status_code == 404):
            four_04 = True
            print("compute-index-service : Error 404! Check IDs of device and sensor of active device.")
        elif (response.status_code == 200):
            four_04 = False
            sensor_DataResponse = response.json()
            #last_PostedSensorValue = sensor_DataResponse['value']['value']
            last_PostedSensorValue = sensor_DataResponse["value"]
            print("compute-index-service : last posted sensor value was : %s" %last_PostedSensorValue)

            if number_of_configurations != 0:
                if (last_PostedSensorValue != sensor_lastValue):  # if sensor value has changed, compute index value
                    compute_humidityIndexValue = True
                    print("compute-index-service : Last posted sensor value has changed.. computing humidity index value.")
                elif (last_PostedSensorValue == sensor_lastValue):
                    compute_humidityIndexValue = False
                    print("compute-index-service : Last posted sensor value has not changed.. Not computing humidity index value.")
            elif (number_of_configurations == 0):
                print("compute-index-service : ..computing index value automatically..")
                get_capacitive_soil_condition(last_PostedSensorValue)

    if (compute_humidityIndexValue):
        get_capacitive_soil_condition(last_PostedSensorValue)


def get_ActiveDeviceID():
    f = open(active_device_filename, 'r')
    read_devices = json.loads(f.read())
    f.close()
    active_deviceID = read_devices[0]['device_id']

    return active_deviceID


def get_capacitive_soil_condition(raw_value):
    device_id = get_ActiveDeviceID()

    get_value_index_from_local_database = True
    if get_value_index_from_local_database:
        WaziGate_url = 'http://localhost/devices/' + device_id + '/sensors/temperatureSensor_0'
        try:
            response = requests.get(WaziGate_url,
                                    headers=WaziGate_headers,
                                    timeout=30)
            print('oled-service: returned msg from server is '),
            print(response.status_code)
            print(response.reason)

            if 200 <= response.status_code < 300:
                print('oled-service: GET success')
                print(response.text)
                device_json = json.loads(response.text)
                global value_index_capacitive
                value_index_capacitive = device_json["meta"]["value_index"]
                print(value_index_capacitive)
            else:
                print('oled-service: bad request')
                print(response.text)

        except requests.exceptions.RequestException as e:
            print(e)
            print('oled-service: requests command failed')

        print('=========================================')

        get_value_index_from_local_database = False
        obtained_value_index_from_local_database = True

    if obtained_value_index_from_local_database:
        value_interval = int(capacitive_sensor_dry_max /
                             capacitive_sensor_n_interval)
        #global value_index_capacitive
        value_index_capacitive = int(raw_value / value_interval)
        #in case the sensed value is greater than the maximum value defined
        if value_index_capacitive >= capacitive_sensor_n_interval:
            value_index_capacitive = capacitive_sensor_n_interval - 1

#we adopt the following rule: 0:very dry; 1:dry; 2:dry-wet 3-wet-dry; 4-wet; 5-very wet
#so for capacitive we need to invert the index
        value_index_capacitive = capacitive_sensor_n_interval - 1 - value_index_capacitive

    if set_value_index_in_local_database:
        my_token = "hello"
        #get the token first
        WaziGate_url = 'http://localhost/auth/token'
        try:
            pload = '{"username":"admin","password":"loragateway"}'
            response = requests.post(WaziGate_url,
                                     headers=WaziGate_headers,
                                     data=pload,
                                     timeout=30)
            print('oled-service: returned msg from server is '),
            print(response.status_code)
            print(response.reason)

            if 200 <= response.status_code < 300:
                print('oled-service: POST success')
                print(response.text)
                my_token = response.text
            else:
                print('oled-service: bad request')
                print(response.text)

        except requests.exceptions.RequestException as e:
            print(e)
            print('oled-service: requests command failed')

        print('=========================================')

        WaziGate_url = 'http://localhost/devices/' + device_id + '/sensors/temperatureSensor_0/meta'
        try:
            pload = '{"value_index":' + str(value_index_capacitive) + '}'
            WaziGate_headers_auth['Authorization'] = 'Bearer' + my_token[1:-2]
            response = requests.post(WaziGate_url,
                                     headers=WaziGate_headers_auth,
                                     data=pload,
                                     timeout=30)
            print('oled-service: returned msg from server is '),
            print(response.status_code)
            print(response.reason)

            if 200 <= response.status_code < 300:
                print('oled-service: POST success')
                print(response.text)

            else:
                print('oled-service: bad request')
                print(response.text)

        except requests.exceptions.RequestException as e:
            print(e)
            print('oled-service: requests command failed')

        print('=========================================')

#---------------------#
# periodically comppute humidity index value
import threading
computing_interval_sec = 10  # seconds
def foo():
    monitor_sensor_value()
    threading.Timer(computing_interval_sec, foo).start()
foo()

#---------------------# Route methods for accessing config data
@app.route("/intel-irris-added-devices",
           methods=['GET'])  # returns list of added devices
def intel_irris_added_devices():
    if request.method == 'GET':
        f = open(added_devices_filename, 'r')
        read_devices = json.loads(f.read())
        f.close()

        return jsonify(read_devices)


@app.route("/intel-irris-active-device",
           methods=['GET'])  # returns device id of active device
def intel_irris_active_device():
    if request.method == 'GET':
        if os.path.getsize(active_device_filename) != 0:
            f = open(active_device_filename, 'r')
            active_device_id = json.loads(f.read())
            active_device_id = active_device_id[0]['device_id']
            f.close()

            return jsonify(active_device_id)

        elif os.path.getsize(active_device_filename) == 0:
            return jsonify('[]')


@app.route("/intel-irris-active-device-sensor",
           methods=['GET'])  # returns data in active device config
def intel_irris_active_device_sensor():
    if request.method == 'GET':
        f = open(active_device_filename, 'r')
        active_device_id = json.loads(f.read())
        f.close()

        return jsonify(active_device_id)


@app.route("/intel-irris-sensor-configurations",
           methods=['GET'])  # returns data in sensor configurations
def intel_irris_sensor_configurations():
    if request.method == 'GET':
        f = open(sensor_config_filename, 'r')
        configurations = json.loads(f.read())
        f.close()

        return jsonify(configurations)

#---------------------#

#---------------------# Route methods for making GET requests (JS fix)
@app.route("/request-gateway-devices", methods=['GET']) # returns data of gateway devices
def request_gateway_devices():
    if request.method == 'GET':
        #url = "http://localhost/devices"
        #url = "https://api.waziup.io/api/v2/devices/"
        url = Waziup_URL + 'devices'

        response = requests.get(url, headers=WaziGate_headers)
        data = response.json()

        return jsonify(data)


@app.route("/check-device-sensor-id", methods=['GET']) # returns 200 or 404 to indicate if sensor or device id is valid/invalid
def check_sensor_id():
    if request.method == 'GET':
        device_id = request.args.get('deviceID')
        sensor_id = request.args.get('sensorID')
        
        #url = "https://api.waziup.io/api/v2/devices/" + device_id + '/sensors/' + sensor_id
        #url = "http://localhost/devices/" + device_id + '/sensors/' + sensor_id
        url = Waziup_URL + 'devices/' + device_id + '/sensors/' + sensor_id

        response = requests.get(url, headers=WaziGate_headers)
        if (response.status_code == 404):
            return jsonify([{"status": "404"}])
        elif (response.status_code == 200):
            return jsonify([{"status": "200"}])


@app.route("/request-device-sensors", methods=['GET']) # returns sensors data of a device ID
def request_device_sensors():
    if request.method == 'GET':
        device_id = request.args.get('deviceID')

        if device_id[0] != '[':
            #device_url = 'https://api.waziup.io/api/v2/devices/' + device_id + '/sensors'
            #device_url = 'http://localhost/devices/' + device_id + '/sensors'
            device_url = Waziup_URL + 'devices/' + device_id + '/sensors'

            response = requests.get(device_url, headers=WaziGate_headers)

            if response.status_code == 200:
                data = response.json()
                print("Device ID exists")
                return jsonify(data)
            elif response.status_code == 404:
                print("Device ID does not exist")
                return jsonify([{'status':'404'}])

        elif device_id[0] == '[': # handle when empty device id
            print("no device id has been provided")
            return jsonify([{'status':'404'}])


@app.route("/request-sensor-values", methods=['GET']) # returns sensor values
def request_sensor_values():
    if request.method == 'GET':
        device_id = request.args.get('deviceID')
        sensor_id = request.args.get('sensorID')

        #sensorValues_url = "https://api.waziup.io/api/v2/devices/" + device_id + "/sensors/" + sensor_id + "/values"
        #sensorValues_url = "http://localhost/devices/" +device_id + "/sensors/" + sensor_id + "/values"
        sensorValues_url = Waziup_URL + 'devices/' + device_id + "/sensors/" + sensor_id + "/values"
        response = requests.get(sensorValues_url, headers=WaziGate_headers)
        data = response.json()

        return jsonify(data)


#---------------------#

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    #app.run(host='unix:///app/intel-irris-waziapp/proxy.sock',use_reloader=False,debug=True)