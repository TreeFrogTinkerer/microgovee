import socket, json, pprint

devicesfound=[]

# Ports and Multicase IP Govee Lights UDP uses
LISTEN_PORT = 4002
DEST_IP = "239.255.255.250"
DEST_PORT = 4001

# Setup Listening Socket
recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(("0.0.0.0", LISTEN_PORT)) # Listen on all interfaces

# Setup Sending Socket (No bind needed for client-side)
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Serialize dict to JSON string
data = {"msg":{"cmd":"scan","data":{"account_topic":"reserve"}}}
json_data = json.dumps(data)

# Convert string to bytes
message = json_data.encode('utf-8')

# Send multicase message to request Govee Devices identify themselves
send_sock.sendto(message, (DEST_IP, DEST_PORT))

recv_sock.settimeout(5.0)  # 5-second timeout

print("Scanning for Govee Devices for 5 seconds...")

# This listens for resposes from the Govee devices for 5 seconds. When it receives a message it parses it into a matrix
try:
    while True:
        dataread, addr = recv_sock.recvfrom(1024)
        datadict = json.loads(dataread)
        gvip = datadict["msg"]["data"]["ip"]
        sku = datadict["msg"]["data"]["sku"]
        gvdevice = datadict["msg"]["data"]["device"]
        devicesfound.append([gvip,sku,gvdevice])
except socket.timeout:
    print("Scanning Complete! (5 seconds elapsed)")
finally:
    recv_sock.close()

# Initialize and overwrite previous outputs
with open("./config/founddevices.txt", "w") as f:
    f.write("Detected Govee Devices...\n")

# Go through the matrix and output the almost JSON to the text file for each device found
count=1
for located in devicesfound:
    with open("./config/founddevices.txt", "a") as f:
        f.write("----- New Item ----\n")
        f.write(f"\"id\":{count},\n")
        f.write(f"\"ip\":\"{located[0]}\",\n")
        f.write(f"\"sku\":\"{located[1]}\",\n")
        f.write(f"\"goveeid\":\"{located[2]}\",\n")
        f.write(f"\"name\":\"\"\n")

    count=count+1
