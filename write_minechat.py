import asyncio
import logging
import configargparse
from dotenv import load_dotenv


async def read_message(reader, tics=1):
    for _ in range(tics):
        data = await reader.readline()
        logging.debug(f'get message: {data.decode()}')


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
    logging.debug('send message: Test\n\n')


def get_args_parser():
    parser = configargparse.ArgParser()
    parser.add_argument('--host', required=False, help='chat host', env_var='HOST')
    parser.add_argument('--port', required=False, help='port', env_var='WRITING_PORT')
    parser.add_argument('--hash', required=False, help='account_hash', env_var='ACCOUNT_HASH')
    return parser


async def main():

    load_dotenv()
    args = get_args_parser().parse_args()
    logging.basicConfig(level=logging.DEBUG)

    reader, writer = await asyncio.open_connection(args.host, int(args.port))
    await authorise(reader, writer, args.hash)
    await submit_message(writer)


if __name__ == "__main__":
    asyncio.run(main())
