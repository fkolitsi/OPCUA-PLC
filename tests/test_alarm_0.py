
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
    # Set initial conditions (example: tank filling, heating off) ------+-------
    await plc.set_object_value("DQ0", True)  # Tank is filling
    await plc.set_object_value("DQ2", False)  # Liquid heating is off
    
    # Yield fixture
    yield plc
    # Cleanup conditions (example: stop tank filling, turn off heating) ------+-------
    await plc.set_object_value("DQ0", False)
    await plc.set_object_value("DQ2", False)
  
    # Disconnect
    await plc.disconnect()

# # Trigger overfilling condition
# @pytest.mark.asyncio
# async def test_fillingheating_overfilling(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == True # Tank was filling

#     await plc.set_object_value("DI8", True) # Overfilling sensor active
#     await asyncio.sleep(1) # Waiting for reactions

#     assert await plc.get_object_value("DQ0") == False # Tank stopped filling
#     assert await plc.get_alarm_status("A0") == True # Alarm is triggered

# Trigger overfilling condition
@pytest.mark.asyncio
async def test_fillingheating_overfilling(plc: PLCClient):
    tank_filling_before = await plc.get_object_value("DQ0")
    print(f"Tank filling before: {tank_filling_before}")
    assert tank_filling_before == True  # Tank was filling

    await plc.set_object_value("DI8", True)  # Overfilling sensor active
    await asyncio.sleep(1)  # Waiting for reactions

    tank_filling_after = await plc.get_object_value("DQ0")
    alarm_status = await plc.get_alarm_status("A0")

    print(f"Tank filling after: {tank_filling_after}")
    print(f"Alarm A0 status: {alarm_status}")

    assert tank_filling_after == False  # Tank stopped filling
    assert alarm_status == True  # Alarm is triggered
