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
    await plc.set_object_value("DQ0", False)  # Tank is not filling initially
    await plc.set_object_value("DQ2", False)  # Liquid heating is off
    await plc.set_object_value("DQ1", True)   # Outlet valve open (discharging)
    
    # Yield fixture
    yield plc
    # Cleanup conditions (example: stop tank discharging) ------+-------
    await plc.set_object_value("DQ0", False)
    await plc.set_object_value("DQ1", False)
    await plc.set_object_value("DQ2", False)  
    # Disconnect
    await plc.disconnect()

# @pytest.mark.asyncio
# async def test_low_tank_level_after_discharging(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == False  # Tank is not filling initially

#     # Simulate discharging (close the outlet valve)
#     await plc.set_object_value("DQ1", False)  # Outlet valve closed
#     await asyncio.sleep(1)  # Waiting for reactions

#     # Set the tank level too low condition
#     await plc.set_object_value("DI5", True)  # Low tank level sensor active
#     await asyncio.sleep(1)  # Waiting for reactions

#     assert await plc.get_object_value("DQ0") == False  # Tank continues to not fill
#     assert await plc.get_alarm_status("A1") == True  # Alarm A1 is triggered

# Simulate low tank level after discharging
@pytest.mark.asyncio
async def test_low_tank_level_after_discharging(plc: PLCClient):
    tank_filling_before = await plc.get_object_value("DQ0")
    print(f"Tank filling before discharging: {tank_filling_before}")
    assert tank_filling_before == False  # Tank is not filling initially

    # Simulate discharging (close the outlet valve)
    await plc.set_object_value("DQ1", False)  # Outlet valve closed
    await asyncio.sleep(1)  # Waiting for reactions

    tank_filling_after = await plc.get_object_value("DQ0")
    alarm_status = await plc.get_alarm_status("A1")

    print(f"Tank filling after discharging: {tank_filling_after}")
    print(f"Alarm A1 status: {alarm_status}")

    # Set the tank level too low condition
    await plc.set_object_value("DI5", True)  # Low tank level sensor active
    await asyncio.sleep(1)  # Waiting for reactions

    tank_filling_after_low_level = await plc.get_object_value("DQ0")
    alarm_status_low_level = await plc.get_alarm_status("A1")

    print(f"Tank filling after low tank level condition: {tank_filling_after_low_level}")
    print(f"Alarm A1 status after low tank level condition: {alarm_status_low_level}")

    assert tank_filling_after == False  # Tank continues to not fill
    assert alarm_status == True  # Alarm A1 is triggered
    assert tank_filling_after_low_level == False  # Tank continues to not fill after low tank level condition
    assert alarm_status_low_level == True  # Alarm A1 is triggered after low tank level condition
