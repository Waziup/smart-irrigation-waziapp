Running IIWA on your host computer with WaziEdge component
====

Start by looking at this [presentation of IIWA](https://docs.google.com/viewer?url=https://github.com/CongducPham/PRIMA-Intel-IrriS/raw/main/Tutorials/Intel-Irris-IIWA.pdf).

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

Then,
	
	> git clone https://github.com/Waziup/wazigate-edge.git
	> cd wazigate-edge
	
For the moment it is still necessary to add the specific file for MacOS computer:

	> cd tools
	> cp host_linux host_darwin
	> cd ..
	
Then,
	
	> go build .

Adding test devices to WaziEdge and configuring IIWA's configuration files
---

	> cd intel-irris-waziapp-local
	> cd build-local/scripts
	> ./intel-irris-auto-config.sh
	
This will create the INTEL-IRRIS starter-kit default configuration which consist in a capacitive device (SOIL-AREA-1) and a tensiometer device (SOIL-AREA-2). These 2 devices are automatically added into the IIWA's configuration files. See [description of INTEL-IRRIS starter-kit default configuration](https://github.com/CongducPham/PRIMA-Intel-IrriS) for more detail.

Note that `intel-irris-auto-config.sh` use `sed` so the current code uses `sed -i .bak` for in-place replacement on MacOS computer.
			
To run the IIWA local instance
---	

In one terminal window:

	> mongod --config /usr/local/etc/mongod.conf &
	> cd wazigate-edge
	> sudo ./wazigate-edge

In another terminal:
	
	> cd intel-irris-waziapp-local
	> . iiwa/bin/activate
	> python3 app.py
	
Then open http://127.0.0.1:5050/ on your host computer's web browser.	

You can push in real-time data to these devices as follows, in another terminal window:

	> cd intel-irris-waziapp-local
	> cd build-local/scripts
	> ./push_test_values.sh 170 15
	
170 is for the capacitive device (SOIL-AREA-1) and 15 is for the tensiometer device (SOIL-AREA-2).

You can alternatively use:

	> ./push_sensor_test_value.sh 63bfeddd6e45da24473eca6e temperatureSensor_0 170
	> ./push_sensor_test_value.sh 63bfeddd6e45da24473eca72 temperatureSensor_0 15
	
assuming your capacitive device id is `63bfeddd6e45da24473eca6e` and your tensiometer device id is `63bfeddd6e45da24473eca72`.

It should be possible to change and modify IIWA's source code in real-time during development phase.

After testing:

	> deactivate iiwa

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

Get Wazi-Edge source files,

	> git clone https://github.com/Waziup/wazigate-edge.git
	> cd wazigate-edge

Compile the source and build the wazigate-edge executable,

	> go build .

Adding test devices to WaziEdge and configuring IIWA's configuration files
---
Before running the scripts below, ensure that Wazi-Edge and MongoDB servers are running. This procedure is described below.

	> cd intel-irris-waziapp-local
	> cd build-local\scripts
	> .\intel-irris-auto-config.sh

This will create the INTEL-IRRIS starter-kit default configuration which consist in a capacitive device (SOIL-AREA-1) and a tensiometer device (SOIL-AREA-2). These 2 devices are automatically added into the IIWA's configuration files. See [description of INTEL-IRRIS starter-kit default configuration](https://github.com/CongducPham/PRIMA-Intel-IrriS) for more detail.

You can push in real-time data to these devices as follows, in another terminal window:

	> cd intel-irris-waziapp-local
	> cd build-local/scripts
	> .\push_test_values.sh 170 15

170 is for the capacitive device (SOIL-AREA-1) and 15 is for the tensiometer device (SOIL-AREA-2).

You can alternatively use:

	> .\push_sensor_test_value.sh 63bfeddd6e45da24473eca6e temperatureSensor_0 170
	> .\push_sensor_test_value.sh 63bfeddd6e45da24473eca72 temperatureSensor_0 15
	
assuming your capacitive device id is `63bfeddd6e45da24473eca6e` and your tensiometer device id is `63bfeddd6e45da24473eca72`.

It should be possible to change and modify IIWA's source code in real-time during development phase.

After testing:

	> deactivate iiwa

To run the IIWA local instance
---	
First start MongoDB on the host computer. On Windows, MongoDB files are by default installed in the directory `C:\Program Files\MongoDB\Server\5.0\bin` . Here `5.0` is the version you have installed. From this directory we need to run the `mogod` application.

Next start the Wazi-Edge server,

	> cd wazigate-edge
	> .\wazigate-edge.exe

In another command line (CMD) window, start the IIWA application,

	> cd intel-irris-waziapp-local
	> .\iiwa\Scripts\activate
	> python3 app.py

Then open http://127.0.0.1:5000/ on your host computer's web browser.