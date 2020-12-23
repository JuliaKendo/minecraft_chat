import time
import asyncio
import aiofiles
import functools
import contextlib
import configargparse
from dotenv import load_dotenv
from datetime import datetime
from requests import ConnectionError


@contextlib.asynccontextmanager
async def open_socket(host, port):
    writer = None
    try:
        reader, writer = await asyncio.open_connection(host, port)
        yield reader
    finally:
        writer.close() if writer else None


async def reconnect_endlessly(async_function):
    failed_attempts_to_open_socket = 0
    while True:
        if failed_attempts_to_open_socket > 3:
            time.sleep(60)  # полностью блокируем работу скрипта в ожидании восстановления соединения
        try:
            await async_function()
        except ConnectionError:
            failed_attempts_to_open_socket += 1
            continue


async def save_message_to_file(message, path_to_history):
    async with aiofiles.open(path_to_history, 'a') as file_handler:
        formatted_date = datetime.now().strftime("%d-%m-%Y %H:%M")
        await file_handler.write(f'[{formatted_date}] {message}')


async def get_and_handle_messages(reader, path_to_history):
    while True:
        chat_message = await reader.readline()
        if not chat_message:
            continue
        decoded_chat_message = chat_message.decode()
        await save_message_to_file(decoded_chat_message, path_to_history)
        print(decoded_chat_message.strip('\n'))


async def read_messages_from_chat(host, port, path_to_history): 
    async with open_socket(host, port) as reader:
        await save_message_to_file('Установлено соединение', path_to_history)
        await get_and_handle_messages(reader, path_to_history)


def get_args_parser():
    parser = configargparse.ArgParser()
    parser.add_argument('--host', required=False, default='minechat.dvmn.org', help='chat host', env_var='HOST')
    parser.add_argument('--port', required=False, default=5000, help='port', env_var='LISTENING_PORT')
    parser.add_argument('--history', required=False, default='chat_history.txt', help='path to file with history')
    return parser


def main():
    load_dotenv()
    args = get_args_parser().parse_args()
    read_function = functools.partial(read_messages_from_chat, args.host, int(args.port), args.history)
    asyncio.run(reconnect_endlessly(read_function))


if __name__ == "__main__":
    main()
