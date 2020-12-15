import asyncio
import json
import logging
import aioconsole
import contextlib
import configargparse
from dotenv import load_dotenv


@contextlib.asynccontextmanager
async def open_socket(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield (reader, writer)
    except asyncio.CancelledError:
        raise
    finally:
        writer.close()
        await writer.wait_closed()


async def authorise(reader, writer, account_hash):
    await reader.readline()
    writer.write(f'{account_hash}\n'.encode())
    await writer.drain()
    chat_message = await reader.readline()
    decoded_chat_message = chat_message.decode()
    logging.debug(decoded_chat_message.strip('\n'))
    if json.loads(decoded_chat_message):
        chat_message = await reader.readline()
        decoded_chat_message = chat_message.decode()
        logging.debug(decoded_chat_message.strip('\n'))
        return True


async def register(reader, writer, new_user):
    logging.debug('new user registration')
    await reader.readline()
    writer.write(f'{new_user}\n'.encode())
    await writer.drain()
    chat_message = await reader.readline()
    decoded_chat_message = chat_message.decode()
    logging.debug(f'added new user {new_user} to chat')
    return json.loads(decoded_chat_message)['account_hash']


async def submit_message(writer, message):
    writer.write(f'{message}\n\n'.encode())
    await writer.drain()
    logging.debug(f'sent message: {message}')


async def get_text_from_cli(prompt):
    from_user = await aioconsole.ainput(prompt)
    return from_user.replace(r'\n', ' ')


async def handle_messages(writer):
    while True:
        message = await get_text_from_cli('> ')
        await submit_message(writer, message)


async def auth_and_send_messages_to_chart(args):
    account_hash = args.hash
    while True:
        async with open_socket(args.host, int(args.port)) as socket_connection:
            reader, writer = socket_connection
            if await authorise(reader, writer, account_hash):
                await handle_messages(writer)
            else:
                new_user = args.user.replace(r'\n', ' ') if args.user else await get_text_from_cli(
                    'Неизвестный токен. Проверьте его или введите Имя для регистрации > '
                )
                account_hash = await register(reader, writer, new_user)


def get_args_parser():
    parser = configargparse.ArgParser()
    parser.add_argument('--host', required=False, default='minechat.dvmn.org', help='chat host', env_var='HOST')
    parser.add_argument('--port', required=False, default=5050, help='port', env_var='WRITING_PORT')
    parser.add_argument('--hash', required=False, help='account_hash', env_var='ACCOUNT_HASH')
    parser.add_argument('--user', type=str, default='', help='user name')
    return parser


def main():
    load_dotenv()
    args = get_args_parser().parse_args()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(auth_and_send_messages_to_chart(args))


if __name__ == "__main__":
    main()
