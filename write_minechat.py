import asyncio


async def read_message(reader, tics=1):
    for _ in range(tics):
        data = await reader.readline()
        print(data.decode())


async def authorise(reader, writer, account_hash):
    await read_message(reader)
    writer.write(f'{account_hash}\n'.encode())
    await writer.drain()
    await read_message(reader, 2)


async def register():
    pass


async def submit_message(writer):
    writer.write('Test\n\n'.encode())
    await writer.drain()


async def main():
    reader, writer = await asyncio.open_connection('minechat.dvmn.org', 5050)
    await authorise(reader, writer, '7d6757be-3425-11eb-8c47-0242ac110002')
    await submit_message(writer)


if __name__ == "__main__":
    asyncio.run(main())
