
import asyncio
import pytest
import pytest_asyncio


from src.plc_client import PLCClient


SERVER_URL = "opc.tcp://localhost:7000/freeopcua/server/"

CLIENT_TIMEOUT = 10  # seconds

@pytest_asyncio.fixture()
async def plc() -> PLCClient:
    """ Instance of the OPC UA client to communicate with the simulator """
    plc = PLCClient(url=SERVER_URL, timeout=CLIENT_TIMEOUT)
    await plc.init()
    yield plc
    await plc.disconnect()


# Press START button and check that tank is filling
@pytest.mark.asyncio
async def test_start_prefilling(plc: PLCClient):
    # Check initial state
    tank_filling_initial = await plc.get_object_value("DQ0")
    tank_discharging_initial = await plc.get_object_value("DQ1")
    liquid_heating_initial = await plc.get_object_value("DQ2")

    print("Initial state:")
    print(f"Tank is filling: {tank_filling_initial}")
    print(f"Tank is discharging: {tank_discharging_initial}")
    print(f"Liquid is heating: {liquid_heating_initial}")

    assert tank_filling_initial == False  # Tank is not filling
    assert tank_discharging_initial == False  # Tank is not discharging
    assert liquid_heating_initial == False  # Liquid is not heating

    # Press START button
    await plc.set_object_pulse("DI0")
    await asyncio.sleep(1)  # Waiting for transition into the next step

    # Check state after pressing START button
    tank_filling_after_start = await plc.get_object_value("DQ0")
    tank_discharging_after_start = await plc.get_object_value("DQ1")
    liquid_heating_after_start = await plc.get_object_value("DQ2")

    print("State after pressing START button:")
    print(f"Tank is filling: {tank_filling_after_start}")
    print(f"Tank is discharging: {tank_discharging_after_start}")
    print(f"Liquid is heating: {liquid_heating_after_start}")

    assert tank_filling_after_start == True  # Tank is filling
    assert tank_discharging_after_start == False  # Tank is not discharging
    assert liquid_heating_after_start == False  # Liquid is not heating





# Press START button and check that tank is filling
# @pytest.mark.asyncio
# async def test_start_prefilling(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == False # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False # Liquid is not heating

#     await plc.set_object_pulse("DI0") # Press START button
#     await asyncio.sleep(1) # Waiting for transition into next step
    
#     # assert await plc.get_object_value("DQ0") == True # Tank is filling
#     # assert await plc.get_object_value("DQ1") == False # Tank is not discharging
#     # assert await plc.get_object_value("DQ2") == False # Liquid is not heating
#     tank_filling = await plc.get_object_value("DQ0")
#     tank_discharging = await plc.get_object_value("DQ1")
#     liquid_heating = await plc.get_object_value("DQ2")

#     print(f"Tank is filling: {tank_filling}")
#     print(f"Tank is discharging: {tank_discharging}")
#     print(f"Liquid is heating: {liquid_heating}")

#     assert tank_filling == True  # Tank is filling
#     assert tank_discharging == False  # Tank is not discharging
#     assert liquid_heating == False  # Liquid is not heating


# # Test low level has been reached
# @pytest.mark.asyncio
# async def test_low_level_reached(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == True  # Tank is filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating

#     await plc.set_object_value("DI6", True)  # Simulate low level reached
#     await asyncio.sleep(1)  # Waiting for transition into the next step

#     assert await plc.get_object_value("DQ0") == False  # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating


# # Test RUN button pressed
# @pytest.mark.asyncio
# async def test_run_button_pressed(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == False  # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating

#     await plc.set_object_value("DI1", True)  # Press RUN button
#     await asyncio.sleep(1)  # Waiting for transition into the next step

#     assert await plc.get_object_value("DQ0") == True  # Tank is filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating


# # Test high level has been reached
# @pytest.mark.asyncio
# async def test_high_level_reached(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == True  # Tank is filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating

#     await plc.set_object_value("DI7", True)  # Simulate high level reached
#     await asyncio.sleep(1)  # Waiting for transition into the next step

#     assert await plc.get_object_value("DQ0") == False  # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating

# Test setpoint has been reached
# @pytest.mark.asyncio
# async def test_temperature_setpoint_reached(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == False  # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == True  # Liquid is heating

#     await plc.set_object_value("AI0", plc.self.temperature_high_limit)  # Simulate temperature reaching setpoint
#     await asyncio.sleep(1)  # Waiting for transition
    
#     assert await plc.get_object_value("DQ0") == False  # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating

# # Test low level discharging has been reached
# @pytest.mark.asyncio
# async def test_low_level_disc_reached(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == False  # Tank is not filling
#     assert await plc.get_object_value("DQ1") == True  # Tank is discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating

#     await plc.set_object_value("DI6", True)  # Simulate low level reached
#     await asyncio.sleep(1)  # Waiting for transition
    
#     assert await plc.get_object_value("DQ0") == False  # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False  # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False  # Liquid is not heating

# # Stop button
# @pytest.mark.asyncio
# async def test_stop_button(plc: PLCClient):
#     assert await plc.get_object_value("DQ0") == False # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False # Liquid is not heating
    
#     await plc.set_object_pulse("DI2") # Press STOP button
#     await asyncio.sleep(1) # Waiting for transition into next step
    
#     assert await plc.get_object_value("DQ0") == False # Tank is not filling
#     assert await plc.get_object_value("DQ1") == False # Tank is not discharging
#     assert await plc.get_object_value("DQ2") == False # Liquid is not heating

# # Add more test cases as needed
