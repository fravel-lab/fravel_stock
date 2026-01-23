
import asyncio
import time
import telegram
import sys



async def send_message(message):
    token = "7468273764:AAGLOPP9mHSTlGYbkJ2Z1rYTvSyO_PlcUaQ"
    bot = telegram.Bot(token=token)
    response = await bot.send_message(chat_id="1237532491", text=message)
    print(response)


if __name__ == "__main__":
    asyncio.run(send_message("Hello, Telegram!"))