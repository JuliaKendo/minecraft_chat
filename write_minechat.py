import asyncio
import aioconsole
import configargparse
import json
import logging
import re
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
    return re.escape(from_user.strip()).replace(r'\ ', ' ')


async def handle_messages(writer):
    while True:
        message = await get_text_from_cli('> ')
        await submit_message(writer, message)


def get_args_parser():
    parser = configargparse.ArgParser()
    parser.add_argument('--host', required=False, help='chat host', env_var='HOST')
    parser.add_argument('--port', required=False, help='port', env_var='WRITING_PORT')
    parser.add_argument('--hash', required=False, help='account_hash', env_var='ACCOUNT_HASH')
    parser.add_argument('--user', type=str, default='', help='user name')
    parser.add_argument('--message', type=str, default='', help='message to send to chat')
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
            if args.message:
                await submit_message(writer, args.message)
                break
            else:
                await handle_messages(writer)
        except AssertionError:
            new_user = args.user if args.user else await get_text_from_cli(
                'Неизвестный токен. Проверьте его или введите Имя для регистрации > '
            )
            account_hash = await register(reader, writer, new_user)
            continue
        except asyncio.CancelledError:
            break
        finally:
            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
