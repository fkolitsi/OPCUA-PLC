from asyncua import Server, ua
import asyncio

class PLCSimulator:
    def __init__(self):
        self.digital_inputs = {"DI0": False, "DI4": False, "DI8": False}  # Add more digital inputs as needed
        self.analog_inputs = {"AI0": 0.0}  # Add more analog inputs as needed
        self.digital_outputs = {"DQ0": False}  # Add more digital outputs as needed
        self.alarms = {"A0": {"Active": False, "UnAck": False, "Status": False}}  # Add more alarms as needed
        
        self.cycle_time = 0.2

    async def update_inputs(self):
        for name in self.digital_inputs.keys():
            myvar = await self.myobj.get_child(f"{self.idx}:{name}")
            value = await myvar.read_value()
            self.digital_inputs.update({name: value})
        for name in self.analog_inputs.keys():
            # Implement reading analog inputs from the server
            pass

    async def write_outputs(self):
        for name, value in self.digital_outputs.items():
            myvar = await self.myobj.get_child(f"{self.idx}:{name}")
            await myvar.write_value(value)
        for name, value in self.analog_inputs.items():
            # Implement writing analog outputs to the server
            pass

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
            self.alarms[key].update({"UnAck": False})
            self.alarms[key].update({"Status": False})

    async def execute_control_logic(self):
        # Implement your control logic here
        try:
            while True:
                await self.update_inputs()
                
                # Implement your control logic, alarms, GRAFCET logic, output logic, etc.
                # ...

                await self.set_alarms()
                await self.write_outputs()
                await asyncio.sleep(self.cycle_time)
        finally:
            await self.stop()
            print("Stopping server")

    async def set_opcua_server(self):
        self.server = Server()
        await self.server.init()
        self.server.set_endpoint("opc.tcp://localhost:7000/freeopcua/server/")

        uri = "http://examples.freeopcua.github.io"
        self.idx = await self.server.register_namespace(uri)
        objects = self.server.get_objects_node()
        self.myobj = await objects.add_object(self.idx, "myPLC")

        # Populate your address space
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

        await self.server.start()
        print("Server started")

    async def stop(self):
        await self.server.stop()

    async def main(self):
        await self.set_opcua_server()
        await self.execute_control_logic()

if __name__ == "__main__":
    plc = PLCSimulator()
    try:
        asyncio.run(plc.main())
    except KeyboardInterrupt:
        print("PLC stopped")
