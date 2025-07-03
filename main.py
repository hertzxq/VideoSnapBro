import aiogram, logging, asyncio
from config import BOT_TOKEN


from aiogram import Bot, Dispatcher, types
from handlers import router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router=router)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())