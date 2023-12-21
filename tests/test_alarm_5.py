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
    await plc.set_object_value("DQ3", False)   # Close motor-controlled discharging door

    # Yield fixture
    yield plc
    # Cleanup conditions ------+-------
    await plc.set_object_value("DQ2", False)  # Stop Heating System
    await plc.set_object_value("DQ3", False)  # Close motor-controlled discharging door
    await plc.disconnect()

# @pytest.mark.asyncio
# async def test_emergency_button_alarm(plc: PLCClient):
#     # Press the emergency button (DI3)
#     await plc.set_object_value("DI3", True)  # Simulate pressing the emergency button

#     # Check if the emergency button alarm (A5) is triggered
#     assert await plc.get_alarm_status("A5") == True

#     # Turn off everything and open the discharging gate
#     await plc.set_object_value("DQ2", False)  # Stop Heating System
#     await plc.set_object_value("DQ3", True)   # Open motor-controlled discharging door

#     # Release the emergency button
#     await plc.set_object_value("DI3", False)  # Simulate releasing the emergency button

# Emergency button alarm test
@pytest.mark.asyncio
async def test_emergency_button_alarm(plc: PLCClient):
    # Press the emergency button (DI3)
    await plc.set_object_value("DI3", True)  # Simulate pressing the emergency button
    emergency_button_status = await plc.get_object_value("DI3")
    print(f"Emergency button status: {emergency_button_status}")

    # Check if the emergency button alarm (A5) is triggered
    alarm_status = await plc.get_alarm_status("A5")
    print(f"Emergency button alarm status: {alarm_status}")
    assert alarm_status == True

    # Turn off everything and open the discharging gate
    await plc.set_object_value("DQ2", False)  # Stop Heating System
    await plc.set_object_value("DQ3", True)   # Open motor-controlled discharging door

    # Release the emergency button
    await plc.set_object_value("DI3", False)  # Simulate releasing the emergency button
    emergency_button_status_after_release = await plc.get_object_value("DI3")
    print(f"Emergency button status after release: {emergency_button_status_after_release}")
