import asyncio
import aioconsole
import json
import logging
import configargparse
from dotenv import load_dotenv


async def authorise(reader, writer, account_hash):
    await reader.readline()
    writer.write(f'{account_hash}\n'.encode())
    await writer.drain()
    chat_message = await reader.readline()
    decoded_chat_message = chat_message.decode()
    logging.debug(decoded_chat_message.strip('\n'))
    assert json.loads(decoded_chat_message) is not None
    chat_message = await reader.readline()
    decoded_chat_message = chat_message.decode()
    logging.debug(decoded_chat_message.strip('\n'))


async def register(reader, writer, new_user):
    pass


async def submit_message(writer, message):
    writer.write(f'{message}\n\n'.encode())
    await writer.drain()
    logging.debug(f'sent message: {message}')


async def get_text_from_cli(prompt):
    from_user = await aioconsole.ainput(prompt)
    return from_user.strip()


async def handle_messages(writer):
    while True:
        message = await get_text_from_cli('> ')
        await submit_message(writer, message)


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
    account_hash = args.hash
    while True:
        reader, writer = await asyncio.open_connection(args.host, int(args.port))
        try:
            await authorise(reader, writer, account_hash)
            await handle_messages(writer)
        except AssertionError:
            new_user = await get_text_from_cli(
                'Неизвестный токен. Проверьте его или введите Имя для регистрации > '
            )
            continue
        except asyncio.CancelledError:
            break
        finally:
            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
