#!python3
import asyncio
import logging
import time
from bleak import BleakClient
from H5080utils import find_device, compute_xor, SEND_CHARACTERISTIC_UUID, RECV_CHARACTERISTIC_UUID

## Configuration
#DEVICE_NAME = "ihoment_H5080_6B2B"  # the name of the device we want to pair with
#AUTH_KEY = "330e235a0bd89cdd0000000000000000"  # Obtain this using pair.py

MSG_TURN_ON = "3301ff00000000000000000000000000000000cd"
MSG_TURN_OFF = "3301f000000000000000000000000000000000c2"

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)-15s %(levelname)s: %(message)s",
    )
logger = logging.getLogger(__name__)
# logger.level = logging.DEBU

async def main_toggle(DEVICE_NAME, AUTH_KEY):
  device, adv_data = await find_device(DEVICE_NAME)
  if device is None:
    print("No device found")
    return

  # Read the state of the switch at this moment
  is_on = get_adv_on_state(adv_data)
  if is_on is None:
    print(f"Could not detect the current state")
    return

  # Connect 
  async with BleakClient(device.address) as client:
    logger.info(f"Connected to {client.address}")
    
    # events to control execution flow
    on_auth_ready = asyncio.Event()
    on_set_state_ready = asyncio.Event()

    async def recv_handler(c, data):
      logger.debug(f"RECV {data.hex()}")
      if data[0] == 0x33 and data[1] == 0xB2:
        on_auth_ready.set()
      elif data[0] == 0x33 and data[1] == 0x01:
        on_set_state_ready.set()

    await client.start_notify(RECV_CHARACTERISTIC_UUID, recv_handler)
    
    await authenticate(client, AUTH_KEY)
    await on_auth_ready.wait()

    await set_state(client, not is_on)
    await on_set_state_ready.wait()

    await client.stop_notify(RECV_CHARACTERISTIC_UUID)
    logger.info("Finished")

async def status(DEVICE_NAME):
    device, adv_data = await find_device(DEVICE_NAME)
# Read the state of the switch at this moment
    is_on = get_adv_on_state(adv_data)
    if is_on is True:
        return "On"
    elif is_on is False:
        return "Off"
    #return is_on
    #if is_on is None:
    #  print(f"Could not detect the current state")
      #  return


# Parses the advertisement data for useful information (i.e. the on/off state)
def get_adv_on_state(adv_data):
    for mfr_id, mfr_data in adv_data.manufacturer_data.items():
      # The last byte in the manufacturer data is the state of the switch
      return mfr_data[-1] == 0x01 
    return None


async def authenticate(client, auth_key):
  logger.info("Authenticating")
  # Create the message
  ba = bytearray([0x33, 0xB2]) + bytearray.fromhex(auth_key).ljust(17, b'\0')
  ba.append(compute_xor(ba))  
  logger.debug(f"SEND {ba.hex()}")
  await client.write_gatt_char(SEND_CHARACTERISTIC_UUID, ba)


async def set_state(client, new_state):
  logger.info(f"Updating state to: {new_state}")
  # Send the set on or off command
  ba = bytearray.fromhex(MSG_TURN_ON if new_state else MSG_TURN_OFF)
  logger.debug(f"SEND {ba.hex()}")
  await client.write_gatt_char(SEND_CHARACTERISTIC_UUID, ba)

    

#asyncio.run(main_toggle())
#asyncio.run(status())
