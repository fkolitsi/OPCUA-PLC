import logging
import asyncio
# import concurrent.futures
from asyncua import Server, ua

# from plc_client import PLCClient  # Import the PLCClient class

class PLCSimulator:
    def __init__(self):
        # Configure logging
        logging.basicConfig(filename='plc_simulator.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

        # Digital and alarm registers
        self.digital_inputs = {"DI0": False,  # START BUTTON
                               "DI1": False,  # RUN BUTTON
                               "DI2": False,  # STOP BUTTON
                               "DI3": False,  # EMERGENCY BUTTON
                               "DI4": False,  # RESET BUTTON
                               "DI5": False,  # LOWER LEVEL FLOATER
                               "DI6": False,  # LOW LEVEL FLOATER
                               "DI7": False,  # HIGH LEVEL FLOATER
                               "DI8": False,  # HIGHER LEVEL FLOATER
                               "DI9": False}  # DISCHARGING GATE SENSOR
        
        self.analog_inputs =  {"AI0": False}  # SENSOR TEMPERATURE

        self.digital_outputs = {"DQ0": False,  # INPUT VALVE
                                "DQ1": False,  # OUTPUT VALVE
                                "DQ2": False,  # HEATING SYSTEM VALVE
                                "DQ3": False}  # MOTOR-CONTROLLED DISCHARGING GATE
        
        self.alarms = {"A0": {"Active": False, "UnAck": False, "Status": False},  # Tank high level
                       "A1": {"Active": False, "UnAck": False, "Status": False},  # Tank low level
                       "A2": {"Active": False, "UnAck": False, "Status": False},  # High temp >80
                       "A3": {"Active": False, "UnAck": False, "Status": False},  # Low temp <10
                       "A4": {"Active": False, "UnAck": False, "Status": False},  # Discharging door open
                       "A5": {"Active": False, "UnAck": False, "Status": False}}  # Emergency activated

        self.temperature_high_limit = 80
        self.temperature_low_limit = 10
        self.heating_setpoint = 45 
        
        # Time interval for cyclic execution (in seconds)
        self.cycle_time = 0.2
        # self.plc_client = PLCClient("opc.tcp://localhost:7000/freeopcua/server/", 10)  # Adjust the timeout as needed
        

    async def update_inputs(self):
        #Digital input readings from the OPC UA server
        for name in self.digital_inputs.keys():
            myvar = await self.myobj.get_child(f"{self.idx}:{name}")
            value = await myvar.read_value()
            self.digital_inputs.update({name: value})

        #Analog input readings from the server
        for name in self.analog_inputs.keys():
            myvar = await self.myobj.get_child(f"{self.idx}:{name}")
            value = await myvar.read_value()  # Use read_value for analog inputs
            self.analog_inputs.update({name: value})

    async def write_outputs(self):
        #Output values into the OPC UA server
        for name, value in self.digital_outputs.items():
            myvar = await self.myobj.get_child(f"{self.idx}:{name}")
            await myvar.write_value(value)

    #Set Alarms State on OPC UA Server
    async def set_alarms(self):
        for key, values in self.alarms.items():
            myalarm = await self.myobj.get_child(f"{self.idx}:{key}")
            if values["Active"]:
                values["UnAck"] = True
                values["Status"] = True
            for newkey, value in values.items():
                myvar = await myalarm.get_child(f"{self.idx}:{newkey}")
                await myvar.write_value(value)

    async def reset_alarms(self):
        for key in self.alarms.keys():
            self.alarms[key].update({"Active": False})
            self.alarms[key].update({"UnAck": False})
            self.alarms[key].update({"Status": False})

    async def grafcet_logic(self):

        if not any(alarm["Active"] for alarm in self.alarms.values()) or self.digital_inputs["DI2"]:
            # Normal operation
        # STARTING
            if self.digital_inputs["DI0"]: #START button pressed
                if self.digital_inputs["DI9"]:
                    # Close the discharging door
                    self.digital_outputs["DQ3"] = False  # Close motor-controlled discharging door

                # Initiate prefilling until DI6 sensor is activated
                while not self.digital_inputs["DI6"]:
                    self.digital_outputs["DQ0"] = True  # Open In Valve
                    # Updating inputs from server
                    await self.update_inputs()

                # Stop prefilling once tank level is reached
                self.digital_outputs["DQ0"] = False  # Close In Valve

        # RUNNING
            if self.digital_inputs["DI1"]:
                # Tank filling process
                self.digital_outputs["DQ0"] = True  # Open In Valve

                # Wait for high level to be reached
                while not self.digital_inputs["DI7"]:
                    # Updating inputs from server
                    await self.update_inputs()

                # Stop tank filling once high level is reached
                self.digital_outputs["DQ0"] = False  # Close In Valve

                # Fluid heating process directly after reaching high level
                self.digital_outputs["DQ2"] = True  # Start Heating System

        # HEATING
            heating_setpoint = self.heating_setpoint  # Get the current setpoint

            while self.analog_inputs["AI0"] < heating_setpoint:
            # Updating inputs from server
                await self.update_inputs()

            # Stop heating once setpoint is reached
            self.digital_outputs["DQ2"] = False  # Stop Heating System

        # DISCHARGING
            self.digital_outputs["DQ1"] = True  # Open Out Valve

            # Wait for low level to be reached
            while not self.digital_inputs["DI6"]:
                # Updating inputs from server
                await self.update_inputs()

            # Stop tank discharging once low level is reached
            self.digital_outputs["DQ1"] = False  # Close Out Valve

    async def execute_control_logic(self):
        try:
            while True:
                # Updating inputs from server
                await self.update_inputs()

                # Implement alarm logic
                self.alarms["A0"]["Active"] = self.digital_inputs["DI7"]  # Tank Level Too High
                self.alarms["A1"]["Active"] = self.digital_inputs["DI5"]  # Tank Level Too Low
                self.alarms["A2"]["Active"] = self.analog_inputs["AI0"] > self.temperature_high_limit # Fluid Temperature Too High
                self.alarms["A3"]["Active"] = self.analog_inputs["AI0"] < self.temperature_low_limit  # Fluid Temperature Too Low
                self.alarms["A4"]["Active"] = self.digital_inputs["DI9"]  # Discharging Door Open
                self.alarms["A5"]["Active"] = self.digital_inputs["DI3"]  # Emergency Button Pressed

                # Check for any active alarms
                active_alarms = [alarm for alarm in self.alarms.values() if alarm["Active"]]

                # Press RESET for ack.
                if self.digital_inputs["DI4"]:
                    await self.reset_alarms()

                # Setting alarms on server
                await self.set_alarms()

                # Implement GRAFCET logic
                await self.grafcet_logic()

                # Implement output logic
                for alarm_key, alarm in self.alarms.items():
                    if alarm["Active"]:
                        self.digital_outputs["DQ3"] = True  # Open motor-controlled discharging door

                # Check if lower tank level sensor indicates no more fluid
                if not self.digital_inputs["DI5"]:
                    self.digital_outputs["DQ3"] = False  # Close motor-controlled discharging door

                # Reset the system after acknowledging alarms
                if not any(alarm["Active"] for alarm in self.alarms.values()):
                    self.digital_outputs["DQ3"] = False  # Close motor-controlled discharging door

                # Setting outputs on server
                await self.write_outputs()

                # Sleeping for cycle time
                await asyncio.sleep(self.cycle_time)
        finally:
            await self.stop()
            print("Stopping server")
            
    
    async def set_opcua_server(self):
        self.server = Server()
        await self.server.init() 
        self.server.set_endpoint("opc.tcp://localhost:7000/freeopcua/server/")

        # setup our own namespace, not really necessary but should as spec
        uri = "http://examples.freeopcua.github.io"
        self.idx = await self.server.register_namespace(uri)

        # get Objects node, this is where we should put our nodes
        objects = self.server.get_objects_node()

        # Populating our address space
        self.myobj = await objects.add_object(self.idx, "myPLC")

        for key, value in self.digital_inputs.items():
            myvar = await self.myobj.add_variable(self.idx, key, value)
            await myvar.set_writable()
        for key, value in self.analog_inputs.items():
            myvar = await self.myobj.add_variable(self.idx, key, value)
            await myvar.set_writable()
        for key, value in self.digital_outputs.items():
            myvar = await self.myobj.add_variable(self.idx, key, value)
            await myvar.set_writable()
        for key, values in self.alarms.items():
            myalarm = await self.myobj.add_object(self.idx, key)
            for newkey, value in values.items():
                myvar = await myalarm.add_variable(self.idx, newkey, value)
                await myvar.set_writable()
        # starting!
        await self.server.start()
        print("Server started")

    async def stop(self):
        await self.server.stop()
        
    
    async def main(self):
        # Set OPC UA server
        await self.set_opcua_server()

        # Execute cycle program
        await self.execute_control_logic()

if __name__ == "__main__":
    plc = PLCSimulator()
    try:
        asyncio.run(plc.main())
    except KeyboardInterrupt:
        print("PLC stopped")