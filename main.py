import asyncio
import aiofiles
from datetime import datetime


async def add_message_to_file(message):
    async with aiofiles.open('chat_history.txt', 'a') as file_handler:
        await file_handler.write(f'[{datetime.now().strftime("%d-%m-%Y %H:%M")}] {message}')


async def read_messages_from_chat(host, port):
    reader, _ = await asyncio.open_connection(host, port)
    await add_message_to_file('Установлено соединение')
    while True:
        chat_message = await reader.readline()
        if not chat_message:
            break
        decoded_chat_message = chat_message.decode()
        await add_message_to_file(decoded_chat_message)
        print(decoded_chat_message)


if __name__ == "__main__":
    asyncio.run(read_messages_from_chat('minechat.dvmn.org', 5000))
