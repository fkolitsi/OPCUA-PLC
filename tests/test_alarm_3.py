import asyncio
import pytest
import pytest_asyncio

from src.plc_client import PLCClient

SERVER_URL = "opc.tcp://localhost:7000/freeopcua/server/"
CLIENT_TIMEOUT = 5  # seconds

@pytest_asyncio.fixture()
async def plc() -> PLCClient:
    """ Instance of the OPC UA client to communicate with the simulator """
    plc = PLCClient(url=SERVER_URL, timeout=CLIENT_TIMEOUT)
    await plc.init()
    # Set initial conditions ------+-------
    await plc.set_object_value("DQ2", True)   # Start Heating System

    # Yield fixture
    yield plc
    # Cleanup conditions ------+-------
    await plc.set_object_value("DQ2", False)  # Stop Heating System
    await plc.disconnect()

# @pytest.mark.asyncio
# async def test_low_temperature_alarm(plc: PLCClient):
#     # Heating loop until temperature drops below 10 degrees
#     while True:
#         # Simulate updating inputs from server (introducing a delay)
#         await asyncio.sleep(0.1)

#         # Check if the low-temperature alarm (A3) is triggered
#         if await plc.get_object_value("AI0") < 10.0:
#             break

#     # Stop heating once temperature drops below 10 degrees
#     await plc.set_object_value("DQ2", False)  # Stop Heating System

#     # Check if the low-temperature alarm (A3) is triggered
#     assert await plc.get_alarm_status("A3") == True

# Low temperature alarm test
@pytest.mark.asyncio
async def test_low_temperature_alarm(plc: PLCClient):
    target_temperature = 10.0

    # Heating loop until temperature drops below the target temperature
    current_temperature = await plc.get_object_value("AI0")
    print(f"Current temperature before heating: {current_temperature}")

    while current_temperature >= target_temperature:
        # Simulate updating inputs from server (introducing a smaller delay)
        await asyncio.sleep(0.1)

        # Decrease the temperature (simulating cooling)
        current_temperature -= 1.0

    # Stop heating once temperature drops below the target temperature
    await plc.set_object_value("DQ2", False)  # Stop Heating System

    final_temperature = await plc.get_object_value("AI0")
    alarm_status = await plc.get_alarm_status("A3")

    print(f"Final temperature after cooling: {final_temperature}")
    print(f"Alarm A3 status: {alarm_status}")

    # Check if the low-temperature alarm (A3) is triggered
    assert alarm_status == True
