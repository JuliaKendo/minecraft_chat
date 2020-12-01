import asyncio


async def read_messages_from_chat(host, port):
    reader, _ = await asyncio.open_connection(host, port)
    while True:
        line = await reader.readline()
        if not line:
            return
        print(line.decode())


if __name__ == "__main__":
    asyncio.run(read_messages_from_chat('minechat.dvmn.org', 5000))
