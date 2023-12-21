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
    await plc.set_object_value("DQ3", False)   # Close motor-controlled discharging door

    # Yield fixture
    yield plc
    # Cleanup conditions ------+-------
    await plc.set_object_value("DQ3", False)  # Close motor-controlled discharging door
    await plc.disconnect()


# Discharging door alarm test
@pytest.mark.asyncio
async def test_discharging_door_alarm(plc: PLCClient):
    # Close the discharging door initially
    await plc.set_object_value("DQ3", False)  # Close motor-controlled discharging door
    initial_door_status = await plc.get_object_value("DQ3")
    print(f"Initial discharging door status: {initial_door_status}")

    # Open the discharging door
    await plc.set_object_value("DI9", True)  # Open discharging door
    await asyncio.sleep(1)  # Waiting for reactions

    door_alarm_status = await plc.get_alarm_status("A4")
    print(f"Discharging door alarm status: {door_alarm_status}")

    # Check if the discharging door alarm (A4) is triggered
    assert door_alarm_status == True

    # Close the discharging door
    await plc.set_object_value("DI9", False)  # Close discharging door
    final_door_status = await plc.get_object_value("DQ3")
    print(f"Final discharging door status: {final_door_status}")
