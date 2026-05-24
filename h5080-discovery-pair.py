#!python3
import asyncio
import logging
from bleak import BleakScanner, BleakClient
import time
from H5080utils import find_device, SEND_CHARACTERISTIC_UUID, RECV_CHARACTERISTIC_UUID
import subprocess
import csv


founddevices = []
paireddevice = []
alreadydevices = []
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)-15s %(levelname)s: %(message)s",
    )
logger = logging.getLogger(__name__)

async def main():
    stop_event = asyncio.Event()

    def callback(device, adv):
        if adv.local_name is None:
            return 

        logger.debug("------")
        logger.debug(device)
        logger.debug(adv.service_uuids)
        logger.debug(adv.manufacturer_data)

        if "H5080" in adv.local_name:
            for mfr_id, mfr_data in adv.manufacturer_data.items():
                is_on = mfr_data[-1] == 0x01
                state_name = "On" if is_on else "Off"
                check = [adv.local_name , device.address]
                if check in founddevices:
                    logger.info(f"Detected Device")
                else:
                    founddevices.append([adv.local_name, device.address])
                    logger.info(f"Undetected Device: {adv.local_name}: state={state_name} (address={device.address}, mfr_data={mfr_data.hex()}) ")

    async with BleakScanner(callback) as scanner:
        await asyncio.sleep(5)
        stop_event.set()
        await stop_event.wait() 

asyncio.run(main())

MSG_GET_AUTH_KEY = "aab100000000000000000000000000000000001b"

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)-15s %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main2(DEVICE_NAME_2):
  logger.info(f"Searching for device {DEVICE_NAME_2}")
  device, _ = await find_device(DEVICE_NAME_2)
  if device is None:
    logger.error(f"Could not find a device!")
    return

  logger.info(f"Connecting...")

  async with BleakClient(device.address) as client:
    logger.info(f"Connected to {client.address}")
    logger.info("Starting pairing process...")

    stop_event = asyncio.Event()

    async def recv_handler(charact, msg):
      if len(msg) != 20:
        return 

      # Check for the response type and subtype
      if msg[0] == 0xAA and msg[1] == 0xB1:
        auth_key = extract_auth_key(msg)
        if auth_key is not None:
          logger.info(f"Retrieved authentication key: {auth_key.hex()}")
          print(f"{auth_key.hex()}")
          paireddevice.append([auth_key.hex()])
          stop_event.set()
        else:          
          logger.debug(f"Invalid auth key message: ({msg.hex()})")
          logger.info(f"Press the physical button on the device!")
          time.sleep(0.2)
          await send_get_auth_key(client)

    await client.start_notify(RECV_CHARACTERISTIC_UUID, recv_handler)
    await send_get_auth_key(client)
    await stop_event.wait()
    await client.stop_notify(RECV_CHARACTERISTIC_UUID)


def extract_auth_key(msg):
  # If first byte in payload is 0x00, it means the key is not good
  if msg[2] != 0x01:
    return None
  key = msg[3:-1]
  return key

async def send_get_auth_key(client):
  ba = bytearray.fromhex(MSG_GET_AUTH_KEY)
  await client.write_gatt_char(SEND_CHARACTERISTIC_UUID, ba)

# # #

with open('./config/H5080DeviceCodes.csv', mode='r', newline='\n') as file:
    reader = csv.reader(file)
    for row in reader:
        alreadydevices.append(f"{row[0]}")

for device2pair in founddevices:
    if device2pair[0] not in alreadydevices:
        print("Value NOT exists!")
        paireddevice=[]
        asyncio.run(main2(device2pair[0]))

        with open("./config/H5080DeviceCodes.csv", "a") as file:
            file.write(f"{device2pair[0]},{device2pair[1]},{paireddevice[0][0]}\n")

count=1
with open('./config/H5080DeviceCodes.csv', mode='r', newline='\n') as file:
    reader = csv.reader(file)
    for device in reader:
        with open("./config/H5080Devices.txt", "w") as f:
            f.write("----- New Item ----\n")
            f.write(f"\"id\":{count},\n")
            f.write(f"\"sku\":\"H5080\",\n")
            f.write(f"\"goveename\":\"{device[0]}\",\n")            
            f.write(f"\"goveeid\":\"{device[1]}\",\n")
            f.write(f"\"btpaircode\":\"{device[2]}\",\n")      
            f.write(f"\"name\":\"\"\n")
        count = count + 1



