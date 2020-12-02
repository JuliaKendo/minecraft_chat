import os
import asyncio
import aiofiles
import logging
import configargparse
from dotenv import load_dotenv
from datetime import datetime


async def add_message_to_file(message, path_to_history):
    async with aiofiles.open(os.path.join(path_to_history, 'chat_history.txt'), 'a') as file_handler:
        await file_handler.write(f'[{datetime.now().strftime("%d-%m-%Y %H:%M")}] {message}')


async def read_messages_from_chat(host, port, path_to_history):
    reader, _ = await asyncio.open_connection(host, port)
    await add_message_to_file('Установлено соединение', path_to_history)
    while True:
        chat_message = await reader.readline()
        if not chat_message:
            break
        decoded_chat_message = chat_message.decode()
        await add_message_to_file(decoded_chat_message, path_to_history)
        print(decoded_chat_message)


def get_args_parser():
    parser = configargparse.ArgParser()
    parser.add_argument('--host', required=False, help='chat host', env_var='HOST')
    parser.add_argument('--port', required=False, help='port', env_var='LISTENING_PORT')
    parser.add_argument('--history', required=False, help='path to file with the history', env_var='PATH_TO_HISTORY')
    return parser


def main():
    load_dotenv()
    args = get_args_parser().parse_args()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(read_messages_from_chat(args.host, int(args.port), args.history))


if __name__ == "__main__":
    main()
