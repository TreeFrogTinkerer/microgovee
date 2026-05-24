from flask import Flask, jsonify, request
import subprocess, socket, json, time,asyncio, time
import H5080

# Import IPs and shortnames for UDP Devices

with open('./config/goveedevices.json', 'r') as file:
    devicedata = json.load(file)


# Function that sends and receives Govee UDP data. After it sends data it then requests the current state of the devices and returns that
def govee_lan(devicename, data):

	for y in devicedata["devices"]:
        	if y["name"] == devicename:
                	DEST_IP = y["ip"]
                	break

	if 'DEST_IP' not in locals():
		return '{"error":"Device name is incorrect"}'
	else:

		# Hard coded ports in Govee Lights
		LISTEN_PORT = 4002
		DEST_PORT = 4003

		# Setup Listening Socket
		recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		recv_sock.bind(("0.0.0.0", LISTEN_PORT)) # Listen on all interfaces

		# Setup Sending Socket (No bind needed for client-side)
		send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Serialize dict to JSON string
		json_data = json.dumps(data)

		# Convert string to bytes
		message = json_data.encode('utf-8')

		# Send the message
		send_sock.sendto(message, (DEST_IP, DEST_PORT))

		# Wait so status reflects the change
		time.sleep(0.25)

		# Check status
		data2 = {"msg":{"cmd":"devStatus","data":{}}}

		# Serialize dict to JSON string
		json_data2 = json.dumps(data2)

        	# Convert string to bytes
		message2 = json_data2.encode('utf-8')

		# Send the message
		send_sock.sendto(message2, (DEST_IP, DEST_PORT))

		# Receive the response
		data3, addr = recv_sock.recvfrom(1024)

		# Return the current status
		return data3

def govee_bt_5080(usernamed, action):
    for y in devicedata["devices"]:
        if y["name"] == usernamed:
            device_name = y["goveename"]
            pairing_code = y["btpaircode"]
            break
        
    if 'device_name' not in locals():
        return '{"error":"Device name is incorrect"}'
    else:
        if action == "status":
            status=asyncio.run(H5080.status(device_name))
            if status == "On":
                return "{\"status\":\"on\"}"
            elif status == "Off":
                return "{\"status\":\"off\"}"
            else:
                return "{\"status\":\"unknown-status\"}"
        elif action == "toggle":
            asyncio.run(H5080.main_toggle(device_name,pairing_code))
            time.sleep(0.5)
            status=asyncio.run(H5080.status(device_name))
            if status == "On":
                return "{\"status\":\"on\"}"
            elif status == "Off":
                return "{\"status\":\"off\"}"
            else:
                return "{\"status\":\"unknown-status\"}"
        else:
            return '{"error":"Invalid action for ble-power family"}'

    
# This section generates the api endpoint and the commands it accepts. And what it returns.
app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def handle_json():
    data = request.get_json()  # Captures JSON body
    # These parse the attributes from the sent JSON into variables
    family = data.get('family')
    action = data.get('action')
    colortemp = data.get('colortemp')
    brightness = data.get('brightness')
    red = data.get('red')
    green = data.get('green')
    blue = data.get('blue')
    power = data.get('power')
    deviceid = data.get('devicename')

    # The core where all the attribute variables are matched to their actions.  
    # Mostly involves matching cases, setting the JSON UDP commands/attributes, and sending them to the function above for the actual communication
    match family:
        case "light":
            match action:
                case "devstatus":
                    command = {"msg":{"cmd":"devStatus","data":{}}}
                    return govee_lan(deviceid,command)
                case "set-brightness":
                        if isinstance(brightness, int):
                            if 0 <= brightness <= 100:
                                command = {"msg":{"cmd":"brightness","data":{"value":brightness}}}
                                return govee_lan(deviceid , command)
                            else:
                                return '{"error":"Requested brightness level is out of bounds (0-100)"}'
                        else:
                            return '{"error":"Requested brightness was not sent as an integer [remove parantheses]"}'
                case "set-colortemp":
                        if isinstance(colortemp, int):
                            if 2000 <= colortemp <= 7200:
                                command = {"msg":{"cmd":"colorwc","data":{"colorTemInKelvin":colortemp}}}
                                return govee_lan(deviceid , command)
                            else:
                                return '{"error":"Requested color temperature is out of bounds (2000-7200)"}'
                        else:
                            return '{"error":"Requested color temperature was not sent as a bare integer [remove parantheses and/or k]"}'
                case "set-color":

                        if isinstance(red, int) and isinstance(green, int) and isinstance(blue,int):
                            if 0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255:
                                command = {"msg":{"cmd":"colorwc","data":{"color":{"r":red,"g":green,"b":blue}}}}
                                return govee_lan(deviceid , command)
                            else:
                                return '{"error":"At least one color (r,g,b) is out of bounds (0-255)"}'
                        else:
                            return '{"error":"Requested color values one was not sent as a bare integer [remove parantheses]"}'
                case "set-power":
                    match power:
                        case "off":
                            command = {"msg":{"cmd":"turn","data":{"value":0}}}
                            return govee_lan(deviceid , command)
                        case "on":
                            command = {"msg":{"cmd":"turn","data":{"value":1}}}
                            return govee_lan(deviceid , command)
                        case _:
                            return  '{"error":"Incorrect lighting power attribute"}'
                case _:
                    return '{"error":"Invalid action for light family"}'




        case "ble-power":
            match action:
                case "devstatus":
                    return govee_bt_5080(deviceid, "status")
                case "toggle":
                    return govee_bt_5080(deviceid, "toggle")
                case _:
                    return '{"error":"Invalid action for ble-power family"}'
            #return '{"Power outlets are not supprted at this time"}'                  


        case "ble-temphumidity":
            return '{"Humidity/Temperature senors are not supported at this time"}'
        case _:
            return '{"There are no commands associated with that family. Check your family and send again."}'


# Starts the server if run with a gunicorn front end
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

