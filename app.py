from codecs import xmlcharrefreplace_errors
from flask import Flask, render_template, request
import requests, json, os
from os import path

app = Flask(__name__)

added_devices_filename = 'config/intel-irris-devices.json'
active_device_filename = 'config/intel-irris-active-device.json'
sensor_config_filename = 'config/intel-irris-conf.json'


#---------------------#
@app.route("/")
def dashboard():

    f = open(added_devices_filename , 'r')
    read_devices = json.loads(f.read())
    length = len(read_devices)

    no_devices = True
    added_devices = ""
    # check if there are devices in devices JSON
    if path.isfile(added_devices_filename) is False: # Check if data.json file exists
        added_devices = "Config file for active device ID not found!"
        print(added_devices)
    else:
        print("Config file for active device ID found!")

        # check if the json list is updated

        if (length == 1):
            # instruct user to add a device
            no_devices = True
            added_devices = "No devices added to Intel-Irris. Go to the Device Manager to add one." 
        #---------------------#  
        else: # show sensor data of current device in html table
            no_devices = False
            # open active device config
            active = open(active_device_filename, 'r')
            active_device = json.loads(active.read())
            # print(active_device)
            deviceID = active_device[0]['device_id']
            print("Active device_id: %s"%deviceID)

            #---------------------#  
            #-- GET sensor data of the device --#
            url = "http://waziup.wazigate-edge/devices/%s"%deviceID 
            #url = "https://api.waziup.io/api/v2/devices/%s"%deviceID
            headers = {
                'accept': 'application/json',
                }
            response = requests.get(url, headers=headers)
            sensors_data = response.json()
            #print(data) # uncomment to see the JSON data
            
            # obtain sensor ID
            sensorID = sensors_data['sensors'][0]['id']
            # obtain the soil sensor value
            soil_moisture = sensors_data['sensors'][0]['value']['value'] 

            # insights indicators : 
            """
            Range   |   Insight    |    Color
            _____       _______         _____

            0-195       very wet        light blue
            196-390     wet             green
            391-585     dry             orange
            586-780     very dry        red
 
            """
            print("Soil moisture sensor ID = %s"%sensorID)
            print("Last sensor value = %s"%soil_moisture)

        #---------------------#
    
    if (no_devices == True):
        return render_template("intel-irris-dashboard.html", added_devices=added_devices, no_devices=no_devices)
    elif (no_devices == False):
        return render_template("intel-irris-dashboard.html", added_devices=added_devices, no_devices=no_devices, deviceID=deviceID, sensorID=sensorID, soil_moisture=soil_moisture)

#---------------------#

@app.route("/intel-irris-devices", methods = ['POST', 'GET'])
def intel_irris_device_manager():
    
    f = open(added_devices_filename , 'r')
    read_devices = json.loads(f.read())
    length = len(read_devices)

    #---------------------#
    #-- Manage selecting an active device from list and update active device --#
    if request.method == 'POST': # get selected device name
        active_device = request.form.get('device-id-select')

        if (active_device is not None): # write device_id to json
            print("Selected active device: %s"%active_device)

            active_device_dict = [{'device_id':active_device}]

            jsString = json.dumps(active_device_dict) # convert python dic to JSON string
            jsFile = open(active_device_filename, "w")
            jsFile.write(jsString)
            jsFile.close() 
            print("Updated active device!")
    #---------------------#

    #-- Add a new device_id and device_name to json using html form ---#
    if request.method == 'POST': # get form input and add to json
        add_device_id = request.form.get('device_id')
        add_device_name = request.form.get('device_name')
        
        if (add_device_id is not None) and (add_device_name is not None):
            # check if devices list has been updates

            if (length == 1): # device list not updated
                print("Added device list not updated! Updating..")
            
                # write device_id as active one in json
                active_device_Dict = [{'device_id':add_device_id}]
                jsString = json.dumps(active_device_Dict) # convert python dic to JSON string
                jsFile = open(active_device_filename, "w")
                jsFile.write(jsString)
                jsFile.close() 
                print("Added device set as active device")

            
            # add new devices in JSON file
                
            add_device_dict = {'device_id':add_device_id, 'device_name':add_device_name}

            # 1. Read file contents
            with open(added_devices_filename, "r") as file:
                read_data = json.load(file)
            # 2. Update json object
            read_data.append(add_device_dict)
            # 3. Write json file
            with open(added_devices_filename, "w") as file:
                json.dump(read_data, file) 
            print("Device list updated!")
    #---------------------#       

    return render_template("intel-irris-device-manager.html", read_devices=read_devices, length=length)

