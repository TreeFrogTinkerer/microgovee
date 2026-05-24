# MicroGovee - A simple REST API Server wrapper for Govee UDP API

Govee has a UDP based API for a subset of their products. Which work. And are fairly easy to work with.  However, some projects I was using them on didn't have an easy way to listen to UDP but did on a standard REST API. And so this project was born.  The REST API Server wrapper was written to make other integrations just a little easier.

# Features

* Autodetect Govee devices on LAN network that have the LAN network feature enabled
   - Not auto loaded. A companion file allows you to copy them into MicroGovee config file
* Allows custom short names to be associated in json config file 
* Multiple devices can be controlled from the same API end point
* Lightweight -- written in python
* Returns status of device automatically when a change is made
   - Status is also available on its own
* Extensible to other Govee products in the API structure
* Docker container offered

# Supported Devices

- [x] Govee UDP Lights : [See supported devices](https://app-h5.govee.com/user-manual/wlan-guide)
- [x] Govee H5080 Bluetooth Plugs
- [ ] Govee H5075 Thermometer / Humidity Sensor  

# Future Feature Possibilities

While Govee has published the UDP API for their light products other products are Bluetooth only, etc. This API setup has the ability to expand to other Govee devices in addition to the ones supported above. 

# Why not GoveeCloud API?

I prefer local options.  Both for immediate use reasons but also in case a company goes out of business 'remote' features still work.

# Why Not Home Assistant? or OpenHAB? 

Complexity and size.  They are both great products. They excel at what they do. But I'm not interested in 99% of what they do.  I only am really interested in remote switches - for lights and maybe power sockets.  I'm not looking to monitor or graph any attributes or automate any actions besides a control panel knowing if something is on or off so I can make a button appear.  I always prefer simplicity over complexity if it does what I want it to do.  With that being said there is no reason to not use them if you want.  MicroGovee doesn't do anything better in fact it does most things way worse and the thing it does really only surpasses it on size and complexity of install.  Technically, this also allows you to do your own integration so really that is the biggest advantage.  If you are looking to integrate Govee lights / or products into something you are building most likely using something like Home Assistant or openHAB likely will be to large for your project.

# Prerequisites

## Hardware

Wi-Fi enabled device and/or Bluetooth enabled device if using Bluetooth devices

## Manual Installed

Make sure your system has the following packages installed before running the install script:

* python3
* venv - for virtual environment
* git

## Script Installed

* flask
* gunicorn
* bleak (for Bluetooth Devices)

# To Install

Run

```
git clone https://github.com/TreeFrogTinkerer/microgovee.git
cd microgovee
chmod +x install.sh
source ./install.sh
```

# Configuration

Before you can send commands to the API you need to tell the API Server what your Govee devices IP/Bluetooth addresses are.  This information is stored in `./config/goveedevices.json`

By default MicroGovee ships with an empty device list.  
```
{
  "devices":[
    {

    }
  ]
}
```


Look at all those devices! Wow! 

There are 2 ways you can populate this data.  The first is to manually add it in the correct JSON format.  The second is to user the helper script to detect Govee Devices on your network to generate MOSTLY formatted JSON entries.

## Manually Add, Edit, Remove, or Change Govee Devices

> [!IMPORTANT]
> Manually adding is ONLY recommended for UDP Lights as Bluetooth devices need a pairing sequence connect

Run

`nano ./config/goveedevices.json`

to open the config file.

Each device is enclosed in a pair of curly brackets `{` & `}`.

The correct format is as follows:
```
{
  "devices":[
    {
      "id":1,
      "ip":"192.168.1.x",
      "sku":"H1401",
      "goveeid":"SO:ME:MA:C0:ADD:RE:SS:00",
	  "goveename":"BLUETOOTHDEVICESONLY",
      "btpaircode":"BLUETOOTHDEVICESONLY",
      "name":"bedroom"
    },
    {
      "id":2,
      "ip":"192.168.1.y",
      "sku":"H61BA",
      "goveeid":"SO:ME:MA:C0:ADD:RE:SS:01",
	  "goveename":"BLUETOOTHDEVICESONLY",
	  "btpaircode":"BLUETOOTHDEVICESONLY",
      "name":"kitchen"
    },
    {
      "id":3,
      "ip":"192.168.1.z",
      "sku":"H1401",
      "goveeid":"SO:ME:MA:C0:ADD:RE:SS:02",
      "goveename":"BLUETOOTHDEVICESONLY",
      "btpaircode":"BLUETOOTHDEVICESONLY",
	  "name":"bathroom"
    }
  ]
}
```

The following three fields are required for ALL MicroGovee Device use:
1) id - Random Integer of no impact -- This isn't actively used but allows each record to be absolutely accessed if need be ie - good practice
2) name - This is the human notable name for the device. This is used when calling the API to direct commands. MicroGovee uses this field to lookup the IP field before sending the UDP commands

