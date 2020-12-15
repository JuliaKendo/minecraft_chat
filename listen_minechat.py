import asyncio
import aiofiles
import configargparse
from dotenv import load_dotenv
from datetime import datetime


async def save_message_to_file(message, path_to_history):
    async with aiofiles.open(path_to_history, 'a') as file_handler:
        await file_handler.write(f'[{datetime.now().strftime("%d-%m-%Y %H:%M")}] {message}')


async def read_messages_from_chat(host, port, path_to_history):
    reader, _ = await asyncio.open_connection(host, port)
    await save_message_to_file('Установлено соединение', path_to_history)
    while True:
        chat_message = await reader.readline()
        if not chat_message:
            continue
        decoded_chat_message = chat_message.decode()
        await save_message_to_file(decoded_chat_message, path_to_history)
        print(decoded_chat_message.strip('\n'))


def get_args_parser():
    parser = configargparse.ArgParser()
    parser.add_argument('--host', required=False, default='minechat.dvmn.org', help='chat host', env_var='HOST')
    parser.add_argument('--port', required=False, default=5000, help='port', env_var='LISTENING_PORT')
    parser.add_argument('--history', required=False, default='chat_history.txt', help='path to file with history')
    return parser


def main():
    load_dotenv()
    args = get_args_parser().parse_args()
    asyncio.run(read_messages_from_chat(args.host, int(args.port), args.history))


if __name__ == "__main__":
    main()