#---------------------#

@app.route("/intel-irris-sensor-config", methods = ['POST', 'GET'])
def intel_irris_sensor_config():
    no_active = True
    # check if an active device is set
    if (os.path.getsize(active_device_filename) == 0): # no device added to Intel-Irris
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
        print("Active device_id: %s"%deviceID)

        #---------------------#
        #-- Manage notifying user to add new config --#
        current_config_file = open(sensor_config_filename, 'r')
        current_config = json.loads(current_config_file.read())

        if (len(current_config['sensors']) == 0): # check if sensor config list empty
            print("No sensor configurations made!")
            no_sensor_config = True
        else:
            no_sensor_config = False

        #---------------------#
        #-- GET sensor data of the device --#
        #url = "https://api.waziup.io/api/v2/devices/%s"%deviceID
        url = "http://waziup.wazigate-edge/devices/%s"%deviceID 
        headers = {
            'accept': 'application/json',
            }
        response = requests.get(url, headers=headers)
        sensors_data = response.json()

        #print(data) # uncomment to see the JSON data
                
        # obtain values for each sensor
        sensor_len = len(sensors_data['sensors'])

        for x in range(0, sensor_len):
            Id = sensors_data['sensors'][x]['id']
            # print("Sensor id: %s"%Id)

        #---------------------#
        #-- Get form data and add to json --#
        if request.method == 'POST': # get selected device name
            sensor_id = request.form.get('sensor_id')
            sensor_type = request.form.get('sensor_type')
            sensor_age = request.form.get('sensor_age')
            region = request.form.get('region')
            soil_type = request.form.get('soil_type')
            irrigation_type = request.form.get('irrigation_type')
            crop = request.form.get('crop')
            global_soil_salinity = request.form.get('soil_salinity')
            global_soil_bulk_density = request.form.get('soil_bulk_density')

            # Get last value of selected sensor id
            for i in range (0, sensor_len):
                if (sensors_data['sensors'][i]['id'] == sensor_id ):
                    last_value = sensors_data['sensors'][i]['value']['value']       

            print("Sensor ID : %s"%sensor_id)
            print("Sensor Type : %s"%sensor_type)
            print("Sensor  Age : %s"%sensor_age)
            print("Region : %s"%region)
            print("Soil Type : %s"%soil_type)
            print("Irrigation Type : %s"%irrigation_type)
            print("Crop : %s"%crop)
            print("Soil Salinity : %s"%global_soil_salinity)
            print("Soil Bulk Density : %s"%global_soil_bulk_density)
            print("Last Value : %s"%last_value)

            #-- Check for Null values --#
            if (region == "hide"):
                region = "undefined"
            if (soil_type == "hide"):
                soil_type = "undefined"
            if (irrigation_type == "None" ):
                irrigation_type = "undefined"
            if (crop == "hide"):
                crop = "undefined"
            if (global_soil_salinity == "" or global_soil_salinity == int("-1") ):
                global_soil_salinity = "disabled" # means disabled
            else:
                global_soil_salinity = int(global_soil_salinity)
            if (global_soil_bulk_density == "" or global_soil_bulk_density == int("-1")):
                global_soil_bulk_density = "disabled"# means disabled
            else:
                global_soil_bulk_density = int(global_soil_bulk_density)  

            #---------------------#          
            #-- add new config to the sensor-config.json --#

            # add_globals = {"global_soil_salinity":global_soil_salinity, "global_soil_bulk_density":global_soil_bulk_density, "sensors":[]}
            add_sensors = {"value":{ "sensor_type": sensor_type, "sensor_age": sensor_age, "region": region, "soil_type": soil_type, "irrigation_type": irrigation_type, "crop": crop, "last_value": last_value}, "device_id": deviceID, "sensor_id":sensor_id}
            # read sensors values
            with open(sensor_config_filename, "r") as file:
                read_sensors = json.load(file)['sensors']
                print("read_sensors : %s"%read_sensors)   

            #---------------------#   
            #-- check if selected sensor id has an existing configuration and update it --#

            updated = False
            lenght_read_sensors = len(read_sensors)
            for x in range(0, lenght_read_sensors):
                if (read_sensors[x]['sensor_id'] == sensor_id):
                    read_sensors[x] = add_sensors

                    update_config = {"global_soil_salinity":global_soil_salinity, "global_soil_bulk_density":global_soil_bulk_density, "sensors":read_sensors}
                    
                    # update with the sensor config 
                    jsString = json.dumps(update_config)
                    jsFile = open(sensor_config_filename, "w")
                    jsFile.write(jsString)
                    jsFile.close() 

                    updated = True
            
            if (updated == False):
                read_sensors.append(add_sensors)

                update_config = {"global_soil_salinity":global_soil_salinity, "global_soil_bulk_density":global_soil_bulk_density, "sensors":read_sensors}

                # update config file with new values
                jsString = json.dumps(update_config)
                jsFile = open(sensor_config_filename, "w")
                jsFile.write(jsString)
                jsFile.close()
            #---------------------#   

        #---------------------#
    if (no_active):
        no_device = "No Devices added to Intel-Irris. Go to the Device Manager to add one."
        return render_template("intel-irris-sensor-config.html", no_active=no_active, no_device=no_device, no_sensor_config=no_sensor_config)
    else:
        return render_template("intel-irris-sensor-config.html", deviceID=deviceID,  no_sensor_config=no_sensor_config, sensors_data=sensors_data, sensor_len=sensor_len, x=x, Id=Id)