Required for UDP Lights:

3) ip - This is where the API is going to send the UDP commands to. It is recommended that your devices have static or reserved IPs to make this persistent

Required for Govee Bluetooth Devices:

4) goveename - This is the name of the device bluetooth reports/responds to
5) btpaircode - This is the code recieved after pairing Bluetooth devices to the server 

The following two commands are optional. Both are returned by the device's announcements of themselves on the network.  I believe the CloudAPI uses the goveeid (called 'device' in the raw data) to send the commands to. In MicroGovee they are included for completeness and future proofing.
 
6) sku - This is the product model. It is returned by the device during query for devices on the network s
7) goveeid - This is the device 'id' the device itself returns. I believe this to be the MAC address.

And as with JSON formatting REALLY matters.  Make sure between each device you include a "," and no comma after the last item.
```
{
  "devices":[
    {
		DATA
    }, <---- This is the important comma
    {
		DATA2
    }, <---- A second important comma!
    {
		DATA3
    } <---- Important LACK of comma
  ]
}
```
## Helper Script / Semi-Automated

There are separate helper scripts for UDP lights and for H5080 Bluetooth Plugs.  

### UDP Lights

There is a script that will send a multicast UDP packet onto your network and listen for device responses for 5 seconds.  It then parses them and creates the DATA block that goes between the curly brackets. It then writes it to the `./config/founddevices.txt` file. Where you can copy and paste them into the goveedevices.json.

> [!IMPORTANT]
> This isn't a highly configured script so sometimes with multiple devices responding at once it can miss devices.  If this happens run it again or a third time. If it continues to not get all your devices manually configure them as above.

To run:

`python3 udp-detect.py`

Then to open your results:

`nano ./config/udp-founddevices.txt`

This will look something like:

```
Detected Govee Devices...
----- New Item ----
"id":1,
"ip":"192.168.1.x",
"sku":"H61BA",
"goveeid":"SO:ME:MA:C0:ADD:RE:SS:00",
"name":""
----- New Item ----
"id":2,
"ip":"192.168.1.y",
"sku":"H1401",
"goveeid":"SO:ME:MA:C0:ADD:RE:SS:01",
"name":""
----- New Item ----
"id":3,
"ip":"192.168.1.z",
"sku":"H1401",
"goveeid":"SO:ME:MA:C0:ADD:RE:SS:02",
"name":""
```

If the script is successful in IDing devices on your network MOST of the information you need should be in this screen.  The human use name is of course is blank.

To use copy the text between the ---- New Item ---- and the next one (or end of the page) and paste between curly brackets in the configuration file. 

> [!IMPORTANT]
> Don't forget to add { before AND after } your paste! And if you need the all important comma do that too!

Once pasted in add a name between the "s for your device

### H5080 Bluetooth plug

> [!IMPORTANT]
> It is HIGHLY recommended to use the script for Bluetooth devices as you need to pair and get the correct code which this script does

`python3 h5080-discovery-pair.py`

This script...
* Listens for Govee bluetooth devices for 30 seconds
* Then checks if seen devices have been paired before (ie retrieve a pairing code)
* If no code is found it then  tries to pair with the bluetooth plug
   * This entails pressing the button on the plug to finalaize the process
   
This files creates 2 files:

`./config/H5080DeviceCodes.csv` & `./config/H5080Devices.txt`

The H5080DeviceCodes.csv is where pairing codes are stored are appended each run of the Script and not removed

