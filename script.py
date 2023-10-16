import asyncio
import random

async def trap_attacker(_, writer):
    """Exploit the SSH Protocol Version Exchange (https://datatracker.ietf.org/doc/html/rfc4253#section-4.2)
       by sending lines of random data every 10 seconds in a loop forever or until the attacker gives up.
    
       Before the authorization part within SSH, a Client & Server MUST exhange a version string, but
       "The server MAY send other lines of data before sending the version string". This is where we
       send nonstop lines of data very slowly back to the client and never sending the version string.
       The client therefore just hangs forever trying to connect to us via SSH."""
    try:
        while True:
            await asyncio.sleep(10)
            writer.write(b'%x\r\n' % random.randint(0, 2**16))
            await writer.drain()
    except ConnectionResetError:
        pass

async def main():
    # Start a socket server with the connection callback set to our trap_attacker function,
    # exposing it to the internet on port 22, and keep it running foreva
    server = await asyncio.start_server(trap_attacker, '0.0.0.0', 22)
    async with server:
        await server.serve_forever()

# Run the main function
asyncio.run(main())