#---------------------#
@app.route("/intel-irris-sensor-configs", methods = ['POST', 'GET'])
def intel_irris_sensor_configs():

    if request.method == 'POST': 
        selected_sensor_id = request.form.get('selected_sensor_id')

    print("selected_sensor_id : %s"%selected_sensor_id)

    #-- open sensor config file and get data of the selected sensor id --#
    with open(sensor_config_filename, "r") as file:
        read_globals  = json.load(file)
        # read_sensors = json.load(file)['sensors']
    
    read_sensors = read_globals['sensors']

    print("read globals : %s"%read_globals)
    if (len(read_sensors) == 0):
        selected_found = False
    else:
        for x in range(0, len(read_sensors)):
            if (read_sensors[x]['sensor_id'] == selected_sensor_id): # if selected sensor id is in sensors list
                selected_found = True
                # get each field data
                sensor_id = selected_sensor_id
                sensor_type = read_sensors[x]['value']['sensor_type']
                sensor_age = read_sensors[x]['value']['sensor_age']
                region = read_sensors[x]['value']['region']
                soil_type = read_sensors[x]['value']['soil_type']
                irrigation_type = read_sensors[x]['value']['irrigation_type']
                crop = read_sensors[x]['value']['crop']
                last_value = read_sensors[x]['value']['last_value']

                print("Sensor ID : %s"%sensor_id)
                print("Sensor Type : %s"%sensor_type)
                print("Sensor  Age : %s"%sensor_age)
                print("Region : %s"%region)
                print("Soil Type : %s"%soil_type)
                print("Irrigation Type : %s"%irrigation_type)
                print("Crop : %s"%crop)
                print("Last Value : %s"%last_value)

                # read global values
            
                global_soil_salinity = read_globals['global_soil_salinity']
                global_soil_bulk_density = read_globals['global_soil_bulk_density']
                print("Soil Salinity (global) : %s"%global_soil_salinity)
                print("Soil Bulk Density (global) : %s"%global_soil_bulk_density)

            else:
                selected_found = False


    if (selected_found):
        return render_template("intel-irris-sensor-configs.html", selected_found=selected_found, sensor_id=sensor_id, sensor_type=sensor_type, sensor_age=sensor_age, region=region, soil_type=soil_type, irrigation_type=irrigation_type, crop=crop, last_value=last_value ,global_soil_salinity=global_soil_salinity, global_soil_bulk_density=global_soil_bulk_density)
    else:
        return render_template("intel-irris-sensor-configs.html", selected_found=selected_found)
#---------------------#

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    #app.run(host='unix:///app/intel-irris-waziapp/proxy.sock',use_reloader=False,debug=True)