The H5080Devices.txt file is rewritten each time from H5080DeviceCodes.csv devices (So can't store the pairing code with multiple runs)

Then to open your results:

`nano ./config/H5080devices.txt`

This will look something like:

```
Detected Govee Devices...
----- New Item ----
"id":1,
"sku":"H5080",
"goveeid":"SO:ME:MA:C0:ADD:RE:SS:00",
"goveename":"BLUETOOTHDEVICESONLY",
"btpaircode":"BLUETOOTHDEVICESONLY",
"name":""
----- New Item ----
"id":2,
"sku":"H5080",
"goveeid":"SO:ME:MA:C0:ADD:RE:SS:01",
"goveename":"BLUETOOTHDEVICESONLY",
"btpaircode":"BLUETOOTHDEVICESONLY",
"name":""
----- New Item ----
"id":3,
"sku":"H5080",
"goveeid":"SO:ME:MA:C0:ADD:RE:SS:02",
"goveename":"BLUETOOTHDEVICESONLY",
"btpaircode":"BLUETOOTHDEVICESONLY",
"name":""
```

If the script is successful in IDing devices on your network MOST of the information you need should be in this screen.  The human use name is of course is blank.

To use copy the text between the ---- New Item ---- and the next one (or end of the page) and paste between curly brackets in the configuration file. 

> [!IMPORTANT]
> Don't forget to add { before AND after } your paste! And if you need the all important comma do that too!

Once pasted in add a name between the "s for your device

# Running the Server
* By default the server runs on port 5000
  - If you need to change this you can do so in the run-microgovee.sh file
## Manually

In an interactive BASH window simply run:

`source ./run-microgovee.sh`

The source prefix just allows python to enter the virtual python environment MicroGovee was installed in

> [!TIP]
> To change the port MicroGovee runs on. Edit (nano run-microgove.sh) and change the port (5000) in the following line:  "gunicorn --bind 0.0.0.0:5000 microgovee:app"

## As a systemd Service

You first need to edit the supplied microgovee.service file:

```
[Unit]
Description=MicroGovee Service
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=root                                                                                   <-----CHANGE THIS USER
WorkingDirectory=/PATH/TO/YOUR/microgovee                                                   <-----CHANGE THIS PATH
ExecStart=/PATH/TO/YOUR/microgovee/.venv/bin/gunicorn --bind 0.0.0.0:5000 microgovee:app    <-----CHANGE THIS PATH

[Install]
WantedBy=multi-user.target

```

In the microgovee folder run:

`nano microgovee.service`

And update the user line to be the user to run under and update the full path to the microgovee folder you cloned.

For example if you cloned into a home folder for the user "george"

These lines 
```
WorkingDirectory=/PATH/TO/YOUR/microgovee
ExecStart=/PATH/TO/YOUR/microgovee/.venv/bin/gunicorn --bind 0.0.0.0:5000 microgovee:app
```

would become 

```
WorkingDirectory=/home/george/microgovee
ExecStart=/home/george/microgovee/.venv/bin/gunicorn --bind 0.0.0.0:5000 microgovee:app
```

Then simply run:

```
sudo cp microgovee.service /etc/systemd/system
sudo systemctl enable microgovee
sudo systemctl start microgovee
```

This copies the service into the correct folder, sets it to automatically launch at boot, and then starts the service now.

To confirm the service is running correctly run:

`sudo systemctl status microgovee`

> [!TIP]
> To change the port MicroGovee runs on. Change the port (5000) in the following line in microgovee.service BEFORE copying it to /etc/systemd/system:  "ExecStart=/PATH/TO/YOUR/microgovee/.venv/bin/gunicorn --bind 0.0.0.0:5000 microgovee:app"

# Using the API Server

## Endpoint Path
The endpoint for the api is:

`http://YOUR.IP.ADD.RESS:5000/api/data`

> [!NOTE]
> Swap out 5000 for your port if you edited the startup script!

## Commands!

Now let the disco light rave begin!  

The API accepts JSON input and returns JSON output.  All commands return the current status of the device in JSON just as the device UDP devStatus returns.  There is small delay so the returned data reflects the changes you just sent to the device.

The API is broken up into 3 main 'sections'.

1) Family - This is the type of device you want to control. Right now the only one that is supported is lighting but maybe in the future some more will be added
   - Current Option(s): 
       - light
	   - ble-power
2) Action - This is what you want it to DO.
   - Current Options:
       - devStatus - Just returns the device status
	   - set-brightness - Sets the brightness between 1 & 100%
	   - set-colortemp - Sets the color temperature between 2000 and 7200 kelvin
	   - set-color - Sets the RGB color
	   - set-power - Turns the light on or off
