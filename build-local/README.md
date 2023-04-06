Running IIWA on your host computer with WaziEdge component
====

Quick presentation of IIWA
---

Start by looking at this [presentation of IIWA](https://docs.google.com/viewer?url=https://github.com/CongducPham/PRIMA-Intel-IrriS/raw/main/Tutorials/Intel-Irris-IIWA.pdf).

IIWA converts the soil humidity sensor value into a water index between 0 and 5. For capacitive sensor, it takes into account the soil type to determine the maximum dry value. The default configuration sets soil type to `silty` with a maximum dry value set to 500. 

Therefore, for a capacitive sensor, the following mapping is currently implemented:

- 0-83 -> water index 0: very dry
- 84-166 -> water index 1: dry
- 167-249 -> water index 2: dry
- 250-333 -> water index 3: wet
- 334-416 -> water index 4: wet
- above 416 -> water index 5: saturated

For a tensiometer sensor, IIWA currently implements the basic Irrometer [irrigation recommendations](https://www.irrometer.com/basics.html#using).

- 0-10 Centibars = Saturated soil -> water index 5: saturated
- 10-30 Centibars = Soil is adequately wet -> water index 4: wet
- 30-60 Centibars = Usual range for irrigation (most soils) -> water index 2: dry
- 60-100 Centibars = Usual range for irrigation in heavy clay -> water index 1: dry
- 100-200 Centibars = Soil is becoming dangerously dry -> water index 0: very dry

You can have all these information summurized in the starter-kit [soil humidity indication flyer](https://intel-irris.eu/wp-content/uploads/2023/02/Intel-Irris-soil-humidity-indication-fr.pdf). More parameters and more intelligence will be added in IIWA during the project.

Installation on your host computer
---

**The installation on your host computer is only for the development phase of the IIWA application, without the whole INTEL-IRRIS WaziGate framework which normally runs on a RaspberryPi. Therefore, only the mongodb database and the WaziEdge REST API will be available to IIWA for creating/modifying device data.**

There are installation instructions for MacOS (that should also work for Linux) and Windows computers. All instructions are duplicated and Windows users can jump directly to the Windows section.

MacOS instructions (and Linux?)
====

Get IIWA
---
	
	> git clone --branch intelirris https://github.com/Waziup/smart-irrigation-waziapp.git intel-irris-waziapp-local
	> cd intel-irris-waziapp-local
	> sed -i .bak 's/port=5000/port=5050/g' app.py

On Mac computers, port 5000 is used by AirReceiver. Note that `sed` on MacOS needs the `sed -i .bak` for in-place replacement. `sed` on Linux distribution does not need `.bak`.
	
For installing Flask and dependencies, using virtual environment
---
	> cd intel-irris-waziapp-local
	> python3 -m venv iiwa
	> . iiwa/bin/activate
	> pip3 install -r requirements.txt 
	> deactivate iiwa

Install WaziEdge and its dependencies. Only MongoDB up to v5.0 is supported.
---
	> brew tap mongodb/brew
	> brew install mongodb-community@5.0
	
	> sudo chown -R $(whoami) $(brew --prefix)
	> brew link --overwrite node
	
Install Go language dev tool from https://go.dev/dl/. Be careful to choose either Intel chip or Apple chip.

Then, get WaziEdge source files:
	
	> git clone https://github.com/Waziup/wazigate-edge.git
	> cd wazigate-edge
	
For the moment it is still necessary to add the specific file for MacOS computer:

	> cd tools
	> cp host_linux host_darwin
	> cd ..
	
Compile the source and build the wazigate-edge executable:
	
	> go build .
			
Run the IIWA local instance
---	

We will start MongoDB and wazigate-edge. In one terminal window:

	> mongod --config /usr/local/etc/mongod.conf &
	> cd wazigate-edge
	> sudo ./wazigate-edge

In another terminal, start the IIWA application:
	
	> cd intel-irris-waziapp-local
	> . iiwa/bin/activate
	> python3 app.py
	
Then open http://127.0.0.1:5050/ on your host computer's web browser.	

Adding default test devices to WaziEdge and configuring IIWA's configuration files
---

Before running the scripts below, ensure that WaziEdge and MongoDB servers are running. Then you have to add the starter-kit default test devices. In a terminal window:

	> cd intel-irris-waziapp-local
	> cd build-local/scripts
	> ./intel-irris-auto-config.sh
	
This will create the INTEL-IRRIS starter-kit default configuration which consist in a capacitive device (SOIL-AREA-1) and a tensiometer device (SOIL-AREA-2). These 2 devices are automatically added into the IIWA's configuration files. See [description of INTEL-IRRIS starter-kit default configuration](https://github.com/CongducPham/PRIMA-Intel-IrriS#default-configuration-for-the-gateway) for more detail although .

**Note that it is mandatory to run this `intel-irris-auto-config.sh` script**

You can then refresh http://127.0.0.1:5050/ to see that the 2 devices have been added to IIWA. Then you can quickly push in real-time some sensor data to the default starter-kit devices as follows, in another terminal window:

	> cd intel-irris-waziapp-local
	> cd build-local/scripts
	> ./push_starterkit_test_values.sh 170 15
	
170 is for the capacitive device (SOIL-AREA-1) and 15 is for the tensiometer device (SOIL-AREA-2). 

Then, it is now possible to change and modify IIWA's source code in real-time during development phase on your host computer.

After testing:

	> deactivate iiwa

Adding more devices
---

You can dynamically add more devices for your tests. To add a new capacitive device named `SOIL-AREA-3` with device's address `26011DAB`:

	> cd intel-irris-waziapp-local
	> cd build-local/scripts
	> ./create_new_capacitive.sh 3 AB
	
To add a new tensiometer device named `SOIL-AREA-4` with device's address `26011DB2`:	

	> ./create_new_tensiometer.sh 4 B2
	
**Note that the device's address is actually not really important for IIWA. However, we still keep it as these scripts use real scripts to add real devices	to the INTEL-IRRIS system.**

**What is important is to avoid assigning same device name, e.g. several `SOIL-AREA-1` for instance.**

After the creation of new devices, you can also push new sensor data as follows:

	> ./push_device_test_value.sh 3 170
	
which will push value 170 to device `SOIL-AREA-3`. In our example it is the newly created capacitive device.	

	> ./push_device_test_value.sh 4 15
	
will will push value 15 to device `SOIL-AREA-4`. In our example it is the newly created tensiometer device.	

You can alternatively use the more generic script `push_sensor_test_value.sh`:

	> ./push_sensor_test_value.sh 63bfeddd6e45da24473eca6e temperatureSensor_0 170
	> ./push_sensor_test_value.sh 63bfeddd6e45da24473eca72 temperatureSensor_0 15
	
assuming your capacitive device id is `63bfeddd6e45da24473eca6e` and your tensiometer device id is `63bfeddd6e45da24473eca72`.

Resetting configuration
---

At any time, you can run again the starter-kit configuration script that will delete all devices and create a new initial configuration.

	> cd intel-irris-waziapp-local
	> cd build-local/scripts
	> ./intel-irris-auto-config.sh 

Windows instructions
====

Get IIWA
---

	> git clone --branch intelirris https://github.com/Waziup/smart-irrigation-waziapp.git intel-irris-waziapp-local
	> cd intel-irris-waziapp-local

For installing Flask and dependencies, using virtual environment
---

	> cd intel-irris-waziapp-local
	> python3 -m venv iiwa
	> .\iiwa\Scripts\activate
	> pip3 install -r requirements.txt 
	> deactivate iiwa

Install WaziEdge and its dependencies
---

Download and install [Node.js](https://nodejs.org/en/download/), [Go programming language](https://go.dev/) and [MongoDB](https://www.mongodb.com/try/download/community) (supported upto version 5.0.14 and below).

Then, get WaziEdge source files:

	> git clone https://github.com/Waziup/wazigate-edge.git
	> cd wazigate-edge

Compile the source and build the wazigate-edge executable:

	> go build .
	
Run the IIWA local instance
---	

First start MongoDB on the host computer. On Windows, MongoDB files are by default installed in the directory `C:\Program Files\MongoDB\Server\5.0\bin`. Here `5.0` is the version you have installed. From this directory we need to run the `mongod` application.

Next, start the wazigate-edge server:

	> cd wazigate-edge
	> .\wazigate-edge.exe

In another command line (CMD) window, start the IIWA application:

	> cd intel-irris-waziapp-local
	> .\iiwa\Scripts\activate
	> python3 app.py

Then open http://127.0.0.1:5000/ on your host computer's web browser.	

Adding default test devices to WaziEdge and configuring IIWA's configuration files
---

Before running the scripts below, ensure that Wazi-Edge and MongoDB servers are running. Then you have to add the starter-kit default test devices. In a terminal window:

	> cd intel-irris-waziapp-local
	> cd build-local\scripts
	> .\intel-irris-auto-config.sh

This will create the INTEL-IRRIS starter-kit default configuration which consist in a capacitive device (SOIL-AREA-1) and a tensiometer device (SOIL-AREA-2). These 2 devices are automatically added into the IIWA's configuration files. See [description of INTEL-IRRIS starter-kit default configuration](https://github.com/CongducPham/PRIMA-Intel-IrriS) for more detail.

**Note that it is mandatory to run this `intel-irris-auto-config.sh` script**

You can then refresh http://127.0.0.1:5000/ to see that the 2 devices have been added to IIWA. Then you can quickly push in real-time some sensor data to the default starter-kit devices as follows, in another terminal window:

	> cd intel-irris-waziapp-local
	> cd build-local\scripts
	> .\push_starterkit_test_values.sh 170 15

170 is for the capacitive device (SOIL-AREA-1) and 15 is for the tensiometer device (SOIL-AREA-2).

Then, it is now possible to change and modify IIWA's source code in real-time during development phase on your host computer.

After testing:

	> deactivate iiwa

Adding more devices
---

You can dynamically add more devices for your tests. To add a new capacitive device named `SOIL-AREA-3` with device's address `26011DAB`:

	> cd intel-irris-waziapp-local
	> cd build-local\scripts
	> .\create_new_capacitive.sh 3 AB
	
To add a new tensiometer device named `SOIL-AREA-4` with device's address `26011DB2`:	

	> .\create_new_tensiometer.sh 4 B2
	
**Note that the device's address is actually not really important for IIWA. However, we still keep it as these scripts use real scripts to add real devices	to the INTEL-IRRIS system.**

**What is important is to avoid assigning same device name, e.g. several `SOIL-AREA-1` for instance.**

After the creation of new devices, you can also push new sensor data as follows:

	> .\push_device_test_value.sh 3 170
	
which will push value 170 to device `SOIL-AREA-3`. In our example it is the newly created capacitive device.	

	> .\push_device_test_value.sh 4 15
	
will will push value 15 to device `SOIL-AREA-4`. In our example it is the newly created tensiometer device.	

You can alternatively use the more generic script `push_sensor_test_value.sh`:

	> .\push_sensor_test_value.sh 63bfeddd6e45da24473eca6e temperatureSensor_0 170
	> .\push_sensor_test_value.sh 63bfeddd6e45da24473eca72 temperatureSensor_0 15
	
assuming your capacitive device id is `63bfeddd6e45da24473eca6e` and your tensiometer device id is `63bfeddd6e45da24473eca72`.

Resetting configuration
---

At any time, you can run again the starter-kit configuration script that will delete all devices and create a new initial configuration.

	> cd intel-irris-waziapp-local
	> cd build-local/scripts
	> .\intel-irris-auto-config.sh
	
Enjoy!
C. Pham and S. Githu

