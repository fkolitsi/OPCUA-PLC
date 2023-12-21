import logging
import asyncio
import concurrent.futures
from asyncua import Server, ua

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://localhost:7000/freeopcua/server/")
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)
    await server.start()
    print("Server started")

    # Watchdog task
    async def watchdog():
        while True:
            await asyncio.sleep(5)  # Adjust the interval as needed
            try:
                if not server.is_server_running():
                    logging.warning("Server is not running. Attempting to restart.")
                    await server.start()
                    logging.info("Server restarted successfully.")
            except Exception as e:
                logging.error(f"Error checking server status: {e}")

    # Start the watchdog task
    asyncio.create_task(watchdog())

    try:
        while True:
            await asyncio.sleep(1)
    except (concurrent.futures.TimeoutError, ConnectionError, ua.UaError):
        logging.warning("Reconnecting in 1 second")
        await asyncio.sleep(1)
    finally:
        await server.stop()
        print("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