3) Action Data - For this one I choose a flat structure for simplicity. The less nested JSON the simplier it is.  This may be a mistake in the future but for now here it is. Each Action has it's own Data to include. The following 

Now let's look at a JSON string for each command. In each example we will use the 'kitchen' light we defined above as our target. As well as all examples will be shown in human readable format. In most cases when sent all the new lines and tabs are removed to create a string that looks like this:

`{"family": "light","action": "devStatus","devicename":"string1"}`

> [!NOTE]
> Atributes ARE case sensitive. They are ALL lowercase.

## Govee UDP Lights
`"family":"light"`

### devStatus

`"action":"devstatus"`

This action has no custom attributes. 

Example:

```
{
    "family": "light",
    "action": "devStatus",
    "devicename":"kitchen"
}
```

### set-brightness

`"action":"set-brightness"`

This action takes one custom attribute:
* brightness - It can be set to any integer percentage between 0 & 100 

Example - This sets the brightness to 75% of maximum:

```
{
    "family": "light",
    "action": "set-brightness",
    "brightness": 75,
    "devicename":"kitchen"
}
```

> [!IMPORTANT]
> Do NOT put the brightness integer inside quotation marks. Note the lack of " around 75 above vs the other attributes like "kitchen"

### set-colortemp

`"action":"set-colortemp"`

This action takes one custom attribute:
* colortemp - It can be set to any integer between 2000 and 7200 noting the color temperature in Kelvin. DO NOT added a "k" at the end
   - 5000 = correct
   - 5000k = incorrect!

Example - This sets the kitchen light to a color temperature of 5500k

```
{
    "family": "light",
    "action": "set-colortemp",
    "colortemp": 5500,
    "devicename":"kitchen"
}
```

> [!IMPORTANT]
> Do NOT put the colortemp integer inside quotation marks. Note the lack of " around 5500 above vs the other attributes like "kitchen"

### set-color

`"action":"set-color"`

This action takes 3 custom mandatory attributes. All values are between 0-255 as for normal RGB color mixing:
* red
* green
* blue

Example - This sets the light to teal

```
{
    "family": "light",
    "action": "set-color",
    "red": 0,
    "green": 128,
    "blue": 128,
    "devicename":"kitchen"
}
```

> [!IMPORTANT]
> Do NOT put the red, green, and blue integers inside quotation marks. Note the lack of " around 128 above vs the other attributes like "kitchen"

### set-power

`"action":"set-power"`

This action takes one custom attribute:
* `power` - Only two states are possible
   - on
   - off

Example - This turns the kitchen light on: 

```
{
    "family": "light",
    "action": "set-power",
    "power" : "on",
    "devicename":"kitchen"
}
```

## H5080 Bluetooth Plugs

`"family":"ble-power"`

### devStatus

`"action":"devstatus"`

This action takes zero custom attributes.

Example - This returns the kitchenplug status:

```
{
    "family": "ble-power",
    "action": "devstatus",
    "devicename": "kitchenplug"
}
```

### toggle

`"action":"toggle"`

This action takes zero custom attributes.

Example - This toggles the kitchenplug:
(If the plug is on it turns off and vice versa) 

```
{
    "family": "ble-power",
    "action": "toggle",
    "devicename": "kitchenplug"
}
```

# Returned Data

## UDP Lights

Each command returns the following JSON formatted information as a pass through from the UDP API

```
{
  "msg":{
    "cmd":"devStatus",
    "data":{
      "onOff":1,
      "brightness":100,
      "color":{
        "r":255,
        "g":0,
        "b":0
      },
      "colorTemInKelvin":7200
    }
  }
}
```

## H5080 Bluetooth Plugs

Each command returns the following JSON formatted information

```
{
    "status": "off"
}
```

Unless you send a bad API call in which case you will get an error in the following JSON format:

```
{
	"error":"....Error details here...."
}
```
	  
	  
	  
# Sources

## Govee UDP API

[Straight from Govee](https://app-h5.govee.com/user-manual/wlan-guide)

## H5080 Bluetooth Plugs

Not only is the protocol but most of the code for H5080 Bluetooth Plugs are from [Govee-Reverse-Engineering Github Project](https://github.com/egold555/Govee-Reverse-Engineering).

I edited and adapted the scripts here to this specific usage but I'd estimate the codebase is about 96% from the source. I wouldn't have been able to do it without the fanstic work done